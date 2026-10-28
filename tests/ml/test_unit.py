"""Unit tes inti ML dengan data sintetis kecil (tanpa dataset survei)."""

import numpy as np
import pandas as pd
import pytest
from sklearn.feature_extraction.text import TfidfTransformer

from app.ml.evaluate import bagi_fold, hit_at_k, sisakan_teknologi
from app.ml.params import Params, ukuran_sampel
from app.ml.profile import bentuk_profil, hitung_idf
from app.ml.recommend import (
    hitung_cosine,
    periksa_input,
    rekomendasi,
    sumbangan_teknologi,
    urutkan_bidang,
)


@pytest.fixture
def kecil():
    X = pd.DataFrame(
        {
            "lang:Python": [1, 1, 1, 0, 0, 1],
            "lang:PHP": [0, 0, 0, 1, 1, 0],
            "db:PostgreSQL": [1, 0, 1, 1, 1, 0],
            "web:Django": [1, 1, 0, 0, 0, 0],
            "web:Laravel": [0, 0, 0, 1, 1, 0],
        },
        dtype="int8",
    )
    label = pd.Series(["ml", "ml", "ml", "web", "web", "data"])
    return X, label


def test_n_min_cochran():
    assert Params().n_min == 151
    assert ukuran_sampel(1.96, 0.5, 0.05) == 385


def test_semua_parameter_punya_alasan_dan_sumber():
    for item in Params().penjelasan():
        assert item["alasan"] and item["sumber"], item["parameter"]


def test_idf_sama_dengan_scikit_learn(kecil):
    X, _ = kecil
    ref = TfidfTransformer(smooth_idf=True).fit(X.to_numpy()).idf_
    np.testing.assert_allclose(hitung_idf(X).to_numpy(), ref)


def test_profil_urutan_bidang_terbanyak_dulu(kecil):
    X, label = kecil
    P, norma = bentuk_profil(X, label, hitung_idf(X))
    assert list(P.index) == ["ml", "web", "data"]
    np.testing.assert_allclose(norma.to_numpy(), np.sqrt((P**2).sum(axis=1)).to_numpy())


def test_cosine_identik_bernilai_satu():
    P = pd.DataFrame([[1.0, 2.0], [2.0, 0.0]], index=["a", "b"])
    norma = np.sqrt((P**2).sum(axis=1))
    cos = hitung_cosine([[1.0, 2.0]], P, norma)
    assert cos[0, 0] == pytest.approx(1.0)
    assert 0 <= cos[0, 1] <= 1


def test_cosine_vektor_nol_tidak_error():
    P = pd.DataFrame([[1.0, 2.0]], index=["a"])
    assert hitung_cosine([[0.0, 0.0]], P, np.sqrt((P**2).sum(axis=1)))[0, 0] == 0


def test_skor_seri_didahulukan_bidang_terbanyak():
    # dua profil identik: bidang di baris pertama (developer terbanyak) harus menang
    assert list(urutkan_bidang(np.array([[0.5, 0.5, 0.1]]))[0]) == [0, 1, 2]


def test_sumbangan_berjumlah_satu(kecil):
    X, label = kecil
    w = hitung_idf(X)
    P, _ = bentuk_profil(X, label, w)
    sb = sumbangan_teknologi("ml", ["lang:Python", "db:PostgreSQL", "web:Django"], w, P)
    assert sb.sum() == pytest.approx(1.0)


def test_rekomendasi_deterministik_dan_lengkap(kecil):
    X, label = kecil
    w = hitung_idf(X)
    P, norma = bentuk_profil(X, label, w)
    dipilih = ["lang:PHP", "web:Laravel", "db:PostgreSQL"]
    a = rekomendasi(dipilih, w, P, norma, top_k=2)
    b = rekomendasi(dipilih, w, P, norma, top_k=2)
    assert a == b
    assert a["peringkat"][0]["bidang_karier"] == "web"
    assert len(a["peringkat"]) == 3  # peringkat seluruh bidang
    assert "sumbangan" in a["peringkat"][1] and "sumbangan" not in a["peringkat"][2]


def test_periksa_input():
    daftar = ["a", "b", "c"]
    assert periksa_input(["a", "b", "c"], daftar, 3) == []
    assert "minimal 3" in periksa_input(["a", "a", "b"], daftar, 3)[0]  # duplikat tidak dihitung
    assert "tidak dikenal" in periksa_input(["a", "b", "x"], daftar, 3)[0]


def test_sisakan_teknologi(kecil):
    X, _ = kecil
    sisa = sisakan_teknologi(X, 1, seed=0)
    assert (sisa.sum(axis=1) <= 1).all()
    assert (sisa <= X).all().all()
    assert sisakan_teknologi(X, None) is X


def test_bagi_fold_hanya_awal_karier_dan_stratified():
    label = pd.Series(["a"] * 10 + ["b"] * 10 + ["a"] * 4)
    awal = pd.Series([True] * 20 + [False] * 4)
    fold = bagi_fold(label, awal, k=5, seed=0)
    assert (fold[~awal] == -1).all()  # bukan awal karier tidak pernah menjadi data uji
    for f in range(5):
        uji = label[fold == f]
        assert (uji == "a").sum() == 2 and (uji == "b").sum() == 2


def test_hit_at_k():
    h = pd.DataFrame({"bidang": ["a", "a", "b", "b"], "peringkat": [1, 4, 2, 3]})
    r = hit_at_k(h, 3)
    assert r["Hit@3"] == pytest.approx(0.75)
    assert r["macro-Hit@3"] == pytest.approx((0.5 + 1.0) / 2)
