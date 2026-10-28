"""Rekomendasi bidang karier untuk Mahasiswa (Bab III 3.2, langkah M1-M4)."""

import numpy as np
import pandas as pd


def periksa_input(dipilih: list[str], daftar_teknologi, min_teknologi: int) -> list[str]:
    """Daftar pesan kesalahan; kosong berarti masukan valid."""
    pesan = []
    dikenal = set(daftar_teknologi)
    tidak_dikenal = sorted({t for t in dipilih if t not in dikenal})
    if tidak_dikenal:
        pesan.append(f"Teknologi tidak dikenal: {tidak_dikenal}")
    if len(set(dipilih)) < min_teknologi:
        pesan.append(f"Pilih minimal {min_teknologi} teknologi (baru {len(set(dipilih))}).")
    return pesan


def vektor_mahasiswa(dipilih, w: pd.Series) -> pd.Series:
    """Vektor u: bernilai bobot IDF pada teknologi terpilih, 0 pada lainnya."""
    u = pd.Series(0.0, index=w.index)
    pilihan = list(dipilih)
    u[pilihan] = w[pilihan]
    return u


def hitung_cosine(U, P: pd.DataFrame, norma_P: pd.Series) -> np.ndarray:
    """Cosine similarity, Pers. (2.4), antara setiap baris U dan setiap profil P."""
    U = np.asarray(U, dtype=float)
    dot = U @ P.to_numpy().T
    norma_U = np.sqrt((U**2).sum(axis=1))
    penyebut = norma_U[:, None] * norma_P.to_numpy()[None, :]
    return np.divide(dot, penyebut, out=np.zeros_like(dot), where=penyebut > 0)


def urutkan_bidang(cos: np.ndarray) -> np.ndarray:
    """Indeks bidang dari skor terbesar; skor seri mengikuti urutan baris profil (stabil)."""
    return np.argsort(-cos, axis=1, kind="stable")


def sumbangan_teknologi(bidang: str, dipilih, w: pd.Series, P: pd.DataFrame) -> pd.Series:
    """Sumbangan tiap teknologi terpilih terhadap dot product bidang, Pers. (3.3); jumlahnya 1."""
    u = vektor_mahasiswa(dipilih, w)
    suku = (u * P.loc[bidang])[list(dipilih)]
    total = suku.sum()
    sumbangan = suku / total if total > 0 else suku * 0.0
    return sumbangan.sort_values(ascending=False, kind="stable")


def teknologi_umum(bidang, P, w, dipilih, dikecualikan=(), n=5) -> list[dict]:
    """Teknologi dengan proporsi pemakaian terbesar di bidang (deskriptif); proporsi = P / w."""
    proporsi = (P.loc[bidang] / w).drop(list(dikecualikan), errors="ignore")
    umum = proporsi.sort_values(ascending=False, kind="stable").head(n)
    terpilih = set(dipilih)
    return [{"kode": k, "proporsi": float(v), "dipilih": k in terpilih} for k, v in umum.items()]


def rekomendasi(
    dipilih, w, P, norma_P, top_k=3, dikecualikan=(), n_umum=5, n_sumbangan=None
) -> dict:
    """Peringkat seluruh bidang; dasar perhitungan disusun untuk ``top_k`` bidang teratas."""
    dipilih = list(dict.fromkeys(dipilih))  # buang duplikat, pertahankan urutan
    u = vektor_mahasiswa(dipilih, w)
    cos = hitung_cosine(u.to_frame().T, P, norma_P)[0]
    urutan = urutkan_bidang(cos[None, :])[0]
    peringkat = []
    for rank, i in enumerate(urutan, start=1):
        bidang = P.index[i]
        baris = {"peringkat": rank, "bidang_karier": bidang, "skor": float(cos[i])}
        if rank <= top_k:
            sb = sumbangan_teknologi(bidang, dipilih, w, P)
            if n_sumbangan:
                sb = sb.head(n_sumbangan)
            baris["sumbangan"] = [{"kode": k, "sumbangan": float(v)} for k, v in sb.items()]
            baris["teknologi_umum"] = teknologi_umum(bidang, P, w, dipilih, dikecualikan, n_umum)
        peringkat.append(baris)
    return {"teknologi_dipilih": dipilih, "peringkat": peringkat}
