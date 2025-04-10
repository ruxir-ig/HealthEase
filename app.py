# final_app_bright_stable.py
import streamlit as st # type: ignore
from streamlit_option_menu import option_menu # type: ignore
import streamlit.components.v1 as components # type: ignore # Import components
import base64
from pathlib import Path
import json
from datetime import datetime, timezone
import time
import os
from dotenv import load_dotenv # type: ignore

# --- Assuming these utility modules exist and work ---
from utils.auth import check_authentication, Auth
from utils.research_analyzer import ResearchAnalyzer
from utils.symptom_analyzer import SymptomAnalyzer
from utils.wellness_tracker import WellnessTracker
from utils.database import MongoDB, ObjectId # Ensure ObjectId is imported

load_dotenv()

# --- Page Config ---
st.set_page_config(
    page_title="HealthEase",
    layout="wide",
    initial_sidebar_state="collapsed" # Default Streamlit sidebar is not used
)

# --- Theme Configuration (BRIGHT THEME V2) ---
config = {
    "theme": {
        "primary_color": "#0B5ED7",    # Accessible Blue
        "secondary_color": "#6c757d",  # Gray
        "accent_color": "#198754",     # Green
        "light_color": "#141413",     # Very Light Blue-Gray Background
        "background_color": "#141413", # White Content Background
        "card_bg": "#141413",
        "dark_color": "#F1F5F9",      # Dark Text Color
        "font_family": "'Lato', sans-serif",
        "hero_bg_gradient": "linear-gradient(145deg, #141413 0%, #cce7ff 100%)", # Lighter Blue Gradient
    },
    "logo_path": "logo.png", # Assuming logo.png exists
    "feature_icons": { # Using simple placeholders, replace if needed
        "Research Analyzer": "📄", "Symptom Analyzer": "🩺", "Wellness Tracker": "❤️‍🩹"
    }
}

