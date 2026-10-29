import logging
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, UploadFile, status
from pydantic import BaseModel
from sqlmodel import Session, select, update

from app.ml.pipeline import bangun_versi_profil
from app.ml.preprocess import KolomTidakLengkap, muat_dataset
from app.models.database import ProfileVersion, Recommendation, User
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
        if version is None:  # versi dihapus sebelum selesai; cukup bersihkan berkas sementara
            Path(path).unlink(missing_ok=True)
            return
        try:
            hasil = bangun_versi_profil(muat_dataset(path))
            version.ringkasan, version.model = serialisasi(hasil)
            version.pratinjau = hasil.pratinjau
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


@admin_router.post("/profile-versions", status_code=status.HTTP_202_ACCEPTED)
def unggah_dataset(file: UploadFile, tasks: BackgroundTasks, response: Response, db: DB, _: Admin):
    """Unggah dataset survei (.csv atau .xlsx) untuk membentuk versi profil baru. Pemrosesan berjalan di
    latar belakang (±45 detik); pantau lewat `Location` (GET /admin/profile-versions/{id}) sampai `ready`."""
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
    response.headers["Location"] = f"/admin/profile-versions/{version.id}"
    return {"id": version.id, "status": version.status}


def _ringkas(v: ProfileVersion) -> dict:
    return {
        "id": v.id,
        "filename": v.filename,
        "status": v.status,
        "is_active": v.is_active,
        "created_at": v.created_at,
        "n_developer": v.ringkasan["n_developer"] if v.ringkasan else None,
        "metrik": v.ringkasan["metrik"] if v.ringkasan else None,
    }


@admin_router.get("/profile-versions")
def daftar_versi(db: DB, _: Admin):
    versi = db.exec(select(ProfileVersion).order_by(ProfileVersion.id.desc())).all()
    return [_ringkas(v) for v in versi]


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
        "pratinjau": v.pratinjau,
    }


class UbahVersi(BaseModel):
    is_active: bool


@admin_router.patch("/profile-versions/{version_id}")
def ubah_versi(version_id: int, body: UbahVersi, db: DB, _: Admin):
    """Aktifkan atau nonaktifkan versi. Mengaktifkan satu versi otomatis menonaktifkan yang lain."""
    v = db.get(ProfileVersion, version_id)
    if not v:
        raise HTTPException(404, "Versi tidak ditemukan")
    if body.is_active:
        if v.status != "ready":
            raise HTTPException(
                409, f"Versi berstatus '{v.status}', hanya 'ready' yang bisa diaktifkan"
            )
        for lama in db.exec(
            select(ProfileVersion).where(ProfileVersion.is_active, ProfileVersion.id != v.id)
        ).all():
            lama.is_active = False
            db.add(lama)
    v.is_active = body.is_active
    db.add(v)
    db.commit()
    db.refresh(v)
    return _ringkas(v)


@admin_router.delete("/profile-versions/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_versi(version_id: int, db: DB, _: Admin):
    """Hapus permanen satu versi. Riwayat rekomendasi yang memakainya tetap utuh (version_id jadi NULL)."""
    v = db.get(ProfileVersion, version_id)
    if not v:
        raise HTTPException(404, "Versi tidak ditemukan")
    if v.is_active:
        raise HTTPException(
            409, "Versi aktif tidak bisa dihapus; nonaktifkan atau aktifkan versi lain dulu"
        )
    if v.status == "processing":
        raise HTTPException(409, "Versi masih diproses; tunggu sampai selesai atau gagal")
    db.exec(update(Recommendation).where(Recommendation.version_id == v.id).values(version_id=None))
    db.delete(v)
    db.commit()


@admin_router.get("/profiles")
def profil_aktif(db: DB, _: Admin, top: int = 10):
    """Profil teknologi tiap bidang pada versi aktif: `top` teknologi dengan proporsi pemakai terbesar,
    beserta bobot IDF-nya."""
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
                    {"kode": k, "proporsi": round(float(p), 4), "bobot_idf": round(float(w[k]), 4)}
                    for k, p in proporsi.loc[b].sort_values(ascending=False).head(top).items()
                ],
            }
            for b, n in zip(P.index, v.model["n_developer"], strict=True)
        ],
    }
