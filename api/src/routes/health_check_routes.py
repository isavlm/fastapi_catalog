from fastapi import APIRouter

health_check_router = APIRouter(prefix="/health_check")


@health_check_router.get("/")
async def check_health():
    return {"status": "OK"}
