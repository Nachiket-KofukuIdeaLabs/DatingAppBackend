from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    gender: str
    latitude: float
    longitude: float
    run_id: int
    ingestion_time: datetime
