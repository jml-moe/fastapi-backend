from app.models.database import User
from app.modules.auth.service import get_current_user
from fastapi import APIRouter, Depends

post_router = APIRouter(prefix="/posts", tags=["Posts"])


@post_router.get("/")
def get_posts(current_user: User = Depends(get_current_user)):

    print(current_user.id)

    return {"posts": []}
