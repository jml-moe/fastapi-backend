"""Evaluasi profil dengan stratified k-fold pada developer awal karier (Bab III 3.2, langkah A6)."""

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

from app.ml.profile import bentuk_profil, hitung_idf
from app.ml.recommend import hitung_cosine, urutkan_bidang


def bagi_fold(label: pd.Series, awal: pd.Series, k: int = 5, seed: int = 0) -> pd.Series:
    """Stratified k-fold pada developer awal karier; developer lain diberi fold -1 (selalu data latih)."""
    fold = pd.Series(-1, index=label.index)
    idx = label.index[awal]
    skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=seed)
    for f, (_, uji) in enumerate(skf.split(idx, label[idx])):
        fold[idx[uji]] = f
    return fold


def sisakan_teknologi(X: pd.DataFrame, k: int | None, seed: int = 0) -> pd.DataFrame:
    """Sisakan k teknologi acak per developer; developer dengan <= k teknologi tetap utuh."""
    if k is None:
        return X
    rng = np.random.default_rng(seed)
    acak = rng.random(X.shape) * X.to_numpy()  # 0 untuk teknologi yang tidak dipakai
    batas = -np.sort(-acak, axis=1)[:, k - 1 : k]  # nilai acak terbesar ke-k per baris
    sisa = (acak >= batas) & (acak > 0)
    return pd.DataFrame(sisa.astype("int8"), index=X.index, columns=X.columns)


def evaluasi(X, label, fold, k_teknologi=None, pakai_idf=True, seed=0) -> pd.DataFrame:
    """Peringkat bidang yang benar untuk setiap developer uji; IDF dan profil dibentuk ulang per fold."""
    hasil = []
    for f in sorted(fold[fold >= 0].unique()):
        latih, uji = fold != f, fold == f
        w = hitung_idf(X[latih]) if pakai_idf else pd.Series(1.0, index=X.columns)
        P, norma_P = bentuk_profil(X[latih], label[latih], w)
        U = sisakan_teknologi(X[uji], k_teknologi, seed) * w
        cos = hitung_cosine(U, P, norma_P)
        urutan = P.index.to_numpy()[urutkan_bidang(cos)]
        benar = label[uji].to_numpy()[:, None]
        hasil.append(
            pd.DataFrame({"bidang": label[uji], "peringkat": (urutan == benar).argmax(axis=1) + 1})
        )
    return pd.concat(hasil)


def evaluasi_popularitas(label: pd.Series, fold: pd.Series) -> pd.DataFrame:
    """Baseline (K15): semua developer uji menerima bidang terbanyak pada data latih."""
    hasil = []
    for f in sorted(fold[fold >= 0].unique()):
        latih, uji = fold != f, fold == f
        urutan = list(label[latih].value_counts().index)
        hasil.append(
            pd.DataFrame(
                {
                    "bidang": label[uji],
                    "peringkat": label[uji].map(lambda b, u=urutan: u.index(b) + 1),
                }
            )
        )
    return pd.concat(hasil)


def hit_at_k(hasil: pd.DataFrame, k: int) -> dict:
    """Hit@K, Pers. (2.5), dan macro-Hit@K, Pers. (2.6)."""
    kena = hasil["peringkat"] <= k
    return {
        f"Hit@{k}": float(kena.mean()),
        f"macro-Hit@{k}": float(kena.groupby(hasil["bidang"]).mean().mean()),
    }


def evaluasi_lengkap(X, label, awal, k_fold, seed, skenario, top_k=3) -> dict:
    """Metrik untuk semua skenario jumlah teknologi, ditambah baseline popularitas."""
    fold = bagi_fold(label, awal, k_fold, seed)
    skenario_hasil = []
    for k in skenario:
        h = evaluasi(X, label, fold, k_teknologi=k, seed=seed)
        skenario_hasil.append(
            {"teknologi": k if k is not None else "semua", "n_uji": len(h), **hit_at_k(h, top_k)}
        )
    return {
        "n_uji": int((fold >= 0).sum()),
        "skenario": skenario_hasil,
        "baseline_popularitas": hit_at_k(evaluasi_popularitas(label, fold), top_k),
    }
