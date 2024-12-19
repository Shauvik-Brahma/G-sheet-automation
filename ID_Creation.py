import streamlit as st
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Function to authenticate Google Sheets using credentials
def authenticate_google_sheets():
    # Access the credentials from Streamlit secrets
    creds = st.secrets["google_credentials"]  # Store your JSON credentials as a secret
    
    # Define the scope required to access Google Sheets
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # Use the credentials to authenticate
    creds_dict = creds
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    
    # Authorize and connect to the Google Sheets API
    client = gspread.authorize(credentials)
    
    # Open the spreadsheet by its URL (replace this with your sheet URL)
    spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1Rrxrjo_id38Rpl1H7Vq30ZsxxjUOvWiFQhfexn-LJlE/edit?usp=sharing")
    
    # Open the specific worksheet (sheet name "Kolkata")
    worksheet = spreadsheet.worksheet("Kolkata")
    return worksheet

# Function to validate email format
def is_valid_email(email):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

# Function to validate phone number (must be exactly 10 digits)
def is_valid_phone(phone):
    return phone.isdigit() and len(phone) == 10

# Function to display the form and connect to Google Sheets
def show_form():
    st.title("Simple Form with Google Sheets Integration")

    # Input fields for user information
    emp_id = st.text_input("EMP ID:")
    agent_name = st.text_input("Agent Name:")
    contact_no = st.text_input("Contact No:")
    official_email = st.text_input("Official Email ID:")

    # Submit button
    if st.button("Submit"):
        # Validate the inputs
        if not emp_id or not agent_name or not contact_no or not official_email:
            st.error("Please fill in all fields!")
        elif not is_valid_email(official_email):
            st.error("Please enter a valid email address.")
        elif not is_valid_phone(contact_no):
            st.error("Contact number must be exactly 10 digits.")
        else:
            # Authenticate with Google Sheets
            worksheet = authenticate_google_sheets()
            
            # Append the form data to Google Sheets
            new_row = [emp_id, agent_name, contact_no, official_email]
            worksheet.append_row(new_row)
            
            st.success("Form submitted successfully!")
            st.write("EMP ID:", emp_id)
            st.write("Agent Name:", agent_name)
            st.write("Contact No:", contact_no)
            st.write("Official Email ID:", official_email)

# Main function to run the app
def main():
    show_form()  # Show the form to the user

if __name__ == "__main__":
    main()
