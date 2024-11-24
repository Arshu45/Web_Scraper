from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from app.database import get_db
from app.models import Task, LegitimateSeller
from app.schemas import TaskResponse, LegitimateSellerResponse
from app.celery import celery_app  # Import the centralized Celery app
from uuid import uuid4
from datetime import datetime

app = FastAPI()

@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(date: Optional[date] = None, db: Session = Depends(get_db)):
    # Now, "db" is the database session that FastAPI injected
    """
    Fetches all tasks or filters by date.
    """
    query = db.query(Task)
    if date:
        query = query.filter(Task.date == date) 
    tasks = query.all() # You can use it to query the database
    return tasks

@app.get("/legitimate_sellers", response_model=List[LegitimateSellerResponse])
def get_legitimate_sellers(domain: str, db: Session = Depends(get_db)):
    """
    Fetches legitimate sellers for a given domain.
    Raises a 404 error if no sellers are found.
    """
    sellers = db.query(LegitimateSeller).filter(LegitimateSeller.site == domain).all()
    if not sellers:
        raise HTTPException(status_code=404, detail="No sellers found")
    return sellers

@app.post("/tasks/schedule", response_model=TaskResponse)
def schedule_task(db: Session = Depends(get_db)):
    """
    Manually schedules a task by adding an entry in the `tasks` table
    and triggers the task execution using Celery.
    """
    try:
        run_id = str(uuid4())
        task = Task(run_id=run_id, date=date.today(), status="SCHEDULED")
        db.add(task)
        db.commit()
        db.refresh(task)

        # Trigger task execution using Celery
        celery_app.send_task('app.executor.execute_task')

        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule task: {e}")

@app.post("/tasks/execute", response_model=TaskResponse)
def execute_scheduled_task(db: Session = Depends(get_db)):
    """
    Manually executes the first available scheduled task.
    """
    task = db.query(Task).filter(Task.status == "SCHEDULED").first()
    if not task:
        raise HTTPException(status_code=404, detail="No scheduled tasks found to execute.")

    try:
        # Update task status to 'STARTED' and commit
        task.status = "STARTED"
        task.started_at = datetime.now()
        db.commit()
        db.refresh(task)

        # Trigger task execution using Celery
        celery_app.send_task('app.executor.execute_task')

        return task
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to execute task: {e}")


@app.get("/stats")
def get_stats(from_: date = Query(..., alias="from"), to: date = Query(..., alias="to"), db: Session = Depends(get_db)):
    """
    Returns the average execution time of tasks between the given date range.
    """
    if from_ > to:
        raise HTTPException(status_code=400, detail="from must be earlier than or equal to to.")

    # Query for tasks in the specified date range
    tasks = db.query(
        Task.started_at, Task.finished_at
    ).filter(
        Task.started_at.isnot(None),  # Ensure tasks have started
        Task.finished_at.isnot(None),  # Ensure tasks have finished
        Task.date >= from_,
        Task.date <= to
    ).all()

    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found in the specified date range.")

    # Calculate execution times
    execution_times = [
        (task.finished_at - task.started_at).total_seconds() for task in tasks
    ]
    avg_execution_time = sum(execution_times) / len(execution_times)

    return {"from_date": from_, "to_date": to, "average_execution_time_seconds": avg_execution_time}
