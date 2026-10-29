from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.ml.params import Params
from app.ml.recommend import periksa_input, rekomendasi
from app.models.database import Recommendation, User
from app.models.engine import db_session
from app.modules.auth.service import get_current_user
from app.modules.profile.service import daftar_teknologi, muat_model, versi_aktif

recommendation_router = APIRouter(tags=["Rekomendasi"])
DB = Annotated[Session, Depends(db_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


class PermintaanRekomendasi(BaseModel):
    teknologi: list[str]  # kode dari GET /technologies, mis. "lang:Python"


def _versi_aktif_atau_503(db: Session):
    v = versi_aktif(db)
    if not v:
        raise HTTPException(
            503, "Belum ada versi profil aktif; Admin perlu mengunggah dan mengaktifkan dataset"
        )
    return v


@recommendation_router.get("/technologies")
def daftar(db: DB, _: CurrentUser):
    """Teknologi dari empat kelompok yang bisa dipilih Mahasiswa."""
    return daftar_teknologi(_versi_aktif_atau_503(db))


@recommendation_router.post("/recommendations", status_code=status.HTTP_201_CREATED)
def buat_rekomendasi(body: PermintaanRekomendasi, db: DB, user: CurrentUser):
    """Tiga bidang teratas beserta skor, dasar perhitungan, dan peringkat seluruh bidang."""
    params = Params()
    v = _versi_aktif_atau_503(db)
    w, P, norma_P = muat_model(v)
    galat = periksa_input(body.teknologi, w.index, params.min_teknologi)
    if galat:
        raise HTTPException(422, galat)
    hasil = rekomendasi(
        body.teknologi, w, P, norma_P, params.top_k, dikecualikan=params.teknologi_dikecualikan_umum
    )
    hasil["version_id"] = v.id
    rec = Recommendation(user_id=user.id, version_id=v.id, hasil=hasil)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return {"id": rec.id, "created_at": rec.created_at, **hasil}


@recommendation_router.get("/recommendations")
def riwayat(db: DB, user: CurrentUser):
    recs = db.exec(
        select(Recommendation)
        .where(Recommendation.user_id == user.id)
        .order_by(Recommendation.id.desc())
    ).all()
    return [
        {
            "id": r.id,
            "created_at": r.created_at,
            "teknologi_dipilih": r.hasil["teknologi_dipilih"],
            "top": [
                {"bidang_karier": p["bidang_karier"], "skor": p["skor"]}
                for p in r.hasil["peringkat"][: Params().top_k]
            ],
        }
        for r in recs
    ]


@recommendation_router.get("/recommendations/{rec_id}")
def detail(rec_id: int, db: DB, user: CurrentUser):
    r = db.get(Recommendation, rec_id)
    if not r or r.user_id != user.id:
        raise HTTPException(404, "Rekomendasi tidak ditemukan")
    return {"id": r.id, "created_at": r.created_at, **r.hasil}


@recommendation_router.delete("/recommendations/{rec_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus(rec_id: int, db: DB, user: CurrentUser):
    """Hapus satu riwayat rekomendasi milik sendiri; milik orang lain dijawab 404."""
    r = db.get(Recommendation, rec_id)
    if not r or r.user_id != user.id:
        raise HTTPException(404, "Rekomendasi tidak ditemukan")
    db.delete(r)
    db.commit()
