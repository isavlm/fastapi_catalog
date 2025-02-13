from typing import Literal
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel

health_check_router = APIRouter(prefix="/health_check")


class HealthCheck(BaseModel):
    status: Literal["OK", "ERROR"]
    timestamp: str
    version: str


@health_check_router.get("/", response_model=HealthCheck)
async def check_health() -> HealthCheck:
    return HealthCheck(
        status="OK",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )
