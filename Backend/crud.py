import requests
from datetime import datetime
from math import radians, cos, sin, sqrt, atan2
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User

def haversine_distance(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return None
    
    R = 6371.0  # Radius of Earth in kilometers
    lat1, lon1, lat2, lon2 = radians(lat1), radians(lon1), radians(lat2), radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

def fetch_and_store_users(db: Session, num_users: int, run_id: int):
    url = f"https://randomuser.me/api/?results={num_users}"
    response = requests.get(url)
    users = response.json().get("results", [])
    
    for user_data in users:
        coordinates = user_data.get("location", {}).get("coordinates", {})
        latitude = coordinates.get("latitude")
        longitude = coordinates.get("longitude")

        try:
            latitude = float(latitude) if latitude is not None else None
            longitude = float(longitude) if longitude is not None else None
        except (ValueError, TypeError):
            latitude = None
            longitude = None

        if latitude is None or longitude is None:
            continue

        user = User(
            email=user_data.get("email"),
            first_name=user_data.get("name", {}).get("first"),
            last_name=user_data.get("name", {}).get("last"),
            gender=user_data.get("gender"),
            latitude=latitude,
            longitude=longitude,
            run_id=run_id,
            ingestion_time=datetime.utcnow(),
        )
        db.add(user)
    db.commit()

def get_random_user(db: Session):
    return db.query(User).order_by(func.random()).first()

def get_nearest_users(db: Session, uid: int, num_users: int):
    user = db.query(User).filter(User.uid == uid).first()
    if not user:
        raise ValueError(f"No user found with UID {uid}")

    users = db.query(User).filter(
        User.uid != uid,
        User.latitude.isnot(None),
        User.longitude.isnot(None)
    ).all()

    users_with_distance = []
    for u in users:
        distance = haversine_distance(user.latitude, user.longitude, u.latitude, u.longitude)
        if distance is not None:
            users_with_distance.append({'user': u, 'distance': distance})
    
    sorted_users = sorted(users_with_distance, key=lambda x: x['distance'])

    nearest_users = sorted_users[:num_users]

    if not nearest_users:
        raise ValueError("No nearest users found")

    return [u['user'] for u in nearest_users]
