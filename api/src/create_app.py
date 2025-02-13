from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from adapters.src.repositories import Connection, SessionManager, SQLConnection

from api.src.routes import health_check_router, product_router

from dotenv import load_dotenv
import os
import logging
import time
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_access.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    connection: Connection = SQLConnection()
    SessionManager.initialize_session(connection)
    yield
    SessionManager.close_session()


def create_app() -> FastAPI:
    app = FastAPI(title="Catalog API", lifespan=lifespan)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        logger.info(
            f"Path: {request.url.path} | "
            f"Method: {request.method} | "
            f"Client: {request.client.host} | "
            f"Duration: {duration:.2f}s | "
            f"Status: {response.status_code}"
        )
        
        return response

    # Add routes
    app.include_router(health_check_router, tags=["health check"])
    app.include_router(product_router, tags=["products"])

    return app

print("DATABASE_URL:", os.getenv("DATABASE_URL"))
app = create_app()