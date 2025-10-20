import msal
import webbrowser
from flask import Flask, request

# --- Configuration ---
AUTHORITY = "https://login.microsoftonline.com/55c9946b-4d69-4dab-9fdc-7ebd09ac4156"
CLIENT_ID = "45f60fac-1199-46d4-be2a-3ea2565f8aa2"
REDIRECT_URI = "http://localhost:5200/callback"

# Change scope to Azure Storage
STORAGE_SCOPE = ["https://storage.azure.com/.default"]
# ---------------------

app_msal = msal.PublicClientApplication(
    CLIENT_ID,
    authority=AUTHORITY
)

# Step 1: Initiate auth code flow
flow = app_msal.initiate_auth_code_flow(scopes=STORAGE_SCOPE, redirect_uri=REDIRECT_URI)
print("Opening browser for authentication...")
webbrowser.open(flow['auth_uri'])

# Step 2: Setup Flask to catch the redirect with the authorization code
flask_app = Flask(__name__)

@flask_app.route("/callback")
def callback():
    try:
        result = app_msal.acquire_token_by_auth_code_flow(flow, request.args)
        access_token = result.get("access_token")
        if access_token:
            print("Authentication successful!")
            print("Access token:", access_token)
            return "Authentication complete! You can close this browser window."
        else:
            return f"Authentication failed: {result.get('error_description')}"
    except Exception as e:
        return f"Authentication failed: {e}"

if __name__ == "__main__":
    flask_app.run(port=5200)
