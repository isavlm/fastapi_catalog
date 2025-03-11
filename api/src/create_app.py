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
from datetime import datetime

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Log to console
    ]
)

logger = logging.getLogger(__name__)

# Store some basic metrics
request_count = 0
last_request_time = None

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    logger.info("Starting up FastAPI application...")
    try:
        connection: Connection = SQLConnection()
        SessionManager.initialize_session(connection)
        logger.info("Database connection established successfully")
        yield
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    finally:
        logger.info("Shutting down FastAPI application...")
        SessionManager.close_session()


def create_app() -> FastAPI:
    logger.info("Creating FastAPI application...")
    app = FastAPI(title="Catalog API", lifespan=lifespan)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        global request_count, last_request_time
        
        # Update metrics
        request_count += 1
        last_request_time = datetime.now()
        
        # Log the request
        logger.info(
            f"Request #{request_count} | "
            f"Path: {request.url.path} | "
            f"Method: {request.method} | "
            f"Client: {request.client.host}"
        )
        
        # Process the request
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Log the response
        logger.info(
            f"Response | "
            f"Status: {response.status_code} | "
            f"Duration: {duration:.2f}s"
        )
        
        return response

    @app.get("/metrics")
    async def get_metrics():
        """Get basic API usage metrics"""
        return {
            "total_requests": request_count,
            "last_request": last_request_time.isoformat() if last_request_time else None,
            "uptime": "Active",
            "version": "1.0.0"
        }

    # Add routes
    logger.info("Registering routes...")
    app.include_router(health_check_router, tags=["health check"])
    app.include_router(product_router, tags=["products"])
    logger.info("Routes registered successfully")

    return app

logger.info("Checking DATABASE_URL...")
logger.info(f"DATABASE_URL is {'set' if os.getenv('DATABASE_URL') else 'not set'}")
app = create_app()