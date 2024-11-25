from datetime import date
from uuid import uuid4
from app.database import SessionLocal
from app.models import Task
import logging
from app.celery import celery_app

# congiguring logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This function Schedules a daily task by adding an entry in the `tasks` table with the status 'SCHEDULED'.
@celery_app.task 
def schedule_daily_task():
    
    session = SessionLocal()
    try:
        run_id = str(uuid4())
        task = Task(run_id=run_id, date=date.today(), status="SCHEDULED")
        session.add(task)
        session.commit()
        logger.info(f"Task scheduled successfully with run_id: {run_id}")
    except Exception as e:
        logger.error(f"Error scheduling task: {e}")
    finally:
        session.close()
