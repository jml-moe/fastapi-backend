"""Operasi hapus dan ubah yang RESTful: versi profil (Admin) dan riwayat rekomendasi (Mahasiswa)."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, select

from app.main import app
from app.models.database import ProfileVersion
from app.models.engine import engine
from tests.test_profil_kecil import MODEL

PILIHAN = ["lang:Python", "lang:SQL", "db:PostgreSQL"]


@pytest.fixture(scope="module")
def client():
    SQLModel.metadata.create_all(engine)
    with TestClient(app) as c:
        yield c


def masuk(client, email, password):
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def daftar_dan_masuk(client, email):
    body = {"name": email.split("@")[0], "email": email, "password": "rahasia123"}
    assert client.post("/auth/register", json=body).status_code == 201
    return masuk(client, email, body["password"])


@pytest.fixture(scope="module")
def admin(client):
    return masuk(client, "admin@test.local", "admin-test-123")


@pytest.fixture(scope="module")
def mhs1(client):
    return daftar_dan_masuk(client, "crud1@test.local")


@pytest.fixture(scope="module")
def mhs2(client):
    return daftar_dan_masuk(client, "crud2@test.local")


@pytest.fixture(autouse=True)
def tanpa_versi_aktif(client):
    """Setiap tes mulai tanpa versi aktif agar urutan tes tidak saling memengaruhi."""
    with Session(engine) as db:
        for v in db.exec(select(ProfileVersion).where(ProfileVersion.is_active)).all():
            v.is_active = False
            db.add(v)
        db.commit()


def buat_versi(status="ready", aktif=False) -> int:
    with Session(engine) as db:
        v = ProfileVersion(
            filename=f"{status}.csv",
            status=status,
            is_active=aktif,
            model=MODEL if status == "ready" else None,
        )
        db.add(v)
        db.commit()
        db.refresh(v)
        return v.id


def ubah(client, admin, vid, aktif):
    return client.patch(f"/admin/profile-versions/{vid}", json={"is_active": aktif}, headers=admin)


def test_unggah_di_koleksi_versi_dengan_location(client, admin):
    r = client.post(
        "/admin/profile-versions",
        headers=admin,
        files={"file": ("a.csv", b"ResponseId,DevType\n1,x\n")},
    )
    assert r.status_code == 202
    assert r.headers["location"] == f"/admin/profile-versions/{r.json()['id']}"


def test_endpoint_lama_sudah_tidak_ada(client, admin):
    # 404 tanpa frontend ter-build, 405 bila StaticFiles terpasang di "/"
    r = client.post("/admin/datasets", headers=admin, files={"file": ("a.csv", b"x")})
    assert r.status_code in (404, 405)
    r = client.post(f"/admin/profile-versions/{buat_versi()}/activate", headers=admin)
    assert r.status_code in (404, 405)


def test_patch_mengaktifkan_dan_menonaktifkan_yang_lain(client, admin):
    a, b = buat_versi(), buat_versi()
    assert ubah(client, admin, a, True).json()["is_active"] is True
    hasil = ubah(client, admin, b, True).json()
    assert hasil["id"] == b and hasil["is_active"] is True
    daftar = {
        v["id"]: v["is_active"] for v in client.get("/admin/profile-versions", headers=admin).json()
    }
    assert daftar[a] is False and daftar[b] is True


def test_patch_menonaktifkan_versi(client, admin):
    a = buat_versi(aktif=True)
    assert ubah(client, admin, a, False).json()["is_active"] is False
    assert client.get("/admin/profiles", headers=admin).status_code == 404


def test_patch_hanya_versi_ready_yang_bisa_diaktifkan(client, admin):
    assert ubah(client, admin, buat_versi("failed"), True).status_code == 409
    assert ubah(client, admin, buat_versi("processing"), True).status_code == 409
    assert ubah(client, admin, 999999, True).status_code == 404


def test_hapus_versi_ready_dan_failed(client, admin):
    for status in ("ready", "failed"):
        vid = buat_versi(status)
        assert client.delete(f"/admin/profile-versions/{vid}", headers=admin).status_code == 204
        assert client.get(f"/admin/profile-versions/{vid}", headers=admin).status_code == 404
        assert client.delete(f"/admin/profile-versions/{vid}", headers=admin).status_code == 404


def test_versi_aktif_dan_processing_tidak_bisa_dihapus(client, admin):
    aktif = buat_versi(aktif=True)
    assert client.delete(f"/admin/profile-versions/{aktif}", headers=admin).status_code == 409
    sedang = buat_versi("processing")
    assert client.delete(f"/admin/profile-versions/{sedang}", headers=admin).status_code == 409
    assert client.get(f"/admin/profile-versions/{aktif}", headers=admin).status_code == 200


def test_riwayat_tetap_utuh_setelah_versinya_dihapus(client, admin, mhs1):
    vid = buat_versi(aktif=True)
    r = client.post("/recommendations", json={"teknologi": PILIHAN}, headers=mhs1)
    assert r.status_code == 201, r.text
    rec_id = r.json()["id"]
    assert ubah(client, admin, vid, False).status_code == 200
    assert client.delete(f"/admin/profile-versions/{vid}", headers=admin).status_code == 204

    detail = client.get(f"/recommendations/{rec_id}", headers=mhs1)
    assert detail.status_code == 200
    assert detail.json()["peringkat"][0]["bidang_karier"] == "Backend"
    assert detail.json()["version_id"] == vid  # salinan hasil tidak berubah
    assert rec_id in [x["id"] for x in client.get("/recommendations", headers=mhs1).json()]


def test_hapus_rekomendasi_sendiri(client, mhs1):
    buat_versi(aktif=True)
    rec_id = client.post("/recommendations", json={"teknologi": PILIHAN}, headers=mhs1).json()["id"]
    assert client.delete(f"/recommendations/{rec_id}", headers=mhs1).status_code == 204
    assert client.get(f"/recommendations/{rec_id}", headers=mhs1).status_code == 404
    assert client.delete(f"/recommendations/{rec_id}", headers=mhs1).status_code == 404


def test_hapus_rekomendasi_orang_lain_dijawab_404(client, mhs1, mhs2):
    buat_versi(aktif=True)
    rec_id = client.post("/recommendations", json={"teknologi": PILIHAN}, headers=mhs1).json()["id"]
    assert client.delete(f"/recommendations/{rec_id}", headers=mhs2).status_code == 404
    assert client.get(f"/recommendations/{rec_id}", headers=mhs1).status_code == 200


def test_mahasiswa_tidak_boleh_ubah_atau_hapus_versi(client, mhs1):
    vid = buat_versi()
    assert (
        client.patch(
            f"/admin/profile-versions/{vid}", json={"is_active": True}, headers=mhs1
        ).status_code
        == 403
    )
    assert client.delete(f"/admin/profile-versions/{vid}", headers=mhs1).status_code == 403
    assert client.delete(f"/admin/profile-versions/{vid}").status_code in (401, 403)
