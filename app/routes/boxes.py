from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db import SessionLocal
from app.models.box import Box
from app.models.location import Location

router = APIRouter(prefix="/boxes", tags=["boxes"])

class BoxCreate(BaseModel):
    code: str
    location_name: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def add_box(box_data: BoxCreate, db: Session = Depends(get_db)):
    # Resolve location by name
    location = db.query(Location).filter(Location.name == box_data.location_name).first()
    if not location:
        raise HTTPException(status_code=404, detail=f"Location '{box_data.location_name}' not found")

    existing = db.query(Box).filter(Box.code == box_data.code, Box.location_id == location.location_id).first()
    if existing:
        return {
            "message": "Box already exists",
            "box_id": existing.box_id,
            "code": existing.code,
            "location_name": location.name
        }

    box = Box(code=box_data.code, location_id=location.location_id)
    db.add(box)
    db.commit()
    db.refresh(box)
    return {
        "message": "Box added",
        "box_id": box.box_id,
        "code": box.code,
        "location_name": location.name
    }

@router.get("/search")
def search_box(code: str, db: Session = Depends(get_db)):
    box = db.query(Box).filter(Box.code == code).first()
    if not box:
        return {"error": "Box not found"}
    location = db.query(Location).filter(Location.location_id == box.location_id).first()
    return {
        "box_id": box.box_id,
        "code": box.code,
        "location_name": location.name if location else ""
    }

@router.get("/print")
def print_boxes(db: Session = Depends(get_db)):
    boxes = db.query(Box).all()

    print("\n=== BOXES IN DATABASE ===")
    for b in boxes:
        location = db.query(Location).filter(Location.location_id == b.location_id).first()
        loc_name = location.name if location else "Unknown"
        print(f"Box ID: {b.box_id}, Code: {b.code}, Location: {loc_name}")
    print("=== END BOXES ===\n")

    return {"message": f"Printed {len(boxes)} boxes to backend console"}

@router.get("/{box_id}")
def get_box_by_id(box_id: int, db: Session = Depends(get_db)):
    box = db.query(Box).filter(Box.box_id == box_id).first()
    if not box:
        raise HTTPException(status_code=404, detail="Box not found")
    location = db.query(Location).filter(Location.location_id == box.location_id).first()
    return {
        "box_id": box.box_id,
        "code": box.code,
        "location_name": location.name if location else ""
    }

@router.delete("/{box_id}")
def delete_box(box_id: int, db: Session = Depends(get_db)):
    box = db.query(Box).filter(Box.box_id == box_id).first()
    if not box:
        raise HTTPException(status_code=404, detail="Box not found")
    db.delete(box)
    db.commit()
    return {"message": f"Box ID {box_id} deleted"}
