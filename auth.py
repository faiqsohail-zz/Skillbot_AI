import streamlit as st
import pandas as pd
import os

USER_FILE = "users.csv"

# Create user file if not exists
if not os.path.exists(USER_FILE):
    pd.DataFrame(columns=["username", "password"]).to_csv(USER_FILE, index=False)

def signup(username, password):
    users = pd.read_csv(USER_FILE)
    if username in users["username"].values:
        st.error("Username already exists. Try signing in.")
        return False
    else:
        new_user = pd.DataFrame({"username": [username], "password": [password]})
        new_user.to_csv(USER_FILE, mode='a', header=False, index=False)
        st.success("Signup successful! Please sign in now.")
        return True

def login(username, password):
    users = pd.read_csv(USER_FILE)
    if username in users["username"].values:
        stored_pw = users.loc[users["username"] == username, "password"].values[0]
        if stored_pw == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success(f"Welcome back, {username}!")
            return True
        else:
            st.error("Incorrect password.")
    else:
        st.error("User not found. Please sign up first.")
    return False
