""" from app.db import Base, engine
from app.models.location import Location
from app.models.box import Box
from app.models.inventory_item import InventoryItem
from app.models.part import Part

# Create all tables
Base.metadata.create_all(bind=engine)
print("✅ Database tables created.") """

from sqlalchemy import event
from app.db import Base, engine
from app.models.location import Location
from app.models.box import Box
from models.inventory import InventoryItem
from app.models.part import Part

# Enable SQLite pragmas for safety and robustness
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, conn_record):
    cursor = dbapi_conn.cursor()
    # Enforce foreign key constraints (prevents orphaned records)
    cursor.execute("PRAGMA foreign_keys=ON;")
    # Use Write-Ahead Logging for safer concurrent writes
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.close()

# Create all tables
Base.metadata.create_all(bind=engine)
print("✅ Database tables created with FK enforcement and WAL mode.")
