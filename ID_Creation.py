import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Connect to Google Sheets API
def connect_to_google_sheets():
    # Use Streamlit secrets for credentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    return client.open_by_key("1Rrxrjo_id38Rpl1H7Vq30ZsxxjUOvWiFQhfexn-LJlE").worksheet("Kolkata")

# Streamlit form
def main():
    st.title('Kolkata Sheet Data Entry')

    # Create a form in Streamlit
    with st.form(key='data_form'):
        name = st.text_input('Name')
        email = st.text_input('Email')
        phone = st.text_input('Phone Number')
        submit_button = st.form_submit_button(label='Submit')

        # If form is submitted, send data to Google Sheets
        if submit_button:
            if name and email and phone:
                # Connect to Google Sheets
                sheet = connect_to_google_sheets()

                # Append data to the sheet
                sheet.append_row([name, email, phone])

                st.success('Data successfully added to the sheet!')
            else:
                st.error('Please fill in all fields.')

if __name__ == "__main__":
    main()
