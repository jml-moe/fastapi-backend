"""Pratinjau data untuk Admin: sampel acak baris mentah dan baris setelah diproses.

Berkas unggahan tidak disimpan, jadi pratinjau dibuat sekali saat pemrosesan dan ikut tersimpan bersama
versi profilnya (murni pandas; tanpa FastAPI atau database).
"""

import json

import pandas as pd

from app.ml.preprocess import KOLOM_WAJIB, DataFinal

N_PRATINJAU = 100


def _baris(df: pd.DataFrame) -> list[dict]:
    """Daftar dict yang aman untuk JSON: tipe numpy menjadi tipe Python dan NaN menjadi null."""
    return json.loads(df.to_json(orient="records"))


def buat_pratinjau(df: pd.DataFrame, data: DataFinal, seed: int = 0, n: int = N_PRATINJAU) -> dict:
    """`n` baris acak (seed tetap, bukan `n` baris pertama agar tidak bias oleh urutan berkas)."""
    kolom = [c for c in KOLOM_WAJIB if c in df.columns]
    mentah = df[kolom].sample(min(n, len(df)), random_state=seed)

    pilih = data.X.sample(min(n, len(data.X)), random_state=seed).index
    terpilih = data.X.loc[pilih]
    terproses = pd.DataFrame(
        {
            "ResponseId": data.id_responden.loc[pilih],
            "bidang_karier": data.label.loc[pilih],
            "awal_karier": data.awal.loc[pilih].astype(bool),
            "jumlah_teknologi": terpilih.sum(axis=1).astype(int),
            "teknologi": [list(terpilih.columns[row.astype(bool)]) for row in terpilih.to_numpy()],
        }
    )
    return {
        "mentah": {"total": len(df), "kolom": kolom, "baris": _baris(mentah)},
        "terproses": {"total": len(data.X), "baris": _baris(terproses)},
    }
