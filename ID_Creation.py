import streamlit as st
import pandas as pd

# Define a simple username and password for login
USERNAME = "admin"
PASSWORD = "admin"

# Initialize session state for data and login status if they don't exist
if 'data' not in st.session_state:
    st.session_state.data = []

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Add Row Functionality
def add_row(name, age, city):
    st.session_state.data.append([name, age, city])

# Delete Row Functionality
def delete_row(row_to_delete):
    if 1 <= row_to_delete <= len(st.session_state.data):
        st.session_state.data.pop(row_to_delete - 1)
        return True
    return False

# Login Page Functionality
def login_page():
    st.title("Login Page")

    # Input fields for username and password
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    # Check login button
    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("Login successful!")
        else:
            st.error("Invalid username or password.")

# Streamlit Data Entry and Management Page
def data_management_page():
    st.title("Data Entry and Management")

    # Add Row Form
    with st.form(key="data_entry_form"):
        name = st.text_input("Enter your name:")
        age = st.number_input("Enter your age:", min_value=1)
        city = st.text_input("Enter your city:")

        # Submit button to add a new row
        submit_button = st.form_submit_button("Add Row")
        if submit_button:
            if name and city:  # Ensure data is not empty
                add_row(name, age, city)
                st.success(f"Row with Name: {name}, Age: {age}, City: {city} added successfully!")
            else:
                st.error("Please fill all fields.")

    # Displaying the table of all added rows
    if st.session_state.data:
        st.write("Your Input Table:")
        df = pd.DataFrame(st.session_state.data, columns=["Name", "Age", "City"])
        st.dataframe(df)

        # Delete Row functionality
        row_to_delete = st.number_input(
            "Enter Row Number to Delete (1-based index):",
            min_value=1,
            max_value=len(df),
            step=1,
            key="row_to_delete"  # Unique key for this widget
        )

        # Delete row button
        delete_button = st.button("Delete Row", key="delete_button")

        if delete_button:
            # Ensure the row number is valid and delete the row
            if delete_row(row_to_delete):
                st.success(f"Row {row_to_delete} deleted successfully!")
            else:
                st.error("Invalid row number. Please try again.")
    else:
        st.write("No data available yet.")

    # Submit button for the form
    if st.button("Submit"):
        if st.session_state.data:
            st.write("Form submitted successfully!")
            # Process the form data here as needed
            st.write(f"Collected Data: {st.session_state.data}")
        else:
            st.error("No rows to submit. Please add some rows first.")

# Main Application Logic
if not st.session_state.logged_in:
    # If not logged in, show the login page
    login_page()
else:
    # If logged in, show the data management page
    data_management_page()
