from app.api import app
from app.database import init_db
import logging
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return

    logger.info("Starting FastAPI server.")
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()
