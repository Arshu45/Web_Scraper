from celery import Celery
from celery.schedules import crontab
from config import CELERY_BROKER_URL


celery_app = Celery('tasks', broker=CELERY_BROKER_URL)


celery_app.conf.beat_schedule = {
    "schedule_daily_task": {
        "task": "app.scheduler.schedule_daily_task",
        "schedule": crontab(hour=0, minute=52),
    },
    "execute_task": {
        "task": "app.executor.execute_task",
        "schedule": crontab(minute="*/5"),
    }, 
    "cleanup_old_data": {
        "task": "app.executor.cleanup_old_data",
        "schedule": crontab(hour=0, minute=0),  
    },
}


# Celery Configurations
celery_app.conf.update(
    # timezone='UTC',
    # enable_utc=True,
    timezone='Asia/Kolkata', 
    enable_utc=False ,         
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks to prevent memory leaks
    task_time_limit=300,  # Sets a timeout for tasks
)


import app.executor  
import app.scheduler  
