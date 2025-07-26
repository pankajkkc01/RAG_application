import sys
import os

# Add the /api folder to Python path
api_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api"))
sys.path.append(api_path)

import streamlit as st
from chat_interface import display_chat_interface
from PIL import Image
import requests
from db_utils import is_user_allowed

#from db_utils import is_user_allowed 

# ---------------- SESSION STATE INIT ---------------- #
if "is_logged_in" not in st.session_state:
    st.session_state["is_logged_in"] = False

# ---------------- LOGIN FUNCTION ---------------- #
def show_login():
    st.markdown("""
        <style>
            .login-header {
                text-align: center;
                margin-top: 40px;
                margin-bottom: 20px;
            }
            .login-header h1 {
                font-size: 36px;
                color: #ffffff;
                font-weight: 800;
                margin-bottom: 8px;
            }
            .login-header p {
                font-size: 16px;
                color: #dddddd;
                font-weight: 400;
            }
            input[type="text"], input[type="email"], input[type="tel"] {
                background-color: transparent !important;
                color: #ffffff !important;
                border: none !important;
                border-bottom: 1.5px solid #999 !important;
                border-radius: 0 !important;
                font-size: 16px !important;
            }
            label {
                color: #dddddd !important;
                font-size: 14px !important;
                font-weight: 600;
            }
            .stButton > button {
                background-color: #4a90e2;
                color: white;
                padding: 10px 22px;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 600;
                margin-top: 20px;
                transition: background-color 0.2s ease;
            }
            .stButton > button:hover {
                background-color: #3a78c2;
            }
            div[data-testid="stForm"] {
                background-color: transparent !important;
                border: none !important;
                box-shadow: none !important;
                padding: 0 !important;
            }
        </style>
        <div class="login-header">
            <h1>Welcome to BLUgo</h1>
            <p>Your AI-powered business advisor</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        st.markdown("#### Log in to continue")
        name = st.text_input("Full Name")
        email = st.text_input("Gmail ID")
        phone = st.text_input("Phone Number")

        submit = st.form_submit_button("Log In")

        if submit:
            if name and email and phone:
                if is_user_allowed(name, email, phone):
                    st.session_state["is_logged_in"] = True
                    st.session_state["user_info"] = {
                        "name": name,
                        "email": email,
                        "phone": phone
                    }
                    try:
                        requests.post("http://localhost:8000/log-user", json={
                            "name": name,
                            "email": email,
                            "phone": phone
                        })
                    except:
                        st.warning("⚠️ Couldn't connect to backend for user logging.")
                    st.success(f"✅ Welcome, {name}! You're now logged in.")
                else:
                    st.error("🚫 Access Denied: Your credentials were not found in our records.")
            else:
                st.warning("🚫 Please fill in all fields.")

# ---------------- MAIN APP FUNCTION ---------------- #
def run_main_app():
    st.title("BLUgo")

    # Centered logo
    st.markdown("<h3 style='text-align: center;'></h3>", unsafe_allow_html=True)
    image = Image.open("logo2.png")
    st.image(image, width=100, use_container_width=True)

    st.markdown("### 👋 Welcome to BLUgo – Your AI Business Coach")
    st.markdown("Ask anything about growing your business. I'm here to help you.")

    # Initialize session state variables
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "session_id" not in st.session_state:
        st.session_state.session_id = None

    if "model" not in st.session_state:
        st.session_state["model"] = "gpt-4o"  # Default model

    # Display the chat interface
    display_chat_interface()

# ---------------- ENTRY POINT ---------------- #
if not st.session_state["is_logged_in"]:
    show_login()
else:
    run_main_app()
