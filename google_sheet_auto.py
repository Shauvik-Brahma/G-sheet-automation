import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Function to connect to Google Sheets
def connect_to_google_sheet(sheet_url):
    # Define the scope for Google Sheets and Drive
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Get credentials from Streamlit secrets
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    
    # Authorize and create a client
    client = gspread.authorize(creds)
    
    # Open the sheet by its URL
    spreadsheet = client.open_by_url(sheet_url)
    
    # Return the first sheet (or adjust if needed)
    return spreadsheet.sheet1

# Google Sheet URL (replace with your sheet's URL)
SHEET_URL = "https://docs.google.com/spreadsheets/d/17AntJJDXFHZPjC8tpvzTkhK8mo2UybFdxikic3VCe6k/edit?gid=0"

# Streamlit App
st.title("Google Sheets Form")

# Create a form for Name and Class
with st.form("user_form", clear_on_submit=True):
    name = st.text_input("Enter your Name")
    class_name = st.text_input("Enter your Class")
    submitted = st.form_submit_button("Submit")

# If the form is submitted, append the data to the Google Sheet
if submitted:
    if name and class_name:
        try:
            # Connect to Google Sheets
            sheet = connect_to_google_sheet(SHEET_URL)
            
            # Append the data
            sheet.append_row([name, class_name])
            
            # Confirmation message
            st.success("Data submitted successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please fill in both fields.")
