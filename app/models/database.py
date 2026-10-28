from datetime import UTC, datetime

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


def _now() -> datetime:
    return datetime.now(UTC)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)
    password: str
    role: str = Field(default="student", sa_column_kwargs={"server_default": "student"})


class ProfileVersion(SQLModel, table=True):
    """Satu hasil pemrosesan dataset. Hanya satu versi yang boleh aktif."""

    id: int | None = Field(default=None, primary_key=True)
    filename: str
    status: str = "processing"  # processing | ready | failed
    is_active: bool = False
    error: str | None = None
    created_at: datetime = Field(default_factory=_now)
    # penyaringan, jumlah per bidang, parameter beserta alasannya, metrik evaluasi
    ringkasan: dict | None = Field(default=None, sa_column=Column(JSON))
    # IDF dan profil 12 bidang (dipakai saat rekomendasi)
    model: dict | None = Field(default=None, sa_column=Column(JSON))


class Recommendation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    version_id: int = Field(foreign_key="profileversion.id")
    created_at: datetime = Field(default_factory=_now)
    hasil: dict = Field(sa_column=Column(JSON))  # salinan hasil agar riwayat tetap utuh
