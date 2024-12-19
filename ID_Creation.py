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
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zAZ0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

# Function to validate contact number (must be exactly 10 digits)
def is_valid_contact_number(contact_number):
    return contact_number.isdigit() and len(contact_number) == 10

# Function to display login page
def show_login_page():
    st.title("Login Page")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    center = st.selectbox("Select Center", ["KOLKATA", "INDORE-TARUS", "MYSORE-TTBS", 
                                            "BHOPAL-TTBS", "RANCHI-AYUDA", "BHOPAL-MGM", 
                                            "COIM-HRHNXT", "NOIDA-ICCS", "HYD-CORPONE", 
                                            "VIJAYAWADA-TTBS"])
    
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
            st.session_state.data = []  # Initialize the data
            st.session_state.form_displayed = True
            st.success("Logged in successfully!")
        else:
            st.error("Invalid username or password")

# Function to display the form and handle data
def show_form():
    st.title("Fill the Form")

    # Initialize data if not already initialized
    if "data" not in st.session_state:
        st.session_state.data = []

    # Define department options based on process
    department_options = {
        "Collection": ["Consent", "LROD", "Collection"],
        "Non_Collection": ["SE_Onbording", "SIC_Onbording", "Risk"],
        "Customer Support": ["Email"]
    }

    if st.button("Refresh Table"):
        st.session_state.show_table = True  # Refresh table

    if "show_table" in st.session_state and st.session_state.show_table:
        st.subheader("Current Data")
        if st.session_state.data:
            df = pd.DataFrame(st.session_state.data)
            st.dataframe(df)

            # Delete Row functionality
            row_to_delete = st.number_input(
                "Enter Row Number to Delete (1-based index):",
                min_value=1,
                max_value=len(df),
                step=1
            )
            if st.button("Delete Row"):
                if 1 <= row_to_delete <= len(df):
                    st.session_state.data.pop(row_to_delete - 1)  # Remove the selected row
                    st.session_state.show_table = True  # Refresh table
                    st.success(f"Row {row_to_delete} deleted successfully!")
                else:
                    st.error("Invalid row number.")
        else:
            st.write("No rows added yet.")

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
                new_row = {
                    "EMP ID": emp_id,
                    "Name": name,
                    "Contact No": contact_no,
                    "Email": email,
                    "Department": department,
                    "Trainer": trainer
                }
                st.session_state.data.append(new_row)
                st.success("Row added successfully!")

    # Submit button to save data to Google Sheets
    if st.button("Submit Data"):
        if not st.session_state.data:
            st.error("No data to submit. Add some rows first.")
        else:
            client = connect_to_google_sheets()

            # Select the appropriate sheet based on the center
            if st.session_state.center == "KOLKATA":
                sheet = client.open_by_key("1Rrxrjo_id38Rpl1H7Vq30ZsxxjUOvWiFQhfexn-LJlE").worksheet("Kolkata")
            else:
                sheet = client.open_by_key("1Rrxrjo_id38Rpl1H7Vq30ZsxxjUOvWiFQhfexn-LJlE").worksheet("Partner")

            # Add login details to each row and submit to Google Sheets
            for row in st.session_state.data:
                row["Username"] = st.session_state.username
                row["Password"] = st.session_state.password
                row["Center"] = st.session_state.center
                row["Employee Type"] = st.session_state.employee_type
                row["Process"] = st.session_state.process
                row["Batch No"] = st.session_state.batch_no
                row["Login Time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Append each row to the selected Google Sheet
                sheet.append_row(list(row.values()))
            st.success("Data submitted successfully!")
            st.session_state.data = []  # Clear data after submission

# Main function to control the flow of the app
def main():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        show_login_page()
    else:
        show_form()

if __name__ == "__main__":
    main()
