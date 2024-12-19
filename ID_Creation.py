import streamlit as st
import pandas as pd
import re
import json
import base64
from oauth2client.service_account import ServiceAccountCredentials
from gspread import authorize

# Function to authenticate Google Sheets using credentials from Streamlit secrets
def authenticate_google_sheets():
    # Access the credentials from Streamlit's secrets
    creds_base64 = st.secrets["google_credentials"]["credentials"]  # Get the base64 string
    
    # Decode the base64 string
    creds_json = base64.b64decode(creds_base64).decode('utf-8')
    
    # Load the credentials as a dictionary
    creds_dict = json.loads(creds_json)
    
    # Define the scope required to access Google Sheets and Drive
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # Use the credentials to authenticate
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    # Authorize the client with the credentials
    client = authorize(creds)
    
    # Access the specified Google Sheet by its URL
    worksheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1Rrxrjo_id38Rpl1H7Vq30ZsxxjUOvWiFQhfexn-LJlE/edit?gid=0').worksheet("Kolkata")
    return worksheet

# Function to validate email format
def is_valid_email(email):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

# Function to validate contact number (must be exactly 10 digits)
def is_valid_contact_number(contact_number):
    return contact_number.isdigit() and len(contact_number) == 10

# Function to display the form
def show_form():
    st.title("Fill the Form")

    # Input fields
    emp_id = st.text_input("EMP ID", key="emp_id")
    agent_name = st.text_input("Agent Name", key="agent_name")
    contact_no = st.text_input("Contact No:", key="contact_no")
    official_email = st.text_input("Official Email_ID:", key="official_email")
    department = st.selectbox("Department Name:", ["Consent", "LROD", "Collection", "SE_Onboarding", "ST_Onboarding"])
    trainer_name = st.text_input("Trainer Name:", key="trainer_name")
    designation = st.text_input("Designation:", key="designation")

    # Add Row functionality
    if st.button("Add Row", key="add_row"):
        # Validate inputs before adding a new row
        if not emp_id or not agent_name or not contact_no or not official_email or not department or not trainer_name:
            st.error("Please fill in all fields!")
        elif not is_valid_email(official_email):
            st.error("Please enter a valid email address.")
        elif not is_valid_contact_number(contact_no):
            st.error("Contact number must be 10 digits.")
        else:
            new_row = {
                "EMP ID": emp_id,
                "Agent Name": agent_name,
                "Contact No": contact_no,
                "Official Email_ID": official_email,
                "Department": department,
                "Trainer Name": trainer_name,
                "Designation": designation  # Include designation if provided
            }
            
            # Fetch Google Sheets worksheet for Kolkata
            worksheet = authenticate_google_sheets()

            # Adding data to the Google Sheet
            worksheet.append_row(list(new_row.values()))

            st.success("Row added successfully!")

# Main function to control the flow of the app
def main():
    show_form()  # Show the form for data input

if __name__ == "__main__":
    main()
