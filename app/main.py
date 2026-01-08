from fastapi import FastAPI
from app.db import engine
from app.models import Base

def create_app():
    app = FastAPI()

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Import and include routers
    #from app.routes import locations, boxes, inventory, parts
    from app.routes import boxes, inventory, locations, parts
    app.include_router(boxes.router)
    app.include_router(inventory.router)
    app.include_router(locations.router)
    app.include_router(parts.router)

    return app
