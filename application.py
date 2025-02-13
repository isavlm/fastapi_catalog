from main import app
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # This is the WSGI entry point
    application = app
    logger.info("FastAPI application initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize FastAPI application: {str(e)}")
    raise

# For local development
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
