import streamlit as st
import pandas as pd
import re

# Function to display login page with "Center" dropdown
def show_login_page():
    st.title("Login Page")
    
    # Username and password input fields
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    
    # Center dropdown for selection
    center = st.selectbox("Select Center", ["KOLKATA"])
    
    # Employee Type dropdown
    employee_type = st.selectbox("Select Employee Type", ["SLT", "DCS"])

    # Conditional Process dropdown based on Employee Type
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

    # Specific form for Kolkata
    emp_id = st.text_input("EMP ID", key="emp_id")
    agent_name = st.text_input("Agent Name", key="agent_name")
    contact_no = st.text_input("Contact No:", key="contact_no")
    official_email = st.text_input("Official Email_ID:", key="official_email")
    
    # Dynamically show department options based on the selected process
    department = st.selectbox("Department Name:", department_options[st.session_state.process])
    
    trainer_name = st.text_input("Trainer Name:", key="trainer_name")

    # Add a 'Designation' field if Employee Type is SLT
    if st.session_state.employee_type == "SLT":
        designation = st.text_input("Designation:", key="designation")
    else:
        designation = None  # Skip the designation field for other employee types

    # Add Row functionality
    if st.button("Add Row", key="add_row"):
        # Validate inputs before adding a new row
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
                "Designation": designation if designation else ""  # Include designation if provided
            }
            st.session_state.data.append(new_row)
            st.success("Row added successfully!")

    # Displaying the table of all added rows
    if st.session_state.data:
        st.write("Your Input Table:")
        df = pd.DataFrame(st.session_state.data)
        st.dataframe(df)

        # Delete Row functionality
        row_to_delete = st.number_input(
            "Enter Row Number to Delete (1-based index):",
            min_value=1,
            max_value=len(df),
            step=1,
            key="row_to_delete"  # Unique key for this widget
        )

        # Only delete when the "Delete Row" button is pressed
        delete_button = st.button("Delete Row", key="delete_button")  # Unique key for delete button

        if delete_button:
            # Ensure the row number is within valid range and delete the row
            if 1 <= row_to_delete <= len(df):
                st.session_state.data.pop(row_to_delete - 1)
                st.success(f"Row {row_to_delete} deleted successfully!")
                # The table should refresh automatically after this, as the state is updated.

    # Submit button for the form
    if st.button("Submit"):
        if st.session_state.data:
            st.write("Form submitted successfully!")
            # Process the form data here as needed
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
