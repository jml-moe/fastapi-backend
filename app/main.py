from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.modules.auth.router import auth_router
from app.modules.post.router import post_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(post_router)


@app.get("/scalar")
def get_scalar():
    return get_scalar_api_reference(openapi_url=app.openapi_url)
