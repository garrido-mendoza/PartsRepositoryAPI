from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db import Base

class Box(Base):
    __tablename__ = "boxes"

    box_id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)  # Equivalent to D4 in VBA
    location_id = Column(Integer, ForeignKey("locations.location_id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship to Location
    location = relationship("Location", back_populates="boxes")

    # Relationship to InventoryItem
    inventory = relationship(
        "InventoryItem",
        back_populates="box",
        cascade="all, delete-orphan"
    )
