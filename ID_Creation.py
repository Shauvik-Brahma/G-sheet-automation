import streamlit as st
import pandas as pd
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# Function to connect to Google Sheets
def connect_to_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    return client

# Function to validate email format
def is_valid_email(email):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

# Function to validate contact number (must be exactly 10 digits)
def is_valid_contact_number(contact_number):
    return contact_number.isdigit() and len(contact_number) == 10

# Function to display login page
def show_login_page():
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    center = st.selectbox("Select Center", ["KOLKATA", "INDORE-TARUS", "MYSORE-TTBS", "BHOPAL-TTBS"])
    employee_type = st.selectbox("Select Employee Type", ["SLT", "DCS"])
    process = st.selectbox("Select Process", ["Collection", "Non_Collection", "Customer Support"])
    Batch_No = st.text_input("Batch No:")
    
    if st.button("Login"):
        if not Batch_No:
            st.error("Please enter a Batch No!")
        elif username == "admin" and password == "admin":
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.center = center
            st.session_state.employee_type = employee_type
            st.session_state.process = process
            st.session_state.Batch_No = Batch_No
            st.session_state.data = pd.DataFrame(columns=["EMP ID", "Name", "Contact No", "Email", "Department", "Trainer"])
            st.success("Login successful!")
        else:
            st.error("Invalid username or password")

# Function to show the editable form
def show_form():
    st.title("Fill the Form")
    
    # Define department options based on process
    department_options = {
        "Collection": ["Consent", "LROD", "Collection"],
        "Non_Collection": ["SE_Onbording", "SIC_Onbording", "Risk"],
        "Customer Support": ["Email"]
    }
    
    # Editable DataFrame for input
    edited_df = st.experimental_data_editor(
        st.session_state.data,
        num_rows="dynamic",
        key="data_editor"
    )
    
    # Validation checks
    invalid_rows = []
    for index, row in edited_df.iterrows():
        if not row["EMP ID"] or not row["Name"] or not row["Contact No"] or not row["Email"] or not row["Department"] or not row["Trainer"]:
            invalid_rows.append(index)
        elif not is_valid_email(row["Email"]):
            invalid_rows.append(index)
        elif not is_valid_contact_number(row["Contact No"]):
            invalid_rows.append(index)
    
    if invalid_rows:
        st.error(f"Row(s) {', '.join(map(str, invalid_rows))} have invalid data. Please fix before submission.")
    
    # Save the updated DataFrame to session state
    st.session_state.data = edited_df
    
    # Submit button
    if st.button("Submit"):
        if invalid_rows:
            st.error("Please fix the errors in the rows before submitting.")
        elif st.session_state.data.empty:
            st.error("No data to submit. Please add rows.")
        else:
            client = connect_to_google_sheets()
            if st.session_state.center == "KOLKATA":
                sheet = client.open_by_key("1Rrxrjo_id38Rpl1H7Vq30ZsxxjUOvWiFQhfexn-LJlE").worksheet("Kolkata")
            else:
                sheet = client.open_by_key("1Rrxrjo_id38Rpl1H7Vq30ZsxxjUOvWiFQhfexn-LJlE").worksheet("Partner")
            
            for _, row in st.session_state.data.iterrows():
                row_data = list(row) + [
                    st.session_state.username,
                    st.session_state.center,
                    st.session_state.employee_type,
                    st.session_state.process,
                    st.session_state.Batch_No,
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ]
                sheet.append_row(row_data)
            
            st.success("Data submitted successfully!")
            st.session_state.data = pd.DataFrame(columns=["EMP ID", "Name", "Contact No", "Email", "Department", "Trainer"])  # Reset data

# Main function
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_form()

if __name__ == "__main__":
    main()
