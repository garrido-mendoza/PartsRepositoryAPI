from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.base import Base  # now cleanly imported

engine = create_engine("sqlite:///parts_inventory.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
