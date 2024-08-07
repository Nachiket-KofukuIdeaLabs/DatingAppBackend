import streamlit as st
import requests
import pandas as pd

backend_url = "http://127.0.0.1:8000"

st.title("Dating App")

# Input field to specify the number of users to scrape
num_users = st.number_input("Number of users to scrape", min_value=1, step=1)
if st.button("Fetch Users"):
    response = requests.post(f"{backend_url}/fetch-users/?num_users={num_users}")
    if response.status_code == 200:
        st.success("Users fetched and stored successfully")
    else:
        st.error("Failed to fetch users")

# Button to get a random user
if st.button("Get Random User"):
    response = requests.get(f"{backend_url}/random-user/")
    if response.status_code == 200:
        user = response.json()
        st.write(user)
    else:
        st.error("Failed to fetch random user")

# Input fields to specify the user ID and number of nearest users to fetch
uid = st.text_input("User ID")
nearest_users_count = st.number_input("Number of nearest users to fetch", min_value=1, step=1)
if st.button("Get Nearest Users"):
    response = requests.get(f"{backend_url}/nearest-users/?uid={uid}&num_users={nearest_users_count}")
    if response.status_code == 200:
        users = response.json()
        for user in users:
            st.write(user)
            st.map(pd.DataFrame([[user['latitude'], user['longitude']]], columns=['lat', 'lon']))
    else:
        st.error("Failed to fetch nearest users")