# --- Asset Loading ---
def get_base64_image(image_path):
    try:
        path = Path(image_path)
        if path.is_file():
            with open(path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
        else: print(f"Warning: Logo file not found at {image_path}"); return None
    except Exception as e: print(f"Error loading logo: {e}"); return None

logo_base64 = get_base64_image(config["logo_path"])
# Combined Logo and Text Title
logo_html = f"""
<div style="display: flex; align-items: center; padding: 5px 0;">
    {f'<img src="data:image/png;base64,{logo_base64}" style="height: 35px; margin-right: 10px;" alt="Logo">' if logo_base64 else ''}
    <span class="navbar-brand-text" style="color: {config["theme"]["primary_color"]};font-size: 1.6em; font-weight: 700;">HealthEase</span>
</div>
"""

# --- Load CSS ---
def load_css():
    # Removed Bootstrap Icons CDN for simplicity - using emojis now
    st.markdown("""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)
    css = f"""
<style>
    /* --- Theme Variables & Base (BRIGHT THEME V2) --- */
    :root {{
        --primary-color: {config['theme']['primary_color']};
        --secondary-color: {config['theme']['secondary_color']};
        --accent-color: {config['theme']['accent_color']};
        --light-color: {config['theme']['light_color']}; /* Light bg */
        --background-color: {config['theme']['background_color']}; /* White content */
        --text-color: {config['theme']['dark_color']}; /* Dark text */
        --card-bg: {config['theme']['card_bg']};
        --font-family: {config['theme']['font_family']};
        --card-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
        --border-radius: 8px;
    }}
    html {{ scroll-behavior: smooth; }} /* Add smooth scrolling */
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
        font-family: var(--font-family); color: var(--text-color);
        background-color: var(--light-color); /* Light background for whole page */
        line-height: 1.6; font-size: 16px;
    }}
    /* Hide Streamlit Defaults */
    header[data-testid="stHeader"], footer {{ display: none !important; }}
    #MainMenu {{ display: none !important; }}
    /* Reset main block container padding */
    .main .block-container {{ padding: 0 !important; max-width: none !important; margin: 0 !important; }}
    .stApp {{ background-color: var(--light-color); }} /* Apply light bg to app */

    /* --- Logged-Out Navbar (using st.columns) --- */
    /* Base style for ALL buttons in the navbar */
    .logged-out-nav .stButton>button {{
        background-color: transparent !important;
        color: var(--primary-color) !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 8px 12px !important;
        border-radius: 6px !important;
        transition: background-color 0.2s ease, color 0.2s ease;
        text-decoration: none !important;
        font-size: 1rem;
        line-height: 1.5;
        text-align: center;
        cursor: pointer;
        width: 100%;
        box-sizing: border-box;
        font-family: var(--font-family);
        vertical-align: middle; /* Helps alignment */
    }}
    /* Hover state for standard buttons */
    .logged-out-nav .stButton>button:not(.emergency-button button):hover {{
        background-color: var(--light-color) !important; /* Use theme variable */
        color: #0a58ca !important; /* Darker blue on hover */
        text-decoration: none !important; /* Keep underline off */
    }}

    /* Style specifically for the Emergency button container */
    .emergency-button-container .stButton>button {{
        background-color: #dc3545 !important; /* Red */
        color: white !important;
        border: none !important;
        font-weight: 700 !important; /* Make it bolder */
    }}
    .emergency-button-container .stButton>button:hover {{
        background-color: #D2042D !important; /* Darker red on hover */
        color: white !important;
    }}


    /* --- Hero Section --- */
    .hero-container {{
        background: {config['theme']['hero_bg_gradient']}; /* Light gradient */
        padding: 4rem 2rem 5rem 2rem; /* Adjusted padding */
        text-align: center;
        width: 100%;
        margin-bottom: 2.5rem; /* Space below hero */
    }}
    .hero-content {{ max-width: 800px; margin: 0 auto; }}
    .hero-content h1 {{
        font-size: 2.8em; font-weight: 700; margin-bottom: 1rem;
        color: var(--primary-color); /* Primary color title */
        border-bottom: none; text-shadow: none;
    }}
    .hero-content p.hero-description {{
        font-size: 1.1em; margin-bottom: 2rem;
        color: var(--text-color); /* Dark text */
        line-height: 1.7;
    }}
    .hero-buttons {{ margin-top: 1.5rem; }} /* Space for buttons */
    .stButton>button.hero-btn {{
        padding: 10px 25px !important; font-size: 1rem !important;
        border-radius: 6px !important; font-weight: 600 !important;
        transition: all 0.2s ease !important; border: none !important; min-width: 140px;
        color: white !important; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }}
    .stButton>button.hero-btn-login {{ background: var(--primary-color) !important; }}
    .stButton>button.hero-btn-login:hover {{ background: #0a58ca !important; transform: translateY(-1px); box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15); }}
    .stButton>button.hero-btn-register {{ background: var(--accent-color) !important; }}
    .stButton>button.hero-btn-register:hover {{ background: #157347 !important; transform: translateY(-1px); box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15); }}

    /* --- Logged-in Layout (using st.columns) --- */
    .app-container-logged-in {{
        display: flex;
        padding-top: 1rem; /* Space from top */
        max-width: 1400px; /* Max width for content */
        margin: 0 auto; /* Center layout */
    }}

    .content-column {{ /* Styling for the main content column */
        padding: 0 1.5rem 2rem 2.5rem; /* Padding around content */
        width: 100%; /* Take remaining width */
    }}
    /* Styles for streamlit-option-menu in LIGHT sidebar */
    .sidebar-column .nav-link {{
        color: var(--text-color) !important; /* Dark text */
        border-radius: 6px; margin-bottom: 4px;
        transition: background-color 0.2s ease, color 0.2s ease;
        padding: 10px 15px !important; font-size: 0.95rem !important;
    }}
    .sidebar-column .nav-link:hover {{
        background-color: #dee2e6 !important; /* Light gray hover */
        color: var(--primary-color) !important; /* Primary color text */
    }}
    .sidebar-column .nav-link.active {{
        background-color: var(--primary-color) !important;
        color: white !important; font-weight: 600;
    }}
    .sidebar-column i {{ /* Assuming Bootstrap Icons classes are used */
        color: var(--secondary-color); font-size: 1.1rem; vertical-align: middle;
        margin-right: 10px; transition: color 0.2s ease;
    }}
    .sidebar-column .nav-link:hover i {{ color: var(--primary-color) !important; }}
    .sidebar-column .nav-link.active i {{ color: white !important; }}

    /* Profile/Logout Area (Logged In - Top Right of Content) */
    .profile-logout-area {{
        text-align: right;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #eee;
    }}
    .profile-logout-area span {{ /* Welcome message */
        margin-right: 15px;
        font-weight: 600;
        color: var(--text-color);
        font-size: 0.95em;
    }}
    .profile-logout-area .stButton>button {{ /* Logout Button */
        background-color: transparent !important; color: var(--secondary-color) !important;
        border: 1px solid #d0d0d0 !important; padding: 5px 10px !important;
        border-radius: 15px !important; font-size: 0.85em !important;
        transition: all 0.2s ease !important;
        display: inline-block !important; /* Ensure button is inline */
        margin-left: 5px; /* Space from name */
    }}
    .profile-logout-area .stButton>button:hover {{
        background-color: #e9ecef !important; color: var(--dark-color) !important;
        border-color: #adb5bd !important;
    }}


    /* --- General Content Styling (Bright Theme) --- */
    .content-column h1, .page-container h1 {{ font-size: 2.0em; text-align: left; margin-bottom: 1.5rem; color: var(--primary-color); border-bottom: 2px solid var(--primary-color); padding-bottom: 0.5rem; font-weight: 700; }}
    .content-column h2, .page-container h2 {{ font-size: 1.6em; color: var(--dark-color); margin-top: 2rem; margin-bottom: 1rem; padding-bottom: 0.4rem; border-bottom: 1px solid #ddd; font-weight: 700; }}
    .content-column h3, .page-container h3 {{ font-size: 1.25em; color: var(--primary-color); margin-top: 1.5rem; margin-bottom: 0.8rem; font-weight: 700; }}
    .content-column h4, .page-container h4 {{ font-size: 1.05em; font-weight: 700; color: var(--text-color); margin-bottom: 0.5rem; }}
    .content-column p, .page-container p {{ margin-bottom: 1rem; color: var(--text-color); }}
    .content-column a, .page-container a {{ color: var(--primary-color); text-decoration: none; }} .content-column a:hover, .page-container a:hover {{ color: #0a58ca; text-decoration: underline; }}
    .content-column ul, .content-column ol, .page-container ul, .page-container ol {{ padding-left: 25px; margin-bottom: 1rem; color: var(--text-color); }} .content-column li, .page-container li {{ margin-bottom: 0.5rem; }}
    hr {{ border: none; border-top: 1px solid #e0e0e0; margin: 1.5rem 0; }}
    .content-card {{ background-color: var(--card-bg); padding: 25px; border-radius: var(--border-radius); box-shadow: var(--card-shadow); margin-bottom: 1.5rem; border: 1px solid #e9ecef; }}
    .login-register-card {{ max-width: 450px; margin: 3rem auto; padding: 30px; background-color: white; }} /* Ensure white background */

    /* Form Styling */
    .stTextInput > label, .stTextArea > label, .stSelectbox > label, .stNumberInput > label {{ color: var(--text-color) !important; font-weight: 600; font-size: 0.95em; margin-bottom: 3px; }}
    .stTextInput>div>div>input, .stTextArea>div>textarea, .stSelectbox>div>div, .stNumberInput>div>div>input {{ border-radius: 6px !important; border: 1px solid #ced4da !important; padding: 10px 12px !important; font-size: 1rem !important; transition: border-color 0.2s ease, box-shadow 0.2s ease; background-color: #141413 !important; color: var(--text-color) !important; }}
    .stTextInput>div>div>input:focus, .stTextArea>div>textarea:focus, .stSelectbox>div>div:focus-within, .stNumberInput>div>div>input:focus {{ border-color: var(--text-color) !important; box-shadow: 0 0 0 0.15rem rgba(13, 157, 227, 0.25) !important; }}
    .stButton>button {{ /* Default button style */ border-radius: 6px !important; padding: 9px 18px !important; font-weight: 600 !important; font-size: 0.95rem !important; transition: all 0.2s ease !important; border: none !important; background: var(--primary-color) !important; color: white !important; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08); }}
    .stButton>button:hover {{ background: #0a8cd2 !important; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); transform: translateY(-1px); }}
    .stButton>button.btn-delete-profile {{ background: #dc3545 !important; box-shadow: 0 2px 5px rgba(220, 53, 69, 0.2); }}
    .stButton>button.btn-delete-profile:hover {{ background: #c82333 !important; box-shadow: 0 4px 10px rgba(220, 53, 69, 0.3); }}

    /* Expander Styling */
    .stExpander {{ border: 1px solid #e0e0e0 !important; border-radius: var(--border-radius) !important; box-shadow: none !important; margin-bottom: 1rem; overflow: hidden; }}
    .stExpander header {{ background-color: #e9f5fd !important; border-top-left-radius: var(--border-radius) !important; border-top-right-radius: var(--border-radius) !important; padding: 10px 15px !important; border-bottom: 1px solid #d0dff0 !important; }}
    .stExpander header p {{ font-weight: 600; color: var(--primary-color); }}
    .stExpander [data-testid="stExpanderDetails"] {{ background-color: black !important; padding: 15px !important; border-bottom-left-radius: var(--border-radius) !important; border-bottom-right-radius: var(--border-radius) !important; }}
    .stExpander [data-testid="stExpanderDetails"] p,
    .stExpander [data-testid="stExpanderDetails"] li,
    .stExpander [data-testid="stExpanderDetails"] span {{ color: var(--text-color) !important; }}

    /* --- Footer --- */
    .footer {{ text-align: center; padding: 1rem 0; font-size: 0.9em; color: var(--secondary-color); margin-top: auto; /* Push footer down */ border-top: 1px solid #e0e0e0; background-color: var(--light-color); width: 100%; }}
    .footer span {{ font-size: 0.85em; display: block; margin-top: 0.3rem; }}

    /* --- Responsive --- */
    @media (max-width: 768px) {{
        .logged-out-nav {{ padding: 5px 1rem; }}
        .hero-container {{ padding: 3rem 1rem 4rem 1rem; }}
        .hero-content h1 {{ font-size: 2.0em; }} .hero-content p {{ font-size: 1em; }}
        .auth-buttons {{ gap: 0.8rem; }} .stButton>button.hero-btn {{ min-width: 120px; padding: 9px 18px !important; font-size: 0.95em !important; }}
        .features-section h2 {{ font-size: 1.6em; margin-bottom: 2rem; }}
        /* Hide sidebar column on mobile */
        .sidebar-column {{ display: none; }}
        /* Make content full width on mobile when logged in */
        .page-container-logged-in {{ margin-left: 0; width: 100%; padding: 1.5rem 1rem; }}
        .profile-logout-area span {{ display: none; }} /* Hide welcome msg on mobile */
        h1 {{ font-size: 1.6em; }} h2 {{ font-size: 1.4em; }}
        .login-register-card {{ max-width: 100%; padding: 20px; margin: 1.5rem auto;}}
        .content-card {{ padding: 20px; }}
        /* Adjust navbar columns for mobile if needed */
        .logged-out-nav .stButton>button {{ font-size: 0.9em; padding: 6px 8px !important; }}
    }}
</style>
"""
    st.markdown(css, unsafe_allow_html=True)

# --- Backend Setup ---
# Assumes utils.auth and utils.database are available and configured
@st.cache_resource
def get_auth_instance(): return Auth()
@st.cache_resource
def get_db_instance():
    try:
        client_wrapper = MongoDB()
        if client_wrapper.client is None: raise Exception("Wrapper failed to init internal client.")
        try:
            client_wrapper.client.admin.command('ping'); print("✅ MongoDB server ping successful!")
            db = client_wrapper.get_database()
            if db is not None: print("✅ Database handle obtained!"); return client_wrapper
            else: raise Exception("get_database() returned None.")
        except Exception as ping_error: raise Exception(f"DB Ping/Handle Error: {ping_error}")
    except Exception as e: st.error(f"❌ Database Init/Connection Error: {e}", icon="🚨"); return None # Return None if DB fails

auth = get_auth_instance()
db_client_wrapper = get_db_instance()
# Only assign db to auth if db_client_wrapper is not None
if db_client_wrapper:
    auth.db = db_client_wrapper
else:
    auth.db = None # Ensure auth.db is None if connection failed
    st.warning("Database connection failed. Some features might be unavailable.", icon="⚠️")


# --- Session State ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Home"
# Add scroll_target to session state if it doesn't exist
if 'scroll_target' not in st.session_state: st.session_state.scroll_target = None

# --- Navigation Components ---
def render_logged_out_navbar():
    # Simple navbar using columns for logged-out state
    with st.container(): # Contain the navbar
        st.markdown('<div class="logged-out-nav">', unsafe_allow_html=True)
        # Adjusted ratios for 5 items: Logo | Home | Features | About | Emergency
        nav_cols = st.columns([3, 1, 1, 1, 1.2]) # Give slightly more space to Emergency
        with nav_cols[0]:
            st.markdown(logo_html, unsafe_allow_html=True) # Render logo+title
        with nav_cols[1]:
            # Home button changes page state
            if st.button("Home", key="nav_home_lo", use_container_width=True):
                st.session_state.page = "Home"
                st.session_state.scroll_target = None # Clear scroll target if navigating home
                st.rerun()
        with nav_cols[2]:
            # Features button sets scroll target
            if st.button("Features", key="nav_features_lo", use_container_width=True):
                st.session_state.scroll_target = "features-section"
                # Ensure we are on the home page to see the section
                if st.session_state.page != "Home":
                    st.session_state.page = "Home"
                st.rerun() # Rerun to trigger JS injection
        with nav_cols[3]:
            # About Us button sets scroll target
            if st.button("About Us", key="nav_about_lo", use_container_width=True):
                st.session_state.scroll_target = "about-us-section"
                # Ensure we are on the home page to see the section
                if st.session_state.page != "Home":
                    st.session_state.page = "Home"
                st.rerun() # Rerun to trigger JS injection
        with nav_cols[4]:
            # Emergency Button uses st.button, needs specific container class for styling
            if st.button("🚨 Emergency (102)", key="nav_emergency_lo", use_container_width=True):
                st.warning("Simulating call to 102. In a real emergency, please dial 102 directly using your phone.", icon="⚠️")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
        # --- Javascript Injection Logic moved to main() ---


def render_sidebar_menu():
    # Renders the option menu inside the sidebar column
    # Uses light theme styling from CSS
    role = st.session_state.user.get("role", "patient").lower()
    menu_items = {
        "Home": {"icon": "bi bi-house-door", "page": "Home"}, # Use outline icons
        "Research Analyzer": {"icon": "bi bi-journal-richtext", "page": "Research Analyzer"},
        "Symptom Analyzer": {"icon": "bi bi-heart-pulse", "page": "Symptom Analyzer"},
        "Wellness Tracker": {"icon": "bi bi-clipboard-data", "page": "Wellness Tracker"},
        "Profile": {"icon": "bi bi-person", "page": "Profile"}
    }
    # Use Bootstrap Icons CSS classes if available, otherwise fallback (emojis used in CSS as fallback)
    icons = [details["icon"] for details in menu_items.values()] # Keep using class names

    if role == 'doctor': menu_items.pop("Symptom Analyzer", None)
    options = list(menu_items.keys())

    current_page = st.session_state.page
    default_index = 0;
    for i, details in enumerate(menu_items.values()):
        if details["page"] == current_page: default_index = i; break

    selected = option_menu(
        menu_title="Navigation", # Add title
        options=options, icons=icons, menu_icon="list-ul", # Use list icon
        default_index=default_index, orientation="vertical",
        key='sidebar_menu',
        styles={ "container": {"padding": "0 !important", "background-color": "transparent"}, } # Rely on CSS
    )
    selected_page_target = menu_items[selected]["page"]
    if st.session_state.page != selected_page_target:
        st.session_state.page = selected_page_target
        st.session_state.scroll_target = None # Clear scroll target when changing pages
        st.rerun()

def render_profile_logout_area():
     # Placed at the top of the content column when logged in
     user = st.session_state.user
     st.markdown('<div class="profile-logout-area">', unsafe_allow_html=True)
     cols = st.columns([0.8, 0.2]) # Adjust ratio for spacing
     with cols[0]:
          st.markdown(f"<span>Welcome, **{user['name']}** ({user['role'].capitalize()})</span>", unsafe_allow_html=True)
     with cols[1]:
          if st.button("Logout", key="content_logout_btn", help="Logout"):
              logout()
     st.markdown('</div>', unsafe_allow_html=True)


# --- Page Rendering Functions ---

def landing_page():
    # Hero Section with integrated buttons and correct text
    with st.container():
        st.markdown('<div class="hero-container">', unsafe_allow_html=True)
        st.markdown('<div class="hero-content">', unsafe_allow_html=True)
        # Specific Title Requested
        st.markdown('<h1>HEALTHEASE - AI Driven Healthcare Innovation</h1>', unsafe_allow_html=True)
        # Updated Description
        st.markdown('<p class="hero-description">Navigate your health journey with confidence. HealthEase leverages cutting-edge AI to help you understand medical research, analyze symptoms preliminarily, and track your wellness goals effectively. Join us to experience a smarter approach to healthcare.</p>', unsafe_allow_html=True)
        # Centralized Buttons below text
        st.markdown('<div class="hero-buttons">', unsafe_allow_html=True)
        col1, col2 = st.columns([1,1]) # Centered columns
        with col1:
            if st.button("Member Login", key="hero_login_btn_v2", use_container_width=True): # Unique key
                st.session_state.page = "Login"
                st.session_state.scroll_target = None
                st.rerun()
        with col2:
            if st.button("Register Now", key="hero_register_btn_v2", use_container_width=True): # Unique key
                st.session_state.page = "Register"
                st.session_state.scroll_target = None
                st.rerun()
        # JS class assignment for styling
        st.markdown("""
            <script>
                const authBtns = window.parent.document.querySelector('.hero-buttons');
                if (authBtns) {
                    const loginBtnContainer = authBtns.querySelector('button[data-testid="stButton"][key="hero_login_btn_v2"]').closest('div[data-testid="stButton"]');
                    const registerBtnContainer = authBtns.querySelector('button[data-testid="stButton"][key="hero_register_btn_v2"]').closest('div[data-testid="stButton"]');
                    if(loginBtnContainer) loginBtnContainer.classList.add('hero-btn', 'hero-btn-login');
                    if(registerBtnContainer) registerBtnContainer.classList.add('hero-btn', 'hero-btn-register');
                }
            </script>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True) # Close auth-buttons
        st.markdown('</div></div>', unsafe_allow_html=True) # Close hero-content, hero-container

    # --- About Us Section (NEW) ---
    # Ensure this container has the ID for the anchor link to target
    with st.container():
        st.markdown('<div id="about-us-section" style="padding: 1rem 1rem; max-width: 900px; margin: 0 auto 2.5rem auto; text-align: left; background-color: var(--background-color); border-radius: var(--border-radius); box-shadow: var(--card-shadow);">', unsafe_allow_html=True) # ID is here
        st.markdown('<h2 style="text-align: center; color: var(--primary-color); border-bottom: none; margin-bottom: 1.5rem;">About HealthEase</h2>', unsafe_allow_html=True)
        st.markdown("""
            <p style="font-size: 1.1em; color: var(--text-color); line-height: 1.7; padding: 0 1rem;">
            HealthEase was founded with the mission to empower individuals by making health information accessible with ease and actionable through cutting-edge Artificial Intelligence.
            We believe in leveraging technology to bridge the gap between medical knowledge and patient understanding, fostering proactive health management and informed decision-making.
            <br><br>
            Our aim is to develop a user-friendly website for basic healthcare monitoring and guidance.Allow users to input symptoms and medical data.Provide remedies and health improvement suggestions.Immediate assistance for any biological query and Summarizing Biological Research Papers for medical purposes.
            <br><br>
            Join us in embracing a smarter, more informed approach to personal health and wellness.
            </p>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


    # Features Section
    # Ensure this container has the ID for the anchor link to target
    with st.container():
        st.markdown('<div id="features-section" class="page-container features-section" style="padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px; margin: 0 auto;">', unsafe_allow_html=True) # ID is here
        st.markdown('<h2 style="text-align: center;">How HealthEase Empowers You</h2>', unsafe_allow_html=True)
        cols = st.columns(3)
        feature_list = ["Research Analyzer", "Symptom Analyzer", "Wellness Tracker"]
        feature_texts = { "Research Analyzer": "Instantly decode complex medical papers. Get AI-generated summaries and key findings from PDF uploads.", "Symptom Analyzer": "Gain preliminary insights from your symptoms. Our AI provides analysis and potential next steps (consult a doctor!).", "Wellness Tracker": "Monitor vital signs, track fitness goals, and visualize your health trends over time. Stay proactive." }
        for i, feature in enumerate(feature_list):
            with cols[i]:
                icon = config["feature_icons"].get(feature, "❓")
                st.markdown(f"""
                    <div class="feature-card" style="background-color: var(--card-bg); padding: 25px; border-radius: var(--border-radius); box-shadow: var(--card-shadow); margin-bottom: 1.5rem; border: 1px solid #e9ecef; text-align: center; height: 100%;">
                        <div class="feature-icon" style="font-size: 2.5em; margin-bottom: 1rem;">{icon}</div>
                        <h3 style="color: var(--primary-color); margin-bottom: 0.8rem;">{feature}</h3>
                        <p style="color: var(--text-color); font-size: 0.95em;">{feature_texts[feature]}</p>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def login_page():
    # Use general page container
    st.markdown('<h1 style="text-align: center; border-bottom: none; margin-bottom: 1.5rem;">Welcome Back!</h1>', unsafe_allow_html=True)
    with st.form("login_form"):
        email = st.text_input("Email Address", key="login_email_input", placeholder="you@example.com")
        password = st.text_input("Password", type="password", key="login_password_input", placeholder="••••••••")
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Log In", use_container_width=True)
        if submitted:
            if not email or not password: st.warning("Please enter email and password.", icon="⚠️"); return
            # Assumes check_authentication is imported and works
            user = check_authentication(email, password)
            if user:
                st.session_state.user = user
                st.session_state.page = "Home"
                st.session_state.scroll_target = None # Clear scroll on login
                st.success(f"Login successful! Redirecting..."); time.sleep(1.5); st.rerun()
            else: st.error("Invalid credentials. Please try again.", icon="❌")
    if st.button("Need an account? Register", key="link_to_register_login"):
         st.session_state.page = "Register"
         st.session_state.scroll_target = None
         st.rerun()
    st.markdown('</div>', unsafe_allow_html=True) # Close page-container

def register_page():
    # Use general page container
    st.markdown('<h1 style="text-align: center; border-bottom: none; margin-bottom: 1.5rem;">Create Account</h1>', unsafe_allow_html=True)
    roles = ["Patient", "Doctor", "Researcher"]
    with st.form("register_form"):
        name = st.text_input("Full Name", key="reg_name_input"); email = st.text_input("Email Address", key="reg_email_input"); password = st.text_input("Create Password", type="password", key="reg_password_input", help="Minimum 6 characters"); confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password_input"); age = st.number_input("Age", min_value=13, max_value=110, step=1, key="reg_age_input"); role = st.selectbox("I am a...", roles, key="reg_role_input"); st.markdown("<br>", unsafe_allow_html=True); submitted = st.form_submit_button("Register", use_container_width=True)
        if submitted:
            if not all([name, email, password, confirm_password, age, role]): st.warning("Please fill all fields.", icon="⚠️"); return
            if password != confirm_password: st.error("Passwords don't match!", icon="❌"); return
            if len(password) < 6: st.warning("Password must be at least 6 characters.", icon="⚠️"); return
            if auth.db is None: st.error("Database connection error. Cannot register account.", icon="🚨"); return
            # Assumes auth.register_user works
            success, message = auth.register_user(name, email, password, age, role)
            if success:
                st.success("Registration successful! Please log in."); time.sleep(2)
                st.session_state.page = "Login"
                st.session_state.scroll_target = None
                st.rerun()
            else: st.error(f"Registration failed: {message}", icon="❌")
    if st.button("Already Registered? Log In", key="link_to_login_reg"):
        st.session_state.page = "Login"
        st.session_state.scroll_target = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True) # Close page-container


# --- INTEGRATED Feature Page Functions (BRIGHT THEME) ---

def logged_in_home_page(): # Dashboard
    user = st.session_state.user
    st.markdown(f"<p style='font-size: 1.1em; color: var(--secondary-color);'>Select a tool from the sidebar menu to get started.</p>", unsafe_allow_html=True)

def research_analyzer_page():
    st.markdown("<h1>📄 Research Paper Analyzer</h1>", unsafe_allow_html=True)
    with st.container(border=True): # Use border=True for visual grouping
        st.markdown("<h2>Upload & Analyze</h2>", unsafe_allow_html=True)
        st.markdown("<p>Select a research paper (PDF). Our AI will summarize and extract key points. Analysis may take a few minutes.</p>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Select PDF File", type=['pdf'], key="ra_uploader_input", label_visibility="collapsed")

    if uploaded_file:
        with st.container(border=True): # Use border=True
            st.markdown("<h2>Analysis Results</h2>", unsafe_allow_html=True)
            with st.spinner("🤖 Analyzing paper... Please wait."):
                try:
                    # Assumes ResearchAnalyzer is imported and works
                    analyzer = ResearchAnalyzer(); result = analyzer.analyze_research_paper(uploaded_file)
                    if isinstance(result, str): result = json.loads(result)
                    elif not isinstance(result, dict): raise ValueError("Unexpected result type")
                    summary = result.get("summary", "No summary generated."); key_points = result.get("key_points", [])
                    st.markdown("<h3>Summary</h3>", unsafe_allow_html=True); st.markdown(f"<div style='background-color: var(--light-color); padding: 15px; border-radius: 6px; border: 1px solid #e0e0e0; margin-bottom: 1rem; color: var(--text-color);'>{summary}</div>", unsafe_allow_html=True)
                    if key_points:
                        st.markdown("<h3>Key Points</h3>", unsafe_allow_html=True)
                        st.markdown("<ul>", unsafe_allow_html=True)
                        for point in key_points: st.markdown(f"<li style='color: var(--text-color);'>{point}</li>", unsafe_allow_html=True)
                        st.markdown("</ul>", unsafe_allow_html=True)
                    else: st.markdown("<p style='color: var(--secondary-color);'><em>No specific key points extracted.</em></p>", unsafe_allow_html=True)
                except Exception as e: st.error(f"Analysis failed: {e}", icon="🚨")

def symptom_analyzer_page():
    st.markdown("<h1>🩺 AI Symptom Analyzer</h1>", unsafe_allow_html=True)
    with st.container(border=True): # Use border=True
        st.markdown("<h2>Describe Your Symptoms</h2>", unsafe_allow_html=True)
        st.warning("AI analysis is informational, not a diagnosis. Consult a doctor.", icon="⚠️")
        symptoms = st.text_area("Provide details:", height=150, key="sa_symptoms_input", placeholder="e.g., Persistent dry cough...")
        analyze_button = st.button("Analyze Symptoms", key="sa_analyze_button")

    if analyze_button:
        if not symptoms or len(symptoms) < 10: st.warning("Please provide more detail.", icon="ℹ️")
        else:
            with st.container(border=True): # Use border=True
                st.markdown("<h2>AI Analysis Results</h2>", unsafe_allow_html=True)
                with st.spinner("🧠 Analyzing symptoms..."):
                    try:
                        # Assumes SymptomAnalyzer is imported and works
                        analyzer = SymptomAnalyzer(); result = analyzer.analyze_symptoms(symptoms)
                        if isinstance(result, str): result = json.loads(result)
                        elif not isinstance(result, dict): raise ValueError("Unexpected result type")
                        user_id = st.session_state.user.get("_id") if st.session_state.user else None
                        if user_id and auth.db is not None:
                            history_data = {"symptoms": symptoms, "recommendation": result, "timestamp": datetime.now(timezone.utc).isoformat()};
                            try: auth.db.save_symptom_history(user_id, history_data)
                            except Exception as db_err: st.warning(f"Could not save history: {db_err}", icon="💾")
                        elif user_id and auth.db is None: st.warning("DB unavailable, history not saved.", icon="💾")
                        analysis_data = result.get("Analysis Results", result)
                        if isinstance(analysis_data, dict):
                            severity = analysis_data.get("Severity", "N/A"); confidence = analysis_data.get("Confidence", "N/A"); recommendations = analysis_data.get("Recommendations", []); possible_conditions = analysis_data.get("Possible Conditions", [])
                            st.markdown(f"<h4>Severity Assessment: <span style='color:#dc3545; font-weight: bold;'>{severity}</span></h4>", unsafe_allow_html=True); st.markdown(f"<h4>Confidence Level: <span style='color:var(--primary-color); font-weight: bold;'>{confidence}</span></h4>", unsafe_allow_html=True); st.markdown("<hr>", unsafe_allow_html=True)
                            if possible_conditions: st.markdown("<h4>Possible Conditions (AI Suggestion):</h4>", unsafe_allow_html=True); cond_html = "".join(f"<li style='color: var(--text-color);'>{cond}</li>" for cond in possible_conditions); st.markdown(f"<ul>{cond_html}</ul>", unsafe_allow_html=True)
                            if recommendations: st.markdown("<h4>💡 Recommendations:</h4>", unsafe_allow_html=True); rec_html = "".join(f"<li style='color: var(--text-color);'>{rec}</li>" for rec in recommendations); st.markdown(f"<ul>{rec_html}</ul>", unsafe_allow_html=True)
                            else: st.markdown("<p><em>No specific recommendations provided.</em></p>", unsafe_allow_html=True)
                            st.markdown("<hr>", unsafe_allow_html=True); st.markdown(f"<p style='color:var(--secondary-color); font-style: italic; font-size: 0.9em;'><strong>Disclaimer:</strong> Consult a healthcare professional.</p>", unsafe_allow_html=True)
                        else: st.error("Unexpected analysis format.", icon="❓"); print(f"Unexpected SA format: {result}")
                    except Exception as e: st.error(f"Analysis Error: {e}", icon="🚨")

def wellness_tracker_page():
    st.markdown("<h1>🧘 Wellness Tracker</h1>", unsafe_allow_html=True)
    with st.container(border=True): # Use border=True
        st.markdown("<h2>Your Wellness Dashboard</h2>", unsafe_allow_html=True)
        st.info("Track metrics, visualize trends, and stay proactive.", icon="📊")
        try:
            # Assumes WellnessTracker is imported and works
            tracker = WellnessTracker()
            tracker.render_dashboard()
        except AttributeError: # Specific fallback if render_dashboard is missing
             st.warning("Tracker dashboard rendering not fully implemented.", icon="🛠️"); st.markdown("---"); st.markdown("<h4>Example Metrics:</h4>", unsafe_allow_html=True); cols = st.columns(3); cols[0].metric("Avg Heart Rate", "72 bpm"); cols[1].metric("Steps Today", "6,540"); cols[2].metric("Sleep Score", "85"); st.line_chart(data={'Score': [70, 75, 85, 82, 88]})
        except Exception as e: st.error(f"Error loading tracker: {e}", icon="🚨")

def profile_page():
    st.markdown("<h1>👤 User Profile</h1>", unsafe_allow_html=True)
    user = st.session_state.user
    with st.container(border=True): # Use border=True
        st.markdown("<h2>Account Information</h2>", unsafe_allow_html=True); col1, col2 = st.columns(2);
        with col1: st.markdown(f"**Name:**<br>{user['name']}", unsafe_allow_html=True); st.markdown(f"**Email:**<br>{user['email']}", unsafe_allow_html=True)
        with col2: st.markdown(f"**Age:**<br>{user.get('age', 'N/A')}", unsafe_allow_html=True); st.markdown(f"**Role:**<br>{user.get('role', 'N/A').capitalize()}", unsafe_allow_html=True)

    if user.get("role", "").lower() != "doctor":
        with st.container(border=True): # Use border=True
            st.markdown("<h2>🩺 Symptom Analysis History</h2>", unsafe_allow_html=True)
            if auth.db is None: st.warning("DB unavailable. Cannot load history.", icon="💾")
            else:
                try:
                    symptom_data = auth.db.get_symptom_history(user["_id"])
                    if symptom_data:
                        st.caption(f"{len(symptom_data)} entr{'y' if len(symptom_data) == 1 else 'ies'} found. Showing newest first.")
                        for i, entry in enumerate(reversed(symptom_data)):
                            timestamp_str = entry.get("timestamp", "N/A"); symptoms = entry.get("symptoms", "N/A"); display_time = timestamp_str;
                            try: display_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00")).strftime('%Y-%m-%d %H:%M %Z') # Handle Z timezone
                            except: pass
                            with st.expander(f"🗓️ Entry: {display_time}", expanded=(i < 2)):
                                st.markdown(f"**Symptoms Reported:**"); st.markdown(f"<p style='background-color: #141413; padding: 10px; border-radius: 5px; color: var(--text-color);'>{symptoms}</p>", unsafe_allow_html=True); st.markdown(f"**AI Analysis:**") # Ensure text color
                                recommendation_raw = entry.get("recommendation", {}); recommendation = recommendation_raw;
                                if isinstance(recommendation, str):
                                    try: recommendation = json.loads(recommendation);
                                    except: recommendation = {}
                                # Handle cases where recommendation might be a list containing the dict
                                if isinstance(recommendation, list) and len(recommendation) > 0 and isinstance(recommendation[0], dict): recommendation = recommendation[0];

                                analysis_results = recommendation.get("Analysis Results", recommendation) # Check top level too
                                if isinstance(analysis_results, dict) and analysis_results:
                                    severity = analysis_results.get("Severity", "N/A"); confidence = analysis_results.get("Confidence", "N/A"); advice_list = analysis_results.get("Recommendations", []); note = analysis_results.get("⚠️ Note", analysis_results.get("Note", "")) # Check for note variations
                                    st.markdown(f"*   **Severity:** {severity}")
                                    st.markdown(f"*   **Confidence:** {confidence}")
                                    if advice_list:
                                        st.markdown("*   **Recommendations:**")
                                        for advice in advice_list: st.markdown(f"    *   {advice}") # Indented list
                                    if note: st.markdown(f"*   **Note:** {note}")
                                else: st.caption("No formatted AI analysis available.")
                    else: st.info("No symptom analysis history found.")
                except Exception as e: st.error(f"Error retrieving history: {e}", icon="🚨")

    with st.container(): # Keep delete section visually separate
        st.markdown("<h2 style='color: #dc3545;'>Delete Account</h2>", unsafe_allow_html=True); st.warning("This action is permanent and cannot be undone.", icon="❗"); confirm_delete = st.checkbox("I understand and wish to permanently delete my account and all associated data.", key="delete_confirm_input");
        if st.button("Delete My Account Permanently", key="delete_account_final_button", disabled=not confirm_delete, type="secondary"):
             # Apply danger class via JS
             st.markdown(""" <script> const deleteBtnContainer = window.parent.document.querySelector('button[data-testid="stButton"][key="delete_account_final_button"]').closest('div[data-testid="stButton"]'); if(deleteBtnContainer){ deleteBtnContainer.classList.add('btn-delete-profile'); } </script> """, unsafe_allow_html=True)
             if confirm_delete and user and auth.db is not None:
                 try:
                     success = auth.db.delete_user_and_data(user["_id"])
                     if success:
                         st.success("Account deleted successfully.", icon="✅")
                         st.session_state.user = None
                         st.session_state.page = "Home"
                         st.session_state.scroll_target = None
                         time.sleep(2); st.rerun()
                     else: st.error("Account deletion failed. Please contact support if this persists.", icon="❌")
                 except Exception as e: st.error(f"An error occurred during account deletion: {e}", icon="🚨")
             elif auth.db is None: st.error("Database service is currently unavailable. Cannot delete account.", icon="💾")
             elif not confirm_delete: pass # Should be disabled, but double check
             else: st.error("User session error. Please log out and log back in.", icon="❓") # Should not happen
        st.markdown('</div>', unsafe_allow_html=True)


# --- Utility Functions ---
def logout():
    st.session_state.user = None
    st.session_state.page = "Home"
    st.session_state.scroll_target = None # Clear scroll target on logout
    st.success("Logged out successfully.")
    time.sleep(1)
    st.rerun()

# --- Main App Logic ---
def main():
    load_css() # Apply styles first

    page = st.session_state.page
    user = st.session_state.user

    if not user:
        # --- Logged Out View ---
        render_logged_out_navbar() # Show simple nav bar with scrolling buttons
        # Landing page content (Hero, About, Features) is rendered based on page state
        if page == "Home": landing_page()
        elif page == "Login": login_page()
        elif page == "Register": register_page()
        # Add handling for potential direct navigation attempts when logged out
        elif page in ["Research Analyzer", "Symptom Analyzer", "Wellness Tracker", "Profile"]:
            st.warning("Please log in or register to access this feature.", icon="🔒")
            st.session_state.page = "Home" # Force back to home
            st.session_state.scroll_target = None
            landing_page() # Show landing page instead
        else:
            st.session_state.page = "Home"; st.rerun() # Default to landing
    else:
        # --- Logged In View (Using Columns) ---
        st.markdown('<div class="app-container-logged-in">', unsafe_allow_html=True)
        col_sidebar, col_content = st.columns([1, 4]) # Adjust ratio e.g., [1, 5] or [2, 8]

        with col_sidebar:
            st.markdown('<div class="sidebar-column">', unsafe_allow_html=True)
            render_sidebar_menu() # Render option menu in the sidebar column
            st.markdown('</div>', unsafe_allow_html=True)

        with col_content:
            st.markdown('<div class="content-column">', unsafe_allow_html=True)
            render_profile_logout_area() # Welcome user / Logout button at top right of content

            # Routing logic for content column
            if page == "Home": logged_in_home_page()
            elif page == "Research Analyzer": research_analyzer_page()
            elif page == "Symptom Analyzer" and user.get('role', '').lower() != 'doctor': symptom_analyzer_page()
            elif page == "Wellness Tracker": wellness_tracker_page()
            elif page == "Profile": profile_page()
            # Handle case where doctor tries to access symptom analyzer via URL manipulation or state issue
            elif page == "Symptom Analyzer" and user.get('role', '').lower() == 'doctor':
                st.warning("Symptom Analyzer is not available for Doctor accounts. Redirecting to Home.", icon="🚫");
                st.session_state.page = "Home"; time.sleep(2); st.rerun()
            # Handle login/register pages if somehow accessed while logged in
            elif page in ["Login", "Register"]:
                 st.info("You are already logged in. Redirecting to Home.", icon="ℹ️")
                 st.session_state.page = "Home"; time.sleep(1); st.rerun()
            else: # Fallback for any unknown page state
                 st.warning(f"Page '{page}' not found. Showing Dashboard.", icon="❓");
                 st.session_state.page = "Home"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True) # Close content-column

        st.markdown('</div>', unsafe_allow_html=True) # Close app-container-logged-in

    # --- Footer --- Render it outside the main content logic
    st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True) # Spacer before footer
    st.markdown(f""" <div class="footer"> © {datetime.now().year} HealthEase. All rights reserved. <span>Disclaimer: AI insights are informational and not a substitute for professional medical advice. Always consult a qualified healthcare provider for any health concerns or before making any decisions related to your health or treatment.</span> </div> """, unsafe_allow_html=True)

    # --- Javascript Scroll Injection ---
    # Check if scroll_target is set and inject script if needed
    if st.session_state.scroll_target:
        target_id = st.session_state.scroll_target
        scroll_script = f"""
            <script>
                // Function to scroll smoothly
                function scrollToElement(elementId) {{
                    const element = window.parent.document.getElementById(elementId);
                    if (element) {{
                        console.log('Scrolling to:', elementId);
                        // Use requestAnimationFrame for smoother rendering before scroll
                        window.parent.requestAnimationFrame(() => {{
                             element.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                        }});
                    }} else {{
                        // Retry after a short delay if element not found immediately
                        setTimeout(() => {{
                            const elementRetry = window.parent.document.getElementById(elementId);
                            if (elementRetry) {{
                                console.log('Scrolling to (retry):', elementId);
                                window.parent.requestAnimationFrame(() => {{
                                     elementRetry.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                                }});
                            }} else {{
                                console.warn('Scroll target still not found after retry:', elementId);
                            }}
                        }}, 300); // Increased delay for retry
                    }}
                }}

                // Execute the scroll function
                scrollToElement('{target_id}');

            </script>
        """
        components.html(scroll_script, height=0, width=0)
        # IMPORTANT: Unset the flag AFTER injecting the script
        st.session_state.scroll_target = None


if __name__ == "__main__":
    main()