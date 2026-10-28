"""Penyimpanan dan pemuatan model profil (IDF + profil bidang) pada tabel ProfileVersion."""

import pandas as pd
from sqlmodel import Session, select

from app.ml.pipeline import HasilVersi
from app.ml.preprocess import NAMA_KELOMPOK
from app.models.database import ProfileVersion


def serialisasi(hasil: HasilVersi) -> tuple[dict, dict]:
    """(ringkasan, model) dalam bentuk JSON-aman."""
    model = {
        "kolom": list(hasil.idf.index),
        "idf": [float(v) for v in hasil.idf],
        "bidang": list(hasil.P.index),
        "n_developer": [int(hasil.per_bidang.loc[b, "semua"]) for b in hasil.P.index],
        "P": [[float(v) for v in baris] for baris in hasil.P.to_numpy()],
    }
    return hasil.ringkasan(), model


def muat_model(version: ProfileVersion):
    """(w, P, norma_P) dari versi profil."""
    m = version.model
    w = pd.Series(m["idf"], index=m["kolom"])
    P = pd.DataFrame(m["P"], index=m["bidang"], columns=m["kolom"])
    return w, P, (P**2).sum(axis=1) ** 0.5


def versi_aktif(db: Session) -> ProfileVersion | None:
    return db.exec(select(ProfileVersion).where(ProfileVersion.is_active)).first()


def daftar_teknologi(version: ProfileVersion) -> dict[str, list[dict]]:
    """Teknologi per kelompok untuk ditampilkan ke Mahasiswa."""
    hasil = {nama: [] for nama in NAMA_KELOMPOK.values()}
    for kode in version.model["kolom"]:
        kelompok, nama = kode.split(":", 1)
        hasil[NAMA_KELOMPOK[kelompok]].append({"kode": kode, "nama": nama})
    return hasil
