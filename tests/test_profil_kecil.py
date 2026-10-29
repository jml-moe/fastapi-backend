"""Alur rekomendasi dan profil bidang dengan satu versi profil kecil yang disisipkan langsung
(tanpa dataset survei), agar tetap teruji di mesin yang tidak punya dataset."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, select

from app.main import app
from app.models.database import ProfileVersion
from app.models.engine import engine

KOLOM = ["lang:Python", "lang:SQL", "db:PostgreSQL", "web:React", "web:Django"]
IDF = [1.0, 1.2, 1.5, 1.8, 2.0]
BIDANG = ["Backend", "Frontend", "Data"]
# proporsi pemakaian per bidang; profil P = proporsi x bobot IDF
PROPORSI = [
    [0.9, 0.8, 0.7, 0.1, 0.6],
    [0.3, 0.2, 0.1, 0.9, 0.1],
    [0.2, 0.9, 0.1, 0.1, 0.1],
]
MODEL = {
    "kolom": KOLOM,
    "idf": IDF,
    "bidang": BIDANG,
    "n_developer": [300, 200, 100],
    "P": [[p * w for p, w in zip(baris, IDF, strict=True)] for baris in PROPORSI],
}


@pytest.fixture(scope="module")
def client():
    SQLModel.metadata.create_all(engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module", autouse=True)
def versi_aktif_kecil(client):
    with Session(engine) as db:
        for lama in db.exec(select(ProfileVersion).where(ProfileVersion.is_active)).all():
            lama.is_active = False
            db.add(lama)
        db.add(ProfileVersion(filename="kecil.csv", status="ready", is_active=True, model=MODEL))
        db.commit()


def masuk(client, email, password):
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


@pytest.fixture(scope="module")
def mhs(client):
    body = {"name": "Mhs Kecil", "email": "kecil@test.local", "password": "rahasia123"}
    assert client.post("/auth/register", json=body).status_code == 201
    return masuk(client, body["email"], body["password"])


@pytest.fixture(scope="module")
def admin(client):
    return masuk(client, "admin@test.local", "admin-test-123")


def test_daftar_teknologi_per_kelompok(client, mhs):
    data = client.get("/technologies", headers=mhs).json()
    assert {"kode": "lang:Python", "nama": "Python"} in data["Bahasa pemrograman"]
    assert {"kode": "web:React", "nama": "React"} in data["Framework web"]


def test_rekomendasi_dengan_dasar_perhitungan(client, mhs):
    r = client.post(
        "/recommendations",
        json={"teknologi": ["lang:Python", "lang:SQL", "db:PostgreSQL"]},
        headers=mhs,
    )
    assert r.status_code == 201, r.text
    hasil = r.json()
    assert hasil["peringkat"][0]["bidang_karier"] == "Backend"
    assert len(hasil["peringkat"]) == 3
    teratas = hasil["peringkat"][0]
    assert sum(s["sumbangan"] for s in teratas["sumbangan"]) == pytest.approx(1.0)
    assert teratas["teknologi_umum"]
    # detail hanya untuk tiga bidang teratas; peringkat ke-4 dan seterusnya ringkas
    assert all("sumbangan" in p for p in hasil["peringkat"])


def test_rekomendasi_minimal_tiga_teknologi(client, mhs):
    r = client.post("/recommendations", json={"teknologi": ["lang:Python"]}, headers=mhs)
    assert r.status_code == 422


def test_profil_bidang_memuat_bobot_idf(client, admin):
    data = client.get("/admin/profiles", headers=admin).json()
    backend = next(b for b in data["bidang"] if b["bidang_karier"] == "Backend")
    assert backend["n_developer"] == 300
    python = next(t for t in backend["teknologi"] if t["kode"] == "lang:Python")
    assert python["proporsi"] == pytest.approx(0.9)
    assert python["bobot_idf"] == pytest.approx(1.0)
    django = next(t for t in backend["teknologi"] if t["kode"] == "web:Django")
    assert django["bobot_idf"] == pytest.approx(2.0)


def test_profil_bidang_membatasi_jumlah_teknologi(client, admin):
    data = client.get("/admin/profiles?top=2", headers=admin).json()
    assert all(len(b["teknologi"]) == 2 for b in data["bidang"])


def test_profil_bidang_hanya_untuk_admin(client, mhs):
    assert client.get("/admin/profiles", headers=mhs).status_code == 403
