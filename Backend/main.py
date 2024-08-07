from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from .database import SessionLocal, engine, User
from .models import fetch_and_store_users, get_random_user, get_nearest_users

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to fetch users from the randomuser API and store them in the database
@app.post("/fetch-users/")
def fetch_users(num_users: int, db: Session = Depends(get_db)):
    run_id = db.query(User).count() // num_users + 1
    fetch_and_store_users(db, num_users, run_id)
    return {"status": "Users fetched and stored"}

# Endpoint to get a random user from the database
@app.get("/random-user/")
def random_user(db: Session = Depends(get_db)):
    user = get_random_user(db)
    if not user:
        raise HTTPException(status_code=404, detail="No users found")
    return user

# Endpoint to get the nearest users to a specified user
@app.get("/nearest-users/")
def nearest_users(uid: int, num_users: int, db: Session = Depends(get_db)):
    users = get_nearest_users(db, uid, num_users)
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users
