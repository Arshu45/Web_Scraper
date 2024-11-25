import json
import requests
from datetime import datetime, date, timedelta
from app.database import SessionLocal
from app.models import Task, LegitimateSeller
from app.schemas import AdsTxtEntry
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.celery import celery_app


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_ads_txt(content):

    for line in content.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        fields = line.split(",")
        try:
            yield AdsTxtEntry(
                ssp_domain_name=fields[0].strip(),
                publisher_id=fields[1].strip(),
                relationship=fields[2].strip(),
                tag_id=fields[3].strip() if len(fields) > 3 else None
            )
        except Exception as e:
            logger.warning(f"Error parsing line '{line}': {e}")

@celery_app.task
def execute_task():
    session = SessionLocal()
    task = session.query(Task).filter(Task.status == "SCHEDULED").first()
    if not task:
        session.close()
        logger.info("No scheduled tasks found.")
        return

    task.status = "STARTED"
    task.started_at = datetime.now()
    session.commit()

    try:
        with open('sites.json', 'r') as file:
            sites = json.load(file)["sites"]

        for site in sites:
            url = f"https://{site}/ads.txt"
            logger.info(f"Fetching ads.txt from: {url}")  
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                logger.info(f"Successfully fetched data from {url}")

                for entry in parse_ads_txt(response.text):
                    seller = LegitimateSeller(
                        site=site,
                        ssp_domain_name=entry.ssp_domain_name,
                        publisher_id=entry.publisher_id,
                        relationship=entry.relationship,
                        date=date.today(),
                        run_id=task.run_id
                    )
                    session.add(seller)
                logger.info(f"Processed ads.txt for site: {site}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch ads.txt for site {site}: {e}")
            except Exception as e:
                logger.error(f"Error processing ads.txt for site {site}: {e}")

        task.status = "FINISHED"
        task.finished_at = datetime.now()
        logger.info(f"Task {task.run_id} finished successfully.")
    except Exception as e:
        task.status = "FAILED"
        task.error = str(e)
        task.failed_at = datetime.now()
        logger.error(f"Task {task.run_id} failed with error: {e}")
    finally:
        try:
            session.commit()
        except SQLAlchemyError as db_error:
            logger.error(f"Database commit failed: {db_error}")
        session.close()





@celery_app.task
def cleanup_old_data():
    
    session = SessionLocal()
    try:
        
        cutoff_time = datetime.now() - timedelta(hours=24)

        # Delete old records from the legitimate_sellers table
        sellers_deleted = session.query(LegitimateSeller).filter(LegitimateSeller.date < cutoff_time.date()).delete()
        logger.info(f"Deleted {sellers_deleted} entries from legitimate_sellers.")

        # Delete old records from the tasks table
        tasks_deleted = session.query(Task).filter(Task.date < cutoff_time.date()).delete()
        logger.info(f"Deleted {tasks_deleted} entries from tasks.")

        session.commit()
    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")
    finally:
        session.close()