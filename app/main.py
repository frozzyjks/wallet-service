from fastapi import FastAPI
from app.api.wallets import router as wallets_router
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

app = FastAPI()

app.include_router(
    wallets_router,
    prefix="/api/v1/wallets",
)


@app.get("/__debug")
async def debug():
    return {
        "routes": [route.path for route in app.routes]
    }

@app.get("/health", tags=["health"])
async def healthcheck():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}