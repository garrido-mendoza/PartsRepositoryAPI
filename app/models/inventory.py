from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db import Base

class InventoryItem(Base):
    __tablename__ = "inventory"   # keep existing name to avoid breaking dependencies

    item_id = Column(Integer, primary_key=True, index=True)
    box_id = Column(Integer, ForeignKey("boxes.box_id"), nullable=False)

    part_number = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)   # ensure this column exists
    quantity = Column(Integer, nullable=False)

    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship back to Box
    box = relationship("Box", back_populates="inventory")
