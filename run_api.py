import uvicorn
from app.main import create_app

if __name__ == "__main__":
    # Start FastAPI backend
    uvicorn.run(create_app(), host="127.0.0.1", port=8000)
