from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from scalar_fastapi import get_scalar_api_reference
from sqlmodel import Session, select

from app.core.settings import settings
from app.models.database import User
from app.models.engine import engine
from app.modules.admin.router import admin_router
from app.modules.auth.router import auth_router
from app.modules.auth.utils import hash_password
from app.modules.recommendation.router import recommendation_router


def seed_admin():
    """Buat akun Admin dari ADMIN_EMAIL/ADMIN_PASSWORD bila belum ada."""
    if not (settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD):
        return
    with Session(engine) as db:
        if db.exec(select(User).where(User.email == settings.ADMIN_EMAIL)).first():
            return
        db.add(
            User(
                name="Admin",
                email=settings.ADMIN_EMAIL,
                password=hash_password(settings.ADMIN_PASSWORD),
                role="admin",
            )
        )
        db.commit()


FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


def pasang_frontend(app: FastAPI, direktori: Path = FRONTEND_DIST) -> bool:
    """Sajikan hasil build frontend (Astro) dari satu origin. Panggil setelah semua route API
    didaftarkan agar route API selalu menang. Dilewati bila belum di-build (`make fe-build`)."""
    if not (direktori / "index.html").is_file():
        return False
    app.mount("/", StaticFiles(directory=direktori, html=True), name="frontend")
    return True


@asynccontextmanager
async def lifespan(_: FastAPI):
    seed_admin()
    yield


app = FastAPI(title="Sistem Rekomendasi Karier Developer", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(recommendation_router)


@app.get("/scalar", include_in_schema=False)
def get_scalar():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title=app.title)


pasang_frontend(app)
