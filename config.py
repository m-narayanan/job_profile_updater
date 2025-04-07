# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# --- Credentials ---
NAUKRI_USERNAME = os.getenv("NAUKRI_USERNAME")
NAUKRI_PASSWORD = os.getenv("NAUKRI_PASSWORD")

# --- Paths ---
RESUME_FOLDER = os.path.join(os.path.dirname(__file__), "resumes")

# --- URLs ---
NAUKRI_LOGIN_URL = "https://login.naukri.com/"
NAUKRI_PROFILE_URL = "https://www.naukri.com/mnjuser/profile"

# --- Feature Flags ---
# Set to True to attempt summary update, False to skip it
UPDATE_PROFILE_SUMMARY = True # <-- Set to False to disable summary updates

# --- Other Settings ---
HEADLESS_BROWSER = True # Set to False for local debugging, True for deployment
IMPLICIT_WAIT_TIME = 10
EXPLICIT_WAIT_TIME = 35 # Increased wait time

# --- Validation ---
def validate_config():
    if not NAUKRI_USERNAME or not NAUKRI_PASSWORD:
        raise ValueError("NAUKRI_USERNAME and NAUKRI_PASSWORD environment variables must be set.")
    if not os.path.isdir(RESUME_FOLDER):
         raise FileNotFoundError(f"Resume folder not found at: {RESUME_FOLDER}")
    print("Configuration validated successfully.")