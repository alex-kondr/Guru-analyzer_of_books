import pathlib

import uvicorn

from fastapi import Depends, FastAPI, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from sqlalchemy import text

from src.database.db import get_db
from src.routes import auth, users, chats, files

app = FastAPI()
templates = Jinja2Templates(directory='templates')
BASE_DIR = pathlib.Path(__file__).parent

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to Guru-analyzer of books!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(chats.router, prefix="/api")
app.include_router(files.router, prefix="/api")

if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, reload=True)
