

# Web Scraper

This is a web scraper project built using FastAPI, SQLAlchemy, Celery, and PostgreSQL to fetch and parse ads.txt files from a list of domains. It stores legitimate sellers' information in a database and provides API endpoints to manage tasks and data.


# Requirements 

- Python 3.8+
- PostgreSQL
- Redis
- Celery

### Install Dependencies

1. Install the required dependencies:
   
  - pip install -r requirements.txt
   

2. Start Redis server (if not already running):
   
   - redis-server
   

5. Set up PostgreSQL database:

   - Ensure PostgreSQL is installed and running.
   - Create a new database `web_scraper_db` and configure the credentials in `.env` (Create a .env file) .
   - Example .env file ( DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/web_scraper_db
                         CELERY_BROKER_URL=redis://localhost:6379/0
                         CELERY_RESULT_BACKEND=redis://localhost:6379/0 )


6. Setup Alembic if want data migrations :
   
   #Make Migrations
    alembic revision --autogenerate -m "Updated run_id VARCHAR length"

   #Migrate
    alembic upgrade head
   

### Run the Application

1. Start the FastAPI server:

   - uvicorn main:app --reload 
   

1. Start the Celery worker:
   
   - celery -A app.celery.celery_app worker --loglevel=info
   

2. Start the Celery Beat scheduler (for scheduled tasks):
   
   - celery -A app.celery.celery_app beat --loglevel=info
   

The application will be running at `http://127.0.0.1:8000`.

### Example API Endpoints

1. `http://127.0.0.1:8000/legitimate_sellers?domain=bloomberg.com` - Gets a list of legitimate sellers for a specific domain. (GET)
2. `http://127.0.0.1:8000/tasks?date=2024-11-22` - Filter out tasks by date (GET)
3. `http://127.0.0.1:8000/tasks` - Gets a list of tasks (GET)
4. `http://127.0.0.1:8000/stats?from=2024-11-23&to=2024-11-23` - Returns the average execution time of tasks between the given date range. (GET)
5. `http://127.0.0.1:8000/tasks/schedule` - Can manually Schedule a Task (POST).
6. `http://127.0.0.1:8000/tasks/execute` - Can manually Execute a Task (POST). 

## Logging

The application uses logging to capture important events, including:
- Task scheduling and execution.
- Errors while processing tasks.
- API requests and responses.

