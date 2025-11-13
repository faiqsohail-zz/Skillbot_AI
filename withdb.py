import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from io import BytesIO
import json

# --- SUPABASE CONFIG ---
SUPABASE_URL = "https://jaztokuyzxettemexcrc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImphenRva3V5enhldHRlbWV4Y3JjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI5NTU4OTMsImV4cCI6MjA3ODUzMTg5M30.I7Q-fAKRqYFzsJoyt7jQD1Vm1eB0sQKo17-ikA5VFBY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(page_title="SkillBot Personality Profiler", layout="wide")

# --- SESSION STATE ---
if "user" not in st.session_state:
    st.session_state.user = None
if "test_result" not in st.session_state:
    st.session_state.test_result = None

# --- AUTH FUNCTIONS ---
def signup(email, password):
    return supabase.auth.sign_up({"email": email, "password": password})

def login(email, password):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

def logout():
    st.session_state.user = None
    st.session_state.test_result = None

# --- PROFILE CREATION ---
def create_profile(user_id):
    st.subheader("👤 Create Your Profile")
    full_name = st.text_input("Full Name")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    age = st.number_input("Age", min_value=10, max_value=100, step=1)
    qualification = st.selectbox(
        "Qualification Level", ["Matric", "Intermediate", "Bachelors", "Masters", "PhD"]
    )
    marksheet = st.file_uploader("Upload Marksheet (image/pdf)", type=["jpg", "jpeg", "png", "pdf"])

    if st.button("Save Profile"):
        marksheet_url = None
        if marksheet:
            file_bytes = marksheet.read()
            filename = f"{user_id}_{marksheet.name}"
            res = supabase.storage.from_("marksheets").upload(filename, file_bytes)
            marksheet_url = supabase.storage.from_("marksheets").get_public_url(filename)
        
        supabase.table("profiles").upsert({
            "id": user_id,
            "full_name": full_name,
            "gender": gender,
            "age": age,
            "qualification": qualification,
            "marksheet_url": marksheet_url
        }).execute()
        st.success("✅ Profile saved successfully!")

# --- TEST SIMULATION (replace with your logic) ---
def conduct_test():
    st.subheader("🧠 Conduct Your Personality Test")
    q1 = st.slider("I enjoy working in teams", 1, 5, 3)
    q2 = st.slider("I stay calm under pressure", 1, 5, 3)
    q3 = st.slider("I like solving complex problems", 1, 5, 3)
    if st.button("Submit Test"):
        score = (q1 + q2 + q3) / 3 * 20
        st.session_state.test_result = {"score": score, "details": {"q1": q1, "q2": q2, "q3": q3}}
        st.success(f"Your score: {score:.2f}")
        st.session_state.page = "dashboard"

# --- DASHBOARD ---
def show_dashboard():
    result = st.session_state.test_result
    st.subheader("📊 Personality Dashboard")
    df = pd.DataFrame([result["details"]])
    fig = px.bar(df, title="Your Responses")
    st.plotly_chart(fig, use_container_width=True)

    st.info(f"Overall Personality Score: {result['score']:.2f}")

    if st.button("Do You Want More Personalized Results?"):
        if st.session_state.user:
            create_profile(st.session_state.user.id)
        else:
            st.session_state.page = "auth"

# --- SAVE TEST RESULTS ---
def save_result_to_db(user_id, result):
    supabase.table("test_results").insert({
        "user_id": user_id,
        "score": result["score"],
        "details": json.dumps(result["details"])
    }).execute()

# --- AUTH UI ---
def auth_ui():
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            res = login(email, password)
            if res.user:
                st.session_state.user = res.user
                st.success("✅ Logged in successfully!")
    with tab2:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Sign Up"):
            res = signup(email, password)
            if res.user:
                st.session_state.user = res.user
                st.success("✅ Account created successfully!")

# --- APP FLOW CONTROLLER ---
if "page" not in st.session_state:
    st.session_state.page = "test"

st.title("🎯 SkillBot Personality Profiler")

if st.session_state.page == "test":
    conduct_test()
elif st.session_state.page == "dashboard":
    show_dashboard()
elif st.session_state.page == "auth":
    auth_ui()
    if st.session_state.user and st.session_state.test_result:
        save_result_to_db(st.session_state.user.id, st.session_state.test_result)
        st.success("✅ Test results saved to your account!")
        create_profile(st.session_state.user.id)
elif st.session_state.page == "profile":
    create_profile(st.session_state.user.id)

if st.session_state.user:
    if st.button("Logout"):
        logout()
        st.session_state.page = "test"
