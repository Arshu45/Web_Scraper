from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from config import DATABASE_URL

# DATABASE_URL = "postgresql://postgres:mltmorpltru@localhost:5432/web_scraper_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """
    Initialize the database, creating all tables.
    """  
    Base.metadata.create_all(bind=engine)


# Dependency injection for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
