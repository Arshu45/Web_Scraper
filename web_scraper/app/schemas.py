from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class TaskResponse(BaseModel):
    run_id: str
    date: date
    status: str
    error: Optional[str]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    failed_at: Optional[datetime]

    class Config:
        from_attributes = True  


class LegitimateSellerResponse(BaseModel):
    id: int
    site: str
    ssp_domain_name: str
    publisher_id: str
    relationship: str
    date: date
    run_id: str

    class Config:
        from_attributes = True  


# Add this for parsing ads.txt entries
class AdsTxtEntry(BaseModel):
    ssp_domain_name: str
    publisher_id: str
    relationship: str
    tag_id: Optional[str] = None
