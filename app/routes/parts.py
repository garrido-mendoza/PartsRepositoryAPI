from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db import SessionLocal
from app.models.part import Part

router = APIRouter(prefix="/parts", tags=["parts"])

class PartCreate(BaseModel):
    part_number: str
    description: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def add_part(part_data: PartCreate, db: Session = Depends(get_db)):
    existing = db.query(Part).filter(Part.part_number == part_data.part_number).first()
    if existing:
        return {
            "message": "Part already exists",
            "part_id": existing.part_id,
            "part_number": existing.part_number,
            "description": existing.description
        }
    part = Part(part_number=part_data.part_number, description=part_data.description)
    db.add(part)
    db.commit()
    db.refresh(part)
    return {
        "message": "Part added",
        "part_id": part.part_id,
        "part_number": part.part_number,
        "description": part.description
    }

@router.get("/search")
def search_part(part_number: str, db: Session = Depends(get_db)):
    """Lookup by part_number via query parameter (e.g. /parts/search?part_number=ABC123)."""
    part = db.query(Part).filter(Part.part_number == part_number).first()
    if not part:
        return {"error": "Part not found"}
    return {
        "part_id": part.part_id,
        "part_number": part.part_number,
        "description": part.description
    }

@router.get("/print")
def print_parts(db: Session = Depends(get_db)):
    parts = db.query(Part).all()
    print("\n=== PARTS IN DATABASE ===")
    for p in parts:
        print(f"Part ID: {p.part_id}, Number: {p.part_number}, Description: {p.description}")
    print("=== END PARTS ===\n")
    return {"message": f"Printed {len(parts)} parts to backend console"}

@router.get("/all")
def list_parts(db: Session = Depends(get_db)):
    parts = db.query(Part).all()
    return [
        {
            "part_id": p.part_id,
            "part_number": p.part_number,
            "description": p.description
        }
            for p in parts
    ]

@router.get("/{part_id}")
def get_part_by_id(part_id: int, db: Session = Depends(get_db)):
    """Lookup by integer part_id (e.g. /parts/1)."""
    part = db.query(Part).filter(Part.part_id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    return {
        "part_id": part.part_id,
        "part_number": part.part_number,
        "description": part.description
    }

@router.get("/by_number/{part_number}")
def get_part_by_number(part_number: str, db: Session = Depends(get_db)):
    """Lookup by part_number directly in path (e.g. /parts/by_number/ABC123)."""
    part = db.query(Part).filter(Part.part_number == part_number).first()
    if not part:
        return {"error": "Part not found"}
    return {
        "part_id": part.part_id,
        "part_number": part.part_number,
        "description": part.description
    }

@router.get("/resolve_id/{part_number}")
def resolve_part_id(part_number: str, db: Session = Depends(get_db)):
    """Lightweight lookup for GUI: returns part_id from part_number."""
    part = db.query(Part).filter(Part.part_number == part_number).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    return {"part_id": part.part_id}

@router.delete("/{part_id}")
def delete_part(part_id: int, db: Session = Depends(get_db)):
    """Delete a part by its ID."""
    part = db.query(Part).filter(Part.part_id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    db.delete(part)
    db.commit()
    return {"message": f"Part {part_id} deleted successfully"}
