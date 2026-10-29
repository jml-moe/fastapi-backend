"""Pratinjau data lewat API dengan unggahan dataset sintetis (alur sungguhan, tanpa dataset survei)."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from app.main import app
from app.models.engine import engine
from tests.ml.sintetis import buat_dataset_sintetis


@pytest.fixture(scope="module")
def client():
    SQLModel.metadata.create_all(engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin(client):
    r = client.post("/auth/login", json={"email": "admin@test.local", "password": "admin-test-123"})
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_unggahan_membentuk_pratinjau_dan_ikut_terhapus(client, admin):
    csv = buat_dataset_sintetis().to_csv(index=False).encode()
    r = client.post("/admin/profile-versions", headers=admin, files={"file": ("sintetis.csv", csv)})
    assert r.status_code == 202
    vid = r.json()["id"]

    detail = client.get(f"/admin/profile-versions/{vid}", headers=admin).json()
    assert detail["status"] == "ready", detail.get("error")
    pr = detail["pratinjau"]
    assert pr["mentah"]["total"] == 655 and len(pr["mentah"]["baris"]) == 100
    assert pr["terproses"]["total"] == detail["ringkasan"]["n_developer"] == 600

    # daftar versi tidak membawa pratinjau (ukuran)
    daftar = client.get("/admin/profile-versions", headers=admin).json()
    assert "pratinjau" not in next(v for v in daftar if v["id"] == vid)

    assert client.delete(f"/admin/profile-versions/{vid}", headers=admin).status_code == 204
    assert client.get(f"/admin/profile-versions/{vid}", headers=admin).status_code == 404


def test_versi_tanpa_pratinjau_mengembalikan_null(client, admin):
    r = client.post(
        "/admin/profile-versions",
        headers=admin,
        files={"file": ("a.csv", b"ResponseId,DevType\n1,x\n")},
    )
    detail = client.get(f"/admin/profile-versions/{r.json()['id']}", headers=admin).json()
    assert detail["status"] == "failed" and detail["pratinjau"] is None
    client.delete(f"/admin/profile-versions/{r.json()['id']}", headers=admin)
