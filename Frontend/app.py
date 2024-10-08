import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.title("Dating App User Finder")

# Fetch and Store Users
st.header("Fetch Users")
num_users = st.number_input("Number of users to fetch:", min_value=1, value=10)
if st.button("Fetch Users"):
    response = requests.post(f"http://127.0.0.1:8000/fetch-users/", params={"num_users": num_users})
    if response.status_code == 200:
        st.success("Users fetched and stored successfully!")
    else:
        st.error(f"Error fetching users: {response.text}")

# Fetch Random User
st.header("Get Random User")
if st.button("Fetch Random User"):
    response = requests.get(f"http://127.0.0.1:8000/random-user/")
    if response.status_code == 200:
        user = response.json()
        st.session_state["random_user"] = user
    else:
        st.error(f"Error fetching random user: {response.text}")

# Display Random User if available
if "random_user" in st.session_state:
    user = st.session_state["random_user"]
    st.header("Current Random User")
    st.write(f"Random User: {user['first_name']} {user['last_name']}")
    st.write(f"Email: {user['email']}")
    st.write(f"Gender: {user['gender']}")
    st.write(f"Coordinates: ({user['latitude']}, {user['longitude']})")

    # Get Nearest Users
    st.header("Get Nearest Users")
    num_nearest_users = st.number_input("Number of nearest users to fetch:", min_value=1, value=10)
    if st.button("Find Nearest Users"):
        uid = user.get("uid")
        if uid is None:
            st.error("UID is missing from the random user data.")
        else:
            response = requests.get(f"http://127.0.0.1:8000/nearest-users/", params={"uid": uid, "num_users": num_nearest_users})
            if response.status_code == 200:
                nearest_users = response.json()
                st.write(f"Found {len(nearest_users)} nearest users.")
                if nearest_users:
                    # Create the map centered on the random user's location
                    m = folium.Map(location=[user["latitude"], user["longitude"]], zoom_start=10)
                    # Add marker for the random user
                    folium.Marker(
                        [user["latitude"], user["longitude"]],
                        tooltip="Random User",
                        icon=folium.Icon(color="darkpurple")
                    ).add_to(m)
                    # Add markers for the nearest users
                    for u in nearest_users:
                        folium.Marker(
                            [u["latitude"], u["longitude"]],
                            tooltip=f"{u['first_name']} {u['last_name']}",
                            icon=folium.Icon(color="red")
                        ).add_to(m)
                    # Render the map
                    st_folium(m, width=700, height=500, returned_objects=['map'])
                else:
                    st.write("No nearest users found.")
            else:
                st.error(f"Error fetching nearest users: {response.text}")
else:
    st.write("Fetch a random user first.")
