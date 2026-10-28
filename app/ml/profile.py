"""Pembobotan IDF dan pembentukan profil bidang karier (Bab III 3.2, langkah A4-A5)."""

import numpy as np
import pandas as pd


def hitung_idf(X: pd.DataFrame) -> pd.Series:
    """IDF terhaluskan, Pers. (3.1), K16: ln((1 + N) / (1 + df)) + 1 (= scikit-learn smooth_idf=True)."""
    N = len(X)
    df = X.sum()
    return np.log((1 + N) / (1 + df)) + 1


def bentuk_profil(
    X: pd.DataFrame, label: pd.Series, w: pd.Series
) -> tuple[pd.DataFrame, pd.Series]:
    """Profil bidang, Pers. (3.2), K17: proporsi pemakaian x bobot IDF (vektor tidak dinormalisasi).

    Baris diurutkan dari bidang dengan developer terbanyak (lalu nama); urutan ini menjadi aturan
    pemecah skor seri.
    """
    jumlah = label.value_counts()
    urutan = jumlah.sort_index().sort_values(ascending=False, kind="stable").index
    proporsi = X.groupby(label).mean().loc[urutan]
    P = proporsi * w
    norma_P = np.sqrt((P**2).sum(axis=1))
    return P, norma_P
