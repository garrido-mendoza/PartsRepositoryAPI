from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db import Base

class Part(Base):
    __tablename__ = "parts"

    part_id = Column(Integer, primary_key=True, index=True)
    part_number = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
