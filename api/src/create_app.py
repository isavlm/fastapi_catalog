from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from adapters.src.repositories import Connection, SessionManager, SQLConnection

from api.src.routes import product_router

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
    connection: Connection = SQLConnection()
    SessionManager.initialize_session(connection)
    yield
    SessionManager.close_session()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Catalog API",
        description="""
        # Catalog API Documentation

        Welcome to the Catalog API! This API is part of the CCPathways Apprenticeship Program (https://ccpathways.org/) Level 2. It was written on Python, deployed using CICD on DigitalOcean.

        * **Products Management**: Create, read, update, and delete products
        * **Status Filtering**: Filter products by their status (New, Used, For parts)
        * **Location Search**: Find products by store location
        * **Availability Check**: Filter products by availability

        ## Getting Started

        To start using the API, you can:
        1. Browse the available endpoints below
        2. Try out the endpoints using the interactive Swagger UI
        3. Use the ReDoc interface for a more readable documentation

        ## Authentication

        Currently, the API is open for testing. Authentication will be implemented in future versions.

        ## Rate Limiting

        Please note that there are rate limits in place to ensure fair usage:
        * 100 requests per minute per IP address

        ## Need Help?

        For any questions or support, please contact me at ivlm@pm.me""",
        version="1.0.0",
        license_info={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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

    @app.get("/")
    async def health_check():
        return {"status": "OK"}

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
    app.include_router(product_router, tags=["products"])

    return app

logger.info("Checking DATABASE_URL...")
logger.info(f"DATABASE_URL is {'set' if os.getenv('DATABASE_URL') else 'not set'}")
app = create_app()