from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db import SessionLocal
from app.models.location import Location

router = APIRouter(prefix="/locations", tags=["locations"])

class LocationCreate(BaseModel):
    location_name: str
    description: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def add_location(location_data: LocationCreate, db: Session = Depends(get_db)):
    existing = db.query(Location).filter(Location.name == location_data.location_name).first()
    if existing:
        return {
            "message": "Location already exists",
            "location_id": existing.location_id,
            "location_name": existing.name,
            "description": existing.description or ""
        }

    location = Location(name=location_data.location_name, description=location_data.description)
    db.add(location)
    db.commit()
    db.refresh(location)

    return {
        "message": "Location added",
        "location_id": location.location_id,
        "location_name": location.name,
        "description": location.description or ""
    }

@router.get("/search")
def search_location(location_name: str, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.name == location_name).first()
    if not location:
        return {"error": "Location not found"}
    return {
        "location_id": location.location_id,
        "location_name": location.name,
        "description": location.description or ""
    }

@router.get("/all")
def list_locations(db: Session = Depends(get_db)):
    """Return all locations for dropdowns and list views."""
    locations = db.query(Location).all()
    if not locations:
        return {"message": "No locations found"}
    return [
        {
            "location_id": loc.location_id,
            "location_name": loc.name,
            "description": loc.description or ""
        }
        for loc in locations
    ]

@router.get("/print")
def print_locations(db: Session = Depends(get_db)):
    locations = db.query(Location).all()

    print("\n=== LOCATIONS IN DATABASE ===")
    for loc in locations:
        print(f"Location ID: {loc.location_id}, Name: {loc.name}, Description: {loc.description}")
    print("=== END LOCATIONS ===\n")
    
    return {"message": f"Printed {len(locations)} locations to backend console"}

@router.get("/{location_id}")
def get_location_by_id(location_id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.location_id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return {
        "location_id": location.location_id,
        "location_name": location.name,
        "description": location.description or ""
    }

@router.get("/resolve_id/{location_name}")
def resolve_location_id(location_name: str, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.name == location_name).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return {"location_id": location.location_id}

@router.delete("/{location_id}")
def delete_location(location_id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.location_id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(location)
    db.commit()
    return {"message": f"Location ID {location_id} deleted"}


