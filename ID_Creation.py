import streamlit as st
import gspread
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

# Simple username and password for login
USERNAME = "admin"
PASSWORD = "password123"

# Authenticate with Google Sheets using Streamlit secrets
def authenticate_gspread():
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
    
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    client = gspread.authorize(creds)
    return client

# Append data to Google Sheets
def append_to_sheet(data):
    client = authenticate_gspread()
    
    # Open the Google Sheet using its URL
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1Rrxrjo_id38Rpl1H7Vq30ZsxxjUOvWiFQhfexn-LJlE/edit?gid=0#gid=0")
    
    # Select the "Kolkata" sheet
    worksheet = sheet.worksheet("Kolkata")
    
    # Append the data as a new row
    worksheet.append_row(data)

# Streamlit Login Page
def login_page():
    st.title("Login Page")

    # Input fields for username and password
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    # Check login button
    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            # Set session state to indicate successful login
            st.session_state.logged_in = True
            st.success("Login successful!")
        else:
            st.error("Invalid username or password.")

# Streamlit Data Entry Form Page
def data_entry_page():
    st.title("Data Entry for Kolkata Sheet")

    with st.form(key="data_entry_form"):
        name = st.text_input("Enter your name:")
        age = st.number_input("Enter your age:", min_value=1)
        city = st.text_input("Enter your city:")

        # Submit button
        submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            if name and city:  # Ensure data is not empty
                # Data to append to the sheet
                data = [name, age, city]
                append_to_sheet(data)
                st.success("Data has been successfully added to the sheet!")
            else:
                st.error("Please fill all fields.")

# Main Application Logic
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    # If not logged in, show the login page
    login_page()
else:
    # If logged in, show the data entry form page
    data_entry_page()
