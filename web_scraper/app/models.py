from sqlalchemy import Column, String, Date, DateTime, Text, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    run_id = Column(String(120), primary_key=True)
    date = Column(Date)
    status = Column(String(30))
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)

class LegitimateSeller(Base):
    __tablename__ = 'legitimate_sellers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    site = Column(String(100))
    ssp_domain_name = Column(String(200))
    publisher_id = Column(String(200))
    relationship = Column(String(50))
    date = Column(Date)
    run_id = Column(String(120), ForeignKey('tasks.run_id'))
