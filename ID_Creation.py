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

# Function to save data to Google Sheets
def save_to_google_sheets(data):
    client = connect_to_google_sheets()
    if st.session_state.center == "KOLKATA":
        sheet = client.open_by_key("1Rrxrjo_id38Rpl1H7Vq30ZsxxjUOvWiFQhfexn-LJlE").worksheet("Kolkata")
    else:
        sheet = client.open_by_key("1Rrxrjo_id38Rpl1H7Vq30ZsxxjUOvWiFQhfexn-LJlE").worksheet("Partner")

    # Append each row to the Google Sheet
    for _, row in data.iterrows():
        sheet.append_row(row.values.tolist())

# Function to display login page
def show_login_page():
    st.title("Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    center = st.selectbox("Select Center", ["KOLKATA", "INDORE-TARUS", "MYSORE-TTBS", "BHOPAL-TTBS", 
                                            "RANCHI-AYUDA", "BHOPAL-MGM", "COIM-HRHNXT", "NOIDA-ICCS",
                                            "HYD-CORPONE", "VIJAYAWADA-TTBS"])
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
            st.session_state.data = pd.DataFrame(columns=["EMP ID", "Name", "Contact No", "Email", "Department", "Trainer"])
            st.success("Logged in successfully!")
        else:
            st.error("Invalid username or password")

# Function to display the form
def show_form():
    st.title("Fill the Form")

    department_options = {
        "Collection": ["Consent", "LROD", "Collection"],
        "Non_Collection": ["SE_Onbording", "SIC_Onbording", "Risk"],
        "Customer Support": ["Email"]
    }

    st.subheader("Current Data")
    if not st.session_state.data.empty:
        for i, row in st.session_state.data.iterrows():
            cols = st.columns(7)
            cols[0].write(row["EMP ID"])
            cols[1].write(row["Name"])
            cols[2].write(row["Contact No"])
            cols[3].write(row["Email"])
            cols[4].write(row["Department"])
            cols[5].write(row["Trainer"])
            if cols[6].button("Delete", key=f"delete_{i}"):
                st.session_state.data = st.session_state.data.drop(i).reset_index(drop=True)
                st.experimental_rerun()

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
            if not emp_id or not name or not contact_no or not email or not department or not trainer:
                st.error("All fields are required.")
            elif not is_valid_email(email):
                st.error("Invalid email format.")
            elif not is_valid_contact_number(contact_no):
                st.error("Contact number must be exactly 10 digits.")
            else:
                new_row = {"EMP ID": emp_id, "Name": name, "Contact No": contact_no, "Email": email, "Department": department, "Trainer": trainer}
                st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
                st.success("Row added successfully!")

    if st.button("Submit Data"):
        if st.session_state.data.empty:
            st.error("No data to submit. Add some rows first.")
        else:
            save_to_google_sheets(st.session_state.data)
            st.success("Data submitted successfully!")
            st.session_state.data = pd.DataFrame(columns=["EMP ID", "Name", "Contact No", "Email", "Department", "Trainer"])

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
