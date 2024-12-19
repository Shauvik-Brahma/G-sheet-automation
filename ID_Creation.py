import streamlit as st
import pandas as pd
import re

# Google Sheets Integration
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Function to authenticate Google Sheets
def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('path_to_your_credentials.json', scope)
    client = gspread.authorize(creds)
    return client

# Function to update Google Sheet
def update_google_sheet(sheet_name, data):
    try:
        client = authenticate_google_sheets()
        sheet = client.open("Your Google Sheet Name").worksheet(sheet_name)
        sheet.append_rows(data)
        return True
    except Exception as e:
        st.error(f"Failed to update Google Sheets: {e}")
        return False

# Function to display login page
def show_login_page():
    st.title("Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    center = st.selectbox("Select Center", [
        "KOLKATA", "INDORE-TARUS", "MYSORE-TTBS",
        "BHOPAL-TTBS", "RANCHI-AYUDA", "BHOPAL-MGM",
        "COIM-HRHNXT", "NOIDA-ICCS", "HYD-CORPONE", "VIJAYAWADA-TTBS"
    ])
    employee_type = st.selectbox("Select Employee Type", ["SLT", "DCS"])
    process = st.selectbox("Select Process", ["Collection", "Non_Collection", "Customer Support"])
    batch_no = st.text_input("Batch No:")

    if st.button("Login"):
        if not batch_no:
            st.error("Please enter a Batch No!")
        elif username == "admin" and password == "admin":
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.center = center
            st.session_state.employee_type = employee_type
            st.session_state.process = process
            st.session_state.batch_no = batch_no
            st.session_state.data = []
        else:
            st.error("Invalid username or password")

# Helper functions for validation
def is_valid_email(email):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

def is_valid_contact_number(contact_number):
    return contact_number.isdigit() and len(contact_number) == 10

# Function to display the form
def show_form():
    st.title("Fill the Form")

    department_options = {
        "Collection": ["Consent", "LROD", "Collection"],
        "Non_Collection": [
            "SE_Onboarding", "ST_Onboarding", "SIB_Onboarding", "SIC_Onboarding",
            "SE_Credit check", "SIC_Credit check", "GRO inbound", "V_KYC", "Risk",
            "SIB_Credit check", "ST_Credit check", "CC_NO_Loan", "CC_Initiator_SIC",
            "CC_Initiator_Student", "CC_Initiator_SE", "CC_Initiator_SIB", "RRR"
        ],
        "Customer Support": ["Email"]
    }

    if st.session_state.center == "KOLKATA":
        emp_id = st.text_input("EMP ID")
        agent_name = st.text_input("Agent Name")
        contact_no = st.text_input("Contact No:")
        official_email = st.text_input("Official Email ID:")
        department = st.selectbox("Department Name:", department_options[st.session_state.process])
        trainer_name = st.text_input("Trainer Name:")

        designation = st.text_input("Designation:") if st.session_state.employee_type == "SLT" else None

        if st.button("Add Row"):
            if not all([emp_id, agent_name, contact_no, official_email, department, trainer_name]):
                st.error("Please fill in all fields!")
            elif not is_valid_email(official_email):
                st.error("Invalid email address!")
            elif not is_valid_contact_number(contact_no):
                st.error("Contact number must be 10 digits!")
            elif st.session_state.employee_type == "SLT" and not designation:
                st.error("Designation is required for SLT employees!")
            else:
                row = [emp_id, agent_name, contact_no, official_email, department, trainer_name, designation or ""]
                st.session_state.data.append(row)
                st.success("Row added successfully!")
    else:
        emp_id = st.text_input("EMP ID")
        candidate_name = st.text_input("Candidate Name")
        mobile_no = st.text_input("Mobile No.")
        mail_id = st.text_input("Mail ID")
        process_name = st.text_input("Process Name")
        trainer = st.text_input("Trainer")

        if st.button("Add Row"):
            if not all([emp_id, candidate_name, mobile_no, mail_id, process_name, trainer]):
                st.error("Please fill in all fields!")
            elif not is_valid_email(mail_id):
                st.error("Invalid email address!")
            elif not is_valid_contact_number(mobile_no):
                st.error("Mobile number must be 10 digits!")
            else:
                row = [emp_id, candidate_name, mobile_no, mail_id, process_name, trainer]
                st.session_state.data.append(row)
                st.success("Row added successfully!")

    if st.session_state.data:
        st.write("Input Data:")
        df = pd.DataFrame(st.session_state.data, columns=[
            "EMP ID", "Name", "Contact No", "Email", "Department/Process", "Trainer", "Designation (if any)"
        ])
        st.dataframe(df)

        if st.button("Submit"):
            sheet_name = "Kolkata" if st.session_state.center == "KOLKATA" else "Partner"
            if update_google_sheet(sheet_name, st.session_state.data):
                st.success("Data submitted successfully!")
                st.session_state.data.clear()

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
