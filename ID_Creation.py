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
    
    # Initialize the data table if not already initialized
    if "data" not in st.session_state:
        st.session_state.data = pd.DataFrame(columns=["EMP ID", "Name", "Contact No", "Email", "Department", "Trainer"])

    # Display current data
    st.subheader("Current Data")
    st.dataframe(st.session_state.data)

    # Input fields for adding new rows
    st.subheader("Add New Row")
    with st.form(key="add_row_form"):
        emp_id = st.text_input("EMP ID")
        name = st.text_input("Name")
        contact_no = st.text_input("Contact No")
        email = st.text_input("Email")
        department = st.selectbox("Department", department_options[st.session_state.process])
        trainer = st.text_input("Trainer")
        submit_button = st.form_submit_button("Add Row")

        if submit_button:
            # Validate input
            if not emp_id or not name or not contact_no or not email or not department or not trainer:
                st.error("All fields are required.")
            elif not is_valid_email(email):
                st.error("Invalid email format.")
            elif not is_valid_contact_number(contact_no):
                st.error("Contact number must be exactly 10 digits.")
            else:
                # Add to DataFrame
                new_row = {"EMP ID": emp_id, "Name": name, "Contact No": contact_no, "Email": email, "Department": department, "Trainer": trainer}
                st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
                st.success("Row added successfully!")

    # Delete rows
    if not st.session_state.data.empty:
        st.subheader("Delete Row")
        row_to_delete = st.number_input("Row to Delete (0-based index):", min_value=0, max_value=len(st.session_state.data) - 1, step=1)
        if st.button("Delete Row"):
            st.session_state.data = st.session_state.data.drop(row_to_delete).reset_index(drop=True)
            st.success(f"Row {row_to_delete} deleted successfully.")

    # Submit to Google Sheets
    if st.button("Submit Data"):
        if st.session_state.data.empty:
            st.error("No data to submit. Add some rows first.")
        else:
            # Call function to save data to Google Sheets
            save_to_google_sheets(st.session_state.data)
            st.success("Data submitted successfully!")
            # Clear DataFrame after submission
            st.session_state.data = pd.DataFrame(columns=["EMP ID", "Name", "Contact No", "Email", "Department", "Trainer"])
