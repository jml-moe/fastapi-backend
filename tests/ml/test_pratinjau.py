"""Pratinjau data (mentah dan terproses) dan alur pipeline penuh dengan data sintetis."""

import json

import pytest

from app.ml.params import Params
from app.ml.pipeline import bangun_versi_profil
from app.ml.pratinjau import buat_pratinjau
from app.ml.preprocess import KOLOM_WAJIB, bangun_data_final
from tests.ml.sintetis import buat_dataset_sintetis


@pytest.fixture(scope="module")
def df():
    return buat_dataset_sintetis()


@pytest.fixture(scope="module")
def hasil(df):
    return bangun_versi_profil(df)


def test_pipeline_sintetis_menghasilkan_profil_dan_metrik(hasil):
    assert list(hasil.P.index) and len(hasil.P.index) == 3
    assert hasil.ringkasan()["metrik"]["skenario"]
    assert hasil.ringkasan()["n_developer"] == 600  # 55 baris tambahan sengaja tersaring


def test_pratinjau_mentah(df, hasil):
    mentah = hasil.pratinjau["mentah"]
    assert mentah["total"] == len(df)
    assert mentah["kolom"] == KOLOM_WAJIB
    assert len(mentah["baris"]) == 100
    assert all(set(b) == set(KOLOM_WAJIB) for b in mentah["baris"])
    assert any(b["WorkExp"] is None for b in mentah["baris"])  # NaN menjadi null


def test_pratinjau_terproses(hasil):
    terproses = hasil.pratinjau["terproses"]
    assert terproses["total"] == hasil.ringkasan()["n_developer"]
    assert len(terproses["baris"]) == 100
    bidang_profil = set(hasil.P.index)
    for b in terproses["baris"]:
        assert b["bidang_karier"] in bidang_profil
        assert isinstance(b["awal_karier"], bool)
        assert b["jumlah_teknologi"] == len(b["teknologi"]) > 0
        assert all(":" in kode for kode in b["teknologi"])


def test_pratinjau_lebih_sedikit_dari_total_dan_lolos_json(df, hasil):
    assert hasil.pratinjau["terproses"]["total"] < hasil.pratinjau["mentah"]["total"]
    json.dumps(hasil.pratinjau)  # tipe numpy dan NaN sudah dibersihkan


def test_pratinjau_sampel_acak_dengan_seed_tetap(df):
    data = bangun_data_final(df, Params())
    a, b = buat_pratinjau(df, data, seed=0), buat_pratinjau(df, data, seed=0)
    c = buat_pratinjau(df, data, seed=1)
    assert a == b
    assert a["mentah"]["baris"] != c["mentah"]["baris"]
    # bukan 100 baris pertama berkas
    assert [r["ResponseId"] for r in a["mentah"]["baris"]] != list(range(1, 101))


def test_pratinjau_n_kecil(df):
    data = bangun_data_final(df, Params())
    kecil = buat_pratinjau(df, data, n=5)
    assert len(kecil["mentah"]["baris"]) == len(kecil["terproses"]["baris"]) == 5
