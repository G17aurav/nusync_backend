from fastapi import FastAPI

from app.db.connection import connect_db
from app.routers.admin import router as admin_router
from app.routers.license import router as license_router

app = FastAPI()
app.include_router(admin_router)
app.include_router(license_router)


@app.on_event("startup")
async def startup():
    await connect_db()


@app.get("/")
async def root():
    return {"status": "ok"}