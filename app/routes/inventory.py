from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone

from app.db import SessionLocal
from app.models.part import Part
from app.models.location import Location
from app.models.box import Box
from app.models.inventory import InventoryItem

# Prefix ensures routes mount at /inventory
router = APIRouter(prefix="/inventory", tags=["inventory"])

class InventoryCreate(BaseModel):
    box_id: str
    part_number: str
    description: str
    location_name: str
    quantity: int

class InventoryUpdate(BaseModel):
    part_number: str
    description: str
    quantity: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def add_inventory(item_data: InventoryCreate, db: Session = Depends(get_db)):
    # Resolve Part
    part = db.query(Part).filter(Part.part_number == item_data.part_number).first()
    if not part:
        raise HTTPException(status_code=404, detail=f"Part '{item_data.part_number}' not found")

    # Resolve Location
    location = db.query(Location).filter(Location.name == item_data.location_name).first()
    if not location:
        raise HTTPException(status_code=404, detail=f"Location '{item_data.location_name}' not found")

    # Ensure Box exists for this Location with given code
    box = db.query(Box).filter(Box.code == item_data.box_id, Box.location_id == location.location_id).first()
    if not box:
        box = Box(code=item_data.box_id, location_id=location.location_id,
                  created_at=datetime.now(timezone.utc))
        db.add(box)
        db.commit()
        db.refresh(box)

    # Check if inventory already exists for this part in this box
    existing = db.query(InventoryItem).filter(
        InventoryItem.box_id == box.box_id,
        InventoryItem.part_number == part.part_number
    ).first()
    if existing:
        return {
            "message": "Inventory item already exists",
            "inventory_id": existing.item_id,
            "box_id": box.code,
            "part_number": existing.part_number,
            "description": existing.description,
            "location_name": location.name,
            "quantity": existing.quantity
        }

    # Create new inventory item
    item = InventoryItem(
        box_id=box.box_id,
        part_number=item_data.part_number,
        description=item_data.description,
        quantity=item_data.quantity,
        updated_at=datetime.now(timezone.utc)
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "message": "Inventory item added",
        "inventory_id": item.item_id,
        "box_id": box.code,
        "part_number": item.part_number,
        "description": item.description,
        "location_name": location.name,
        "quantity": item.quantity
    }

@router.put("/{item_id}")
def update_inventory(item_id: int, update_data: InventoryUpdate, db: Session = Depends(get_db)):
    item = db.query(InventoryItem).filter(InventoryItem.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    # Update fields
    item.part_number = update_data.part_number  # type: ignore
    item.description = update_data.description  # type: ignore
    item.quantity = update_data.quantity  # type: ignore
    item.updated_at = datetime.now(timezone.utc)  # type: ignore
    db.commit()
    db.refresh(item)
    return {
        "message": "Inventory updated",
        "inventory_id": item.item_id,
        "box_id": item.box_id,
        "part_number": item.part_number,
        "description": item.description,
        "new_quantity": item.quantity
    }

@router.get("/search")
def search_inventory(part_number: str, db: Session = Depends(get_db)):
    """Search inventory by part_number (query param)."""
    items = db.query(InventoryItem).filter(InventoryItem.part_number == part_number).all()
    if not items:
        return {"message": f"No inventory found for part_number '{part_number}'"}
    results = []
    for i in items:
        box = db.query(Box).filter(Box.box_id == i.box_id).first()
        location = db.query(Location).filter(Location.location_id == box.location_id).first() if box else None
        results.append({
            "inventory_id": i.item_id,
            "box_id": box.code if box else "",
            "part_number": i.part_number,
            "description": i.description,
            "location_name": location.name if location else "",
            "quantity": i.quantity
        })
    return results

@router.get("/search_by_box/{box_code}")
def search_inventory_by_box(box_code: str, db: Session = Depends(get_db)):
    """Search inventory by box_code (string)."""
    box = db.query(Box).filter(Box.code == box_code).first()
    if not box:
        return {"message": f"No box found with code '{box_code}'"}
    items = db.query(InventoryItem).filter(InventoryItem.box_id == box.box_id).all()
    if not items:
        return {"message": f"No inventory found for box '{box_code}'"}
    results = []
    for i in items:
        location = db.query(Location).filter(Location.location_id == box.location_id).first()
        results.append({
            "inventory_id": i.item_id,
            "box_id": box.code,
            "part_number": i.part_number,
            "description": i.description,
            "location_name": location.name if location else "",
            "quantity": i.quantity
        })
    return results

@router.delete("/{inventory_id}")
def delete_inventory(inventory_id: int, db: Session = Depends(get_db)):
    item = db.query(InventoryItem).filter(InventoryItem.item_id == inventory_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    db.delete(item)
    db.commit()
    return {"message": f"Inventory ID {inventory_id} deleted"}
