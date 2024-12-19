import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

# Function to connect to Google Sheets
def connect_to_google_sheets(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1Rrxrjo_id38Rpl1H7Vq30ZsxxjUOvWiFQhfexn-LJlE/edit#gid=0")
    return sheet.worksheet(sheet_name)

# Function to display login page
def show_login_page():
    st.title("Login Page")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    employee_type = st.selectbox("Select Employee Type", ["SLT", "DCS"])
    process = st.selectbox("Select Process", ["Collection", "Non_Collection", "Customer Support"])
    Batch_No = st.text_input("Batch No:")
    
    if st.button("Login"):
        if not Batch_No:
            st.error("Please enter a Batch No!")
        elif username == "admin" and password == "admin":  # Simple login check
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.employee_type = employee_type
            st.session_state.process = process
            st.session_state.Batch_No = Batch_No
            st.session_state.form_displayed = True
            st.session_state.data = []
        else:
            st.error("Invalid username or password")

# Function to validate email format
def is_valid_email(email):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

# Function to validate contact number
def is_valid_contact_number(contact_number):
    return contact_number.isdigit() and len(contact_number) == 10

# Function to display the form for Kolkata center
def show_form():
    st.title("Fill the Form")

    if "data" not in st.session_state:
        st.session_state.data = []

    department_options = {
        "Collection": ["Consent", "LROD", "Collection"],
        "Non_Collection": ["SE_Onbording", "ST_Onbording", "SIB_Onbording", "SIC_Onbording", 
                           "SE_Credit check", "SIC_Credit check", "GRO inbound", "V_KYC", 
                           "Risk", "SIB_Credit check", "ST_Credit check", "CC_NO_Loan", 
                           "CC_Initiator_SIC", "CC_Initiator_Student", "CC_Initiator_SE", 
                           "CC_Initiator_SIB", "RRR"],
        "Customer Support": ["Email"]
    }

    emp_id = st.text_input("EMP ID", key="emp_id")
    agent_name = st.text_input("Agent Name", key="agent_name")
    contact_no = st.text_input("Contact No:", key="contact_no")
    official_email = st.text_input("Official Email_ID:", key="official_email")
    department = st.selectbox("Department Name:", department_options[st.session_state.process])
    trainer_name = st.text_input("Trainer Name:", key="trainer_name")

    if st.session_state.employee_type == "SLT":
        designation = st.text_input("Designation:", key="designation")
    else:
        designation = None

    if st.button("Add Row", key="add_row"):
        if not emp_id or not agent_name or not contact_no or not official_email or not department or not trainer_name:
            st.error("Please fill in all fields!")
        elif not is_valid_email(official_email):
            st.error("Invalid email address.")
        elif not is_valid_contact_number(contact_no):
            st.error("Contact number must be 10 digits.")
        elif st.session_state.employee_type == "SLT" and not designation:
            st.error("Designation required for SLT employees.")
        else:
            new_row = {
                "EMP ID": emp_id,
                "Agent Name": agent_name,
                "Contact No": contact_no,
                "Official Email_ID": official_email,
                "Department": department,
                "Trainer Name": trainer_name,
                "Designation": designation if designation else ""
            }
            st.session_state.data.append(new_row)
            st.success("Row added successfully!")

    if st.session_state.data:
        st.write("Your Input Table:")
        df = pd.DataFrame(st.session_state.data)
        st.dataframe(df)

    if st.button("Submit"):
        if st.session_state.data:
            try:
                worksheet = connect_to_google_sheets("K")
                for row in st.session_state.data:
                    worksheet.append_row(list(row.values()))
                st.success("Data successfully added to Google Sheets!")
                st.session_state.data = []  # Clear data after submission
            except Exception as e:
                st.error(f"Failed to submit data: {e}")
        else:
            st.error("No rows to submit.")

# Main function
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.form_displayed = False

    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_form()

if __name__ == "__main__":
    main()
