import streamlit as st
import os
from PIL import Image
import base64

from auth import authenticate
from dashboards.facility import render_facility_dashboard
from dashboards.country import render_country_dashboard
from dashboards.international import render_international_dashboard

# API Token from environment variable (fallback to default value)
API_TOKEN = os.getenv("API_TOKEN", "EF688B6DD205E120D282B5639450C6AC")


def load_custom_styles():
    """Load custom styles from an external CSS file."""
    css_file_path = "assets/styles.css"
    with open(css_file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)



def main():
    
    # Initialize session state attributes
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None

    # Set page configuration based on login state
    if not st.session_state.logged_in:
        # Login page uses centered layout
        st.set_page_config(
            page_title="VODAN ANC Dashboard",
            page_icon="/home/dhc/dashboard/assets/logo.png",
            layout="centered",
            initial_sidebar_state="expanded"
        )
    else:
        # Dashboard uses wide layout
        st.set_page_config(
            page_title="VODAN ANC Dashboard",
            page_icon="/home/dhc/dashboard/assets/logo.png",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    load_custom_styles()
    
    if not st.session_state.logged_in:
        render_logo(sidebar=False)  # Logo on main content bar
    else:
        render_logo(sidebar=True)   # Logo on sidebar

    

    # Render appropriate content based on login state
    if st.session_state.logged_in and st.session_state.user:
        render_dashboard()
    else:
        login_form()


def login_form():
    """Render the login form."""
    st.title("ANC Dashboard Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = authenticate(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.success(f"Welcome, {user['name']}!")
        else:
            st.error("Invalid username or password!")


def logout():
    """Log out the user."""
    st.session_state.logged_in = False
    st.session_state.user = None
    #st.experimental__return()
    st.sidebar.success("You have been logged out.")
    


def render_dashboard():
    """Render the dashboard based on user role."""
    user = st.session_state.user
    
    col1, col2 = st.sidebar.columns([2, 1])  # Split sidebar into two columns

    with col1:
        st.markdown(
            f"""
            <div class="logged-in-text">
                Logged in as: <strong>{user['name']}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("Logout"):
            logout()
    
 
    #st.sidebar.success(f"Logged in as: {user['name']} ({user['role']})")
    #st.sidebar.markdown(
    #    f"""
    #    <div class="logged-in-container">
    #        <span class="logged-in-text">Logged in as: {user['name']}</span>
    #        <button class="logout-button" onclick="logout()">Logout</button>
    #    </div>
    #    """,
    #    unsafe_allow_html=True,
    #)
    # Logout button
    #if st.sidebar.button("Logout"):
    #    logout()

    # Role-based dashboard rendering
    dashboards = {
        "facility": render_facility_dashboard,
        "country": render_country_dashboard,
        "international": render_international_dashboard
    }

    dashboard_func = dashboards.get(user["role"])
    if dashboard_func:
        dashboard_func(user, API_TOKEN)
    else:
        st.error("Unknown role. Please contact the administrator.")


def render_logo(sidebar=False):
    """Render the logo either in the main content bar (larger) or the sidebar (smaller)."""
    with open("assets/logo.png", "rb") as img_file:
        encoded_img = base64.b64encode(img_file.read()).decode()

    if sidebar:
        # Smaller size for the sidebar
        logo_html = f"""
            <div class="logo-container" style="text-align: center; width: 100%; margin-bottom: 20px;">
                <img src="data:image/jpeg;base64,{encoded_img}" alt="Dashboard Logo" style="width: 100%; max-width: 300px;">
            </div>
        """
        st.sidebar.markdown(logo_html, unsafe_allow_html=True)
    else:
        # Larger size for the main content
        logo_html = f"""
            <div class="logo-container" style="text-align: center; width: 100%; margin-bottom: 20px;">
                <img src="data:image/jpeg;base64,{encoded_img}" alt="Dashboard Logo" style="width: 100%; max-width: 600px;">
            </div>
        """
        st.markdown(logo_html, unsafe_allow_html=True)
###
def add_footer():
    st.markdown(
        """
        <div class="custom-footer">
            VODAN Africa
        </div>
        """,
        unsafe_allow_html=True,
    )

#add_footer()

if __name__ == "__main__":
    main()
