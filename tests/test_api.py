"""Tes API dari ujung ke ujung (database sementara)."""

import time

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from app.main import app
from app.models.engine import engine
from tests.conftest import DATASET


@pytest.fixture(scope="module")
def client():
    SQLModel.metadata.create_all(engine)
    with TestClient(app) as c:  # menjalankan lifespan -> akun Admin dibuat
        yield c


def masuk(client, email, password):
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


@pytest.fixture(scope="module")
def admin(client):
    return masuk(client, "admin@test.local", "admin-test-123")


@pytest.fixture(scope="module")
def mhs(client):
    body = {"name": "Mhs", "email": "mhs@test.local", "password": "rahasia123"}
    assert client.post("/auth/register", json=body).status_code == 201
    return masuk(client, body["email"], body["password"])


def test_mahasiswa_tidak_boleh_ke_admin(client, mhs):
    assert client.get("/admin/profile-versions", headers=mhs).status_code == 403
    assert client.get("/admin/profile-versions").status_code in (401, 403)  # tanpa token


def test_rekomendasi_sebelum_ada_profil_aktif(client, mhs):
    assert client.get("/technologies", headers=mhs).status_code == 503


def test_unggah_berkas_bukan_dataset(client, admin):
    r = client.post("/admin/datasets", headers=admin, files={"file": ("a.txt", b"x")})
    assert r.status_code == 422


def test_kolom_tidak_lengkap_menjadi_failed(client, admin):
    r = client.post(
        "/admin/datasets", headers=admin, files={"file": ("a.csv", b"ResponseId,DevType\n1,x\n")}
    )
    assert r.status_code == 202
    v = client.get(f"/admin/profile-versions/{r.json()['id']}", headers=admin).json()
    assert v["status"] == "failed" and "Kolom wajib" in v["error"]
    assert (
        client.post(f"/admin/profile-versions/{v['id']}/activate", headers=admin).status_code == 409
    )


@pytest.mark.skipif(not DATASET.exists(), reason=f"dataset tidak ada: {DATASET}")
def test_alur_lengkap_admin_lalu_mahasiswa(client, admin, mhs):
    # --- Admin: unggah, tunggu, aktifkan ---
    with open(DATASET, "rb") as f:
        r = client.post("/admin/datasets", headers=admin, files={"file": (DATASET.name, f)})
    assert r.status_code == 202
    vid = r.json()["id"]
    for _ in range(
        120
    ):  # TestClient menjalankan tugas latar sebelum kembali; loop untuk server nyata
        v = client.get(f"/admin/profile-versions/{vid}", headers=admin).json()
        if v["status"] != "processing":
            break
        time.sleep(1)
    assert v["status"] == "ready", v.get("error")
    assert v["ringkasan"]["n_developer"] == 16132
    assert client.post(f"/admin/profile-versions/{vid}/activate", headers=admin).status_code == 200
    profil = client.get("/admin/profiles", headers=admin).json()
    assert len(profil["bidang"]) == 12

    # --- Mahasiswa ---
    tek = client.get("/technologies", headers=mhs).json()
    assert sum(len(x) for x in tek.values()) == 142

    pilihan = {"teknologi": ["lang:Python", "lang:SQL", "db:PostgreSQL"]}
    r = client.post("/recommendations", headers=mhs, json=pilihan)
    assert r.status_code == 201, r.text
    hasil = r.json()
    assert len(hasil["peringkat"]) == 12
    skor = [p["skor"] for p in hasil["peringkat"]]
    assert skor == sorted(skor, reverse=True)
    for p in hasil["peringkat"][:3]:
        assert sum(s["sumbangan"] for s in p["sumbangan"]) == pytest.approx(1.0)
        assert len(p["teknologi_umum"]) == 5
    assert "sumbangan" not in hasil["peringkat"][3]
    # konsisten: masukan sama -> hasil sama
    ulang = client.post("/recommendations", headers=mhs, json=pilihan).json()
    assert [p["bidang_karier"] for p in ulang["peringkat"]] == [
        p["bidang_karier"] for p in hasil["peringkat"]
    ]

    # validasi masukan
    assert (
        client.post(
            "/recommendations", headers=mhs, json={"teknologi": ["lang:Python"]}
        ).status_code
        == 422
    )
    r = client.post(
        "/recommendations", headers=mhs, json={"teknologi": ["lang:Python", "lang:SQL", "xx:Bukan"]}
    )
    assert r.status_code == 422

    # riwayat dan detail; milik pengguna lain tidak terlihat
    riwayat = client.get("/recommendations", headers=mhs).json()
    assert len(riwayat) == 2 and len(riwayat[0]["top"]) == 3
    assert client.get(f"/recommendations/{hasil['id']}", headers=mhs).status_code == 200
    assert client.get(f"/recommendations/{hasil['id']}", headers=admin).status_code == 404
