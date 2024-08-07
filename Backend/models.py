from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
import requests
from .database import User
import datetime

# Fetch users from the randomuser API and store them in the database
def fetch_and_store_users(db: Session, num_users: int, run_id: int):
    response = requests.get(f'https://randomuser.me/api/?results={num_users}')
    users_data = response.json()['results']
    
    for user_data in users_data:
        user = User(
            email=user_data['email'],
            first_name=user_data['name']['first'],
            last_name=user_data['name']['last'],
            gender=user_data['gender'],
            latitude=float(user_data['location']['coordinates']['latitude']),
            longitude=float(user_data['location']['coordinates']['longitude']),
            run_id=run_id,
            ingestion_time=datetime.datetime.utcnow()
        )
        db.add(user)
    db.commit()

# Get a random user from the database
def get_random_user(db: Session):
    return db.query(User).order_by(func.random()).first()

# Get the nearest users to a specified user
def get_nearest_users(db: Session, uid: int, num_users: int):
    user = db.query(User).filter(User.uid == uid).first()
    if not user:
        return []
    
    users = db.query(User).filter(User.uid != uid).all()
    users.sort(key=lambda x: haversine_distance(user.latitude, user.longitude, x.latitude, x.longitude))
    return users[:num_users]

# Calculate the haversine distance between two points (latitude and longitude)
def haversine_distance(lat1, lon1, lat2, lon2):
    from math import radians, cos, sin, sqrt, atan2
    R = 6371.0
    lat1, lon1, lat2, lon2 = radians(lat1), radians(lon1), radians(lat2), radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance
