"""Pembentukan satu versi profil dari dataset survei (alur A). Dapat dijalankan sebagai skrip:

uv run python -m app.ml.pipeline data/survey_results_public_2025.xlsx
"""

import json
import sys
from dataclasses import dataclass

import pandas as pd

from app.ml.evaluate import evaluasi_lengkap
from app.ml.params import Params
from app.ml.preprocess import bangun_data_final, daftar_teknologi, muat_dataset
from app.ml.profile import bentuk_profil, hitung_idf


@dataclass
class HasilVersi:
    params: Params
    log: list[dict]
    per_bidang: pd.DataFrame
    teknologi: pd.DataFrame
    idf: pd.Series
    P: pd.DataFrame  # profil bidang (baris urut dari developer terbanyak)
    norma_P: pd.Series
    metrik: dict

    def ringkasan(self) -> dict:
        """Bagian yang dapat disimpan sebagai JSON (tanpa matriks)."""
        return {
            "params": self.params.snapshot(),
            "penyaringan": self.log,
            "per_bidang": self.per_bidang.reset_index().to_dict("records"),
            "n_developer": int(self.per_bidang["semua"].sum()),
            "n_teknologi": len(self.teknologi),
            "metrik": self.metrik,
        }


def bangun_versi_profil(df: pd.DataFrame, params: Params | None = None) -> HasilVersi:
    params = params or Params()
    data = bangun_data_final(df, params)
    idf = hitung_idf(data.X)
    P, norma_P = bentuk_profil(data.X, data.label, idf)
    metrik = evaluasi_lengkap(
        data.X,
        data.label,
        data.awal,
        params.k_fold,
        params.seed,
        params.skenario_teknologi,
        params.top_k,
    )
    return HasilVersi(
        params=params,
        log=data.log,
        per_bidang=data.per_bidang,
        teknologi=daftar_teknologi(data.X),
        idf=idf,
        P=P,
        norma_P=norma_P,
        metrik=metrik,
    )


def main(path: str) -> None:
    params = Params()
    print(
        f"n_min = ceil({params.z}^2 x {params.p}(1-{params.p}) / {params.e}^2) = {params.n_min}\n"
    )
    hasil = bangun_versi_profil(muat_dataset(path), params)
    print(pd.DataFrame(hasil.log)[["tahap", "sisa", "terbuang"]].to_string(index=False), "\n")
    print(hasil.per_bidang.to_string(), "\n")
    print(
        f"{len(hasil.teknologi)} teknologi:",
        hasil.teknologi["kelompok"].value_counts().to_dict(),
        "\n",
    )
    print(json.dumps(hasil.metrik, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/survey_results_public_2025.xlsx")
