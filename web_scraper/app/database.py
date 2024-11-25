from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from config import DATABASE_URL



engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine) # this command will create all tables


# Dependency injection for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
