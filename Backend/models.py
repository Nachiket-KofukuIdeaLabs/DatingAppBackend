from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from .database import User

# Calculate the haversine distance between two points (latitude and longitude)
def haversine_distance(lat1, lon1, lat2, lon2):
    from math import radians, cos, sin, sqrt, atan2
    R = 6371.0  # Radius of Earth in kilometers
    lat1, lon1, lat2, lon2 = radians(lat1), radians(lon1), radians(lat2), radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

# Get the nearest users to a specified user
def get_nearest_users(db: Session, uid: int, num_users: int):
    user = db.query(User).filter(User.uid == uid).first()
    if not user:
        return []

    # Fetch all users except the specified user
    users = db.query(User).filter(User.uid != uid).all()
    
    # Calculate distances and sort users
    users_with_distance = [
        {
            'user': u,
            'distance': haversine_distance(user.latitude, user.longitude, u.latitude, u.longitude)
        }
        for u in users
    ]
    
    # Sort users by distance
    sorted_users = sorted(users_with_distance, key=lambda x: x['distance'])

    # Get the nearest 'num_users' users
    nearest_users = sorted_users[:num_users]

    return [u['user'] for u in nearest_users]