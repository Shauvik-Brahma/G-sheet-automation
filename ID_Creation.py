import streamlit as st
import pandas as pd
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# Function to connect to Google Sheets
def connect_to_google_sheets():
    # Define the scope for Google Sheets and Google Drive API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Use the credentials from Streamlit secrets
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    
    # Authenticate with Google Sheets
    client = gspread.authorize(creds)
    
    # Return the authenticated client
    return client

# Function to display login page with "Center" dropdown
def show_login_page():
    st.title("Login Page")
    
    # Username and password input fields
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    
    # Center dropdown for selection
    center = st.selectbox("Select Center", ["KOLKATA", "INDORE-TARUS", "MYSORE-TTBS",
                                            "BHOPAL-TTBS", "RANCHI-AYUDA","BHOPAL-MGM","COIM-HRHNXT"
                                            ,"NOIDA-ICCS", "HYD-CORPONE" , "VIJAYAWADA-TTBS" ])
    
    # Employee Type dropdown
    employee_type = st.selectbox("Select Employee Type", ["SLT", "DCS"])

    # Conditional Process dropdown based on Employee Type and Center
    process = st.selectbox("Select Process", ["Collection", "Non_Collection", "Customer Support"])

    Batch_No = st.text_input("Batch No:")

    # Login button
    if st.button("Login"):
        # Check if the Batch No is provided
        if not Batch_No:
            st.error("Please enter a Batch No!")
        elif username == "admin" and password == "admin":  # Simple login check
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.center = center  # Store selected center in session state
            st.session_state.employee_type = employee_type  # Store selected employee type
            st.session_state.process = process  # Store selected process in session state
            st.session_state.Batch_No = Batch_No
            st.session_state.form_displayed = True  # Flag to track whether form is displayed
            st.session_state.data = []  # Initialize the list to hold the form data

            # Store login information in session_state for use later
            st.session_state.login_info = {
                "Username": username,
                "Password": password,
                "Center": center,
                "Employee Type": employee_type,
                "Process": process,
                "Batch No": Batch_No
            }
        else:
            st.error("Invalid username or password")

# Function to validate email format
def is_valid_email(email):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

# Function to validate contact number (must be exactly 10 digits)
def is_valid_contact_number(contact_number):
    return contact_number.isdigit() and len(contact_number) == 10

# Function to display the form after login
def show_form():
    st.title("Fill the Form")

    # Initialize the data list if it's not already initialized
    if "data" not in st.session_state:
        st.session_state.data = []

    # Department dropdown options based on process
    department_options = {
        "Collection": ["Consent", "LROD", "Collection"],
        "Non_Collection": ["SE_Onbording", "ST_Onbording", "SIB_Onbording", "SIC_Onbording" , "SE_Credit check" , "SIC_Credit check","GRO inbound","V_KYC","Risk"
                          ,"SIB_Credit check", "ST_Credit check","CC_NO_Loan","CC_Initiator_SIC","CC_Initiator_Student","CC_Initiator_SE","CC_Initiator_SIB","RRR"],
        "Customer Support": ["Email"]
    }

    # Form elements for "KOLKATA" center
    if st.session_state.center == "KOLKATA":
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

        # Add Row functionality
        if st.button("Add Row", key="add_row"):
            if not emp_id or not agent_name or not contact_no or not official_email or not department or not trainer_name:
                st.error("Please fill in all fields!")
            elif not is_valid_email(official_email):
                st.error("Please enter a valid email address.")
            elif not is_valid_contact_number(contact_no):
                st.error("Contact number must be 10 digits.")
            elif st.session_state.employee_type == "SLT" and not designation:
                st.error("Please enter the Designation for SLT employees.")
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

    # Form elements for other centers
    else:
        emp_id = st.text_input("EMP ID", key="emp_id")
        candidate_name = st.text_input("Candidate Name", key="candidate_name")
        mobile_no = st.text_input("Mobile No.", key="mobile_no")
        mail_id = st.text_input("Mail ID", key="mail_id")
        process_name = st.text_input("Process Name", key="process_name")
        trainer = st.text_input("Trainer", key="trainer")

        if st.button("Add Row", key="add_row"):
            if not emp_id or not candidate_name or not mobile_no or not mail_id or not process_name or not trainer:
                st.error("Please fill in all fields!")
            elif not is_valid_email(mail_id):
                st.error("Please enter a valid email address.")
            elif not is_valid_contact_number(mobile_no):
                st.error("Mobile number must be 10 digits.")
            else:
                new_row = {
                    "EMP ID": emp_id,
                    "Candidate Name": candidate_name,
                    "Mobile No": mobile_no,
                    "Mail ID": mail_id,
                    "Process Name": process_name,
                    "Trainer": trainer
                }
                st.session_state.data.append(new_row)
                st.success("Row added successfully!")

    # Displaying the table of all added rows
    if st.session_state.data:
        st.write("Your Input Table:")

        # Loop over each row and display it with delete option
        for idx, row in enumerate(st.session_state.data):
            col1, col2 = st.columns([5, 1])  # Create two columns: one for data, one for the delete button
            with col1:
                # Display row as individual columns (fields) rather than as a dict
                st.write(f"**EMP ID**: {row['EMP ID']}")
                st.write(f"**Agent Name**: {row['Agent Name']}")
                st.write(f"**Contact No**: {row['Contact No']}")
                st.write(f"**Official Email_ID**: {row['Official Email_ID']}")
                st.write(f"**Department**: {row['Department']}")
                st.write(f"**Trainer Name**: {row['Trainer Name']}")
                if row.get('Designation'):
                    st.write(f"**Designation**: {row['Designation']}")
            with col2:
                delete_button = st.button(f"Delete Row {idx + 1}", key=f"delete_{idx}")
                if delete_button:
                    st.session_state.data.pop(idx)
                    st.success(f"Row {idx + 1} deleted successfully!")
                    break  # Prevent modifying the list while iterating over it

        # Add a Refresh button to manually reload the data without causing an error
        if st.button("Refresh Table"):
            # Refresh the session state data (effectively reloading the table)
            st.session_state.data = st.session_state.data[:]
            st.success("Table refreshed!")

    # Submit button for the form
    if st.button("Submit"):
        if st.session_state.data:
            client = connect_to_google_sheets()
            
            # Select the appropriate sheet based on the center
            if st.session_state.center == "KOLKATA":
                sheet = client.open_by_key("1Rrxrjo_id38Rpl1H7Vq30ZsxxjUOvWiFQhfexn-LJlE").worksheet("Kolkata")
            else:
                sheet = client.open_by_key("1Rrxrjo_id38Rpl1H7Vq30ZsxxjUOvWiFQhfexn-LJlE").worksheet("Partner")
            
            # Add login details to each form row
            for row in st.session_state.data:
                row["Username"] = st.session_state.login_info["Username"]
                row["Password"] = st.session_state.login_info["Password"]
                row["Center"] = st.session_state.login_info["Center"]
                row["Employee Type"] = st.session_state.login_info["Employee Type"]
                row["Process"] = st.session_state.login_info["Process"]
                row["Batch No"] = st.session_state.login_info["Batch No"]
                row["Login Time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                sheet.append_row(list(row.values()))  # Add each row's values to the sheet

            st.write("Form submitted successfully!")
            st.write(f"Collected Data: {st.session_state.data}")
        else:
            st.error("No rows to submit. Please add some rows first.")

# Main function to control the flow of the app
def main():
    # Initialize session state if not already initialized
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.form_displayed = False  # Ensure form is not displayed by default

    if not st.session_state.logged_in:
        show_login_page()  # Show login page if not logged in
    else:
        show_form()  # Show the form after login

if __name__ == "__main__":
    main()
