import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope for Google Sheets and Drive API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from Streamlit secrets
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)

# Authorize the client
client = gspread.authorize(creds)

# Open the Google Sheet by name
sheet = client.open("Your Sheet Name")

# Access specific worksheets
kolkata_sheet = sheet.worksheet("Kolkata")
partner_sheet = sheet.worksheet("Partner")
