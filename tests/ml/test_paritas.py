"""Tes paritas: pipeline harus mereproduksi angka di naskah/tracker (K1-K16).

Dilewati bila dataset tidak ada (berkasnya tidak disimpan di git); letakkan di data/ untuk menjalankan.
"""

import pytest

from app.ml.pipeline import bangun_versi_profil
from app.ml.preprocess import muat_dataset
from tests.conftest import DATASET

pytestmark = pytest.mark.skipif(not DATASET.exists(), reason=f"dataset tidak ada: {DATASET}")


@pytest.fixture(scope="module")
def hasil():
    return bangun_versi_profil(muat_dataset(str(DATASET)))


def test_tabel_penyaringan(hasil):
    assert [b["sisa"] for b in hasil.log] == [49196, 37467, 28774, 26320, 22584, 16723, 16132]


def test_jumlah_bidang_dan_awal_karier(hasil):
    assert len(hasil.per_bidang) == 12
    assert hasil.per_bidang["awal_karier"].sum() == 4364
    assert (hasil.per_bidang["semua"] >= 151).all()


def test_daftar_teknologi(hasil):
    t = hasil.teknologi.set_index("kode")
    assert len(t) == 142
    assert t["kelompok"].value_counts().to_dict() == {"lang": 42, "plat": 42, "db": 30, "web": 28}
    assert t.loc["lang:JavaScript", "jumlah_pemakai"] == 10972
    assert t.loc["web:Laravel", "jumlah_pemakai"] == 1078


def test_hit_at_3_sesuai_tracker(hasil):
    m = {s["teknologi"]: s for s in hasil.metrik["skenario"]}
    assert hasil.metrik["n_uji"] == 4364
    for k, hit, macro in [
        (3, 0.613, 0.586),
        (5, 0.655, 0.644),
        (8, 0.702, 0.703),
        ("semua", 0.772, 0.769),
    ]:
        assert m[k]["Hit@3"] == pytest.approx(hit, abs=5e-4)
        assert m[k]["macro-Hit@3"] == pytest.approx(macro, abs=5e-4)


def test_baseline_popularitas(hasil):
    b = hasil.metrik["baseline_popularitas"]
    assert b["Hit@3"] == pytest.approx(0.719, abs=5e-4)
    assert b["macro-Hit@3"] == pytest.approx(0.250, abs=5e-4)
