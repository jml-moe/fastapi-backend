import logging
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, status
from sqlmodel import Session, select

from app.ml.pipeline import bangun_versi_profil
from app.ml.preprocess import KolomTidakLengkap, muat_dataset
from app.models.database import ProfileVersion, User
from app.models.engine import db_session, engine
from app.modules.auth.service import require_admin
from app.modules.profile.service import muat_model, serialisasi, versi_aktif

logger = logging.getLogger(__name__)

admin_router = APIRouter(prefix="/admin", tags=["Admin"])
Admin = Annotated[User, Depends(require_admin)]
DB = Annotated[Session, Depends(db_session)]


def proses_dataset(version_id: int, path: str):
    """Jalankan alur A di latar belakang; hasil atau pesan galat disimpan pada versi."""
    with Session(engine) as db:
        version = db.get(ProfileVersion, version_id)
        try:
            hasil = bangun_versi_profil(muat_dataset(path))
            version.ringkasan, version.model = serialisasi(hasil)
            version.status = "ready"
        except KolomTidakLengkap as e:
            version.status, version.error = "failed", str(e)
        except Exception as e:
            logger.exception("Pemrosesan dataset gagal")
            version.status, version.error = "failed", f"{type(e).__name__}: {e}"
        finally:
            Path(path).unlink(missing_ok=True)
        db.add(version)
        db.commit()


@admin_router.post("/datasets", status_code=status.HTTP_202_ACCEPTED)
def unggah_dataset(file: UploadFile, tasks: BackgroundTasks, db: DB, _: Admin):
    """Unggah dataset survei (.csv atau .xlsx). Pemrosesan berjalan di latar belakang (±45 detik);
    pantau lewat GET /admin/profile-versions/{id} sampai status `ready`."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in (".csv", ".xlsx"):
        raise HTTPException(422, "Berkas harus .csv atau .xlsx")
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.file.read())
    version = ProfileVersion(filename=file.filename)
    db.add(version)
    db.commit()
    db.refresh(version)
    tasks.add_task(proses_dataset, version.id, tmp.name)
    return {"id": version.id, "status": version.status}


@admin_router.get("/profile-versions")
def daftar_versi(db: DB, _: Admin):
    versi = db.exec(select(ProfileVersion).order_by(ProfileVersion.id.desc())).all()
    return [
        {
            "id": v.id,
            "filename": v.filename,
            "status": v.status,
            "is_active": v.is_active,
            "created_at": v.created_at,
            "n_developer": v.ringkasan["n_developer"] if v.ringkasan else None,
            "metrik": v.ringkasan["metrik"] if v.ringkasan else None,
        }
        for v in versi
    ]


@admin_router.get("/profile-versions/{version_id}")
def detail_versi(version_id: int, db: DB, _: Admin):
    """Penyaringan, jumlah per bidang, parameter beserta alasannya, dan hasil evaluasi."""
    v = db.get(ProfileVersion, version_id)
    if not v:
        raise HTTPException(404, "Versi tidak ditemukan")
    return {
        "id": v.id,
        "filename": v.filename,
        "status": v.status,
        "is_active": v.is_active,
        "error": v.error,
        "ringkasan": v.ringkasan,
    }


@admin_router.post("/profile-versions/{version_id}/activate")
def aktifkan_versi(version_id: int, db: DB, _: Admin):
    v = db.get(ProfileVersion, version_id)
    if not v:
        raise HTTPException(404, "Versi tidak ditemukan")
    if v.status != "ready":
        raise HTTPException(
            409, f"Versi berstatus '{v.status}', hanya 'ready' yang bisa diaktifkan"
        )
    for lama in db.exec(select(ProfileVersion).where(ProfileVersion.is_active)).all():
        lama.is_active = False
        db.add(lama)
    v.is_active = True
    db.add(v)
    db.commit()
    return {"id": v.id, "is_active": True}


@admin_router.get("/profiles")
def profil_aktif(db: DB, _: Admin, top: int = 10):
    """Profil teknologi tiap bidang pada versi aktif: `top` teknologi dengan proporsi pemakai terbesar."""
    v = versi_aktif(db)
    if not v:
        raise HTTPException(404, "Belum ada versi profil yang aktif")
    w, P, _norma = muat_model(v)
    proporsi = P / w
    return {
        "version_id": v.id,
        "bidang": [
            {
                "bidang_karier": b,
                "n_developer": n,
                "teknologi": [
                    {"kode": k, "proporsi": round(float(p), 4)}
                    for k, p in proporsi.loc[b].sort_values(ascending=False).head(top).items()
                ],
            }
            for b, n in zip(P.index, v.model["n_developer"], strict=True)
        ],
    }
