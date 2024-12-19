import streamlit as st
import gspread
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

# Authenticate with Google Sheets using Streamlit secrets
def authenticate_gspread():
    # Load credentials from the Streamlit secrets
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
    
    # Authenticate the credentials
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

# Streamlit Form for user input
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
