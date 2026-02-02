import msal
import webbrowser
from flask import Flask, request, jsonify

# --- Configuration ---
AUTHORITY = "https://login.microsoftonline.com/55c9946b-4d69-4dab-9fdc-7ebd09ac4156"
CLIENT_ID = "45f60fac-1199-46d4-be2a-3ea2565f8aa2"
REDIRECT_URI = "http://localhost:5200/callback"

# request offline_access to receive a refresh token
SCOPES = ["https://storage.azure.com/.default", "offline_access"]

app_msal = msal.PublicClientApplication(
    CLIENT_ID,
    authority=AUTHORITY
)

# In-memory token store (replace with DB in production)
user_tokens = {}

# Create the flow with login_hint to prefill abc@knauf.com
login_email = "abc@knauf.com"
flow = app_msal.initiate_auth_code_flow(
    scopes=SCOPES,
    redirect_uri=REDIRECT_URI,
    # pass additional query params. login_hint prefills the email:
    login_hint=login_email,
    # optional: prompt can force account selection or consent
    prompt="select_account",
    # optional: domain_hint can hint tenant type ("organizations"|"consumers"|"none")
    # domain_hint="organizations"
)

print("Open this URL to sign-in (it will prefill the email):")
print(flow["auth_uri"])

# Optionally open browser locally
webbrowser.open(flow["auth_uri"])

flask_app = Flask(__name__)

@flask_app.route("/callback")
def callback():
    try:
        # Complete code flow and exchange code for tokens
        result = app_msal.acquire_token_by_auth_code_flow(flow, request.args)
        if "error" in result:
            return f"Auth error: {result.get('error_description')}"

        access_token = result.get("access_token")
        refresh_token = result.get("refresh_token")
        id_claims = result.get("id_token_claims", {})

        # Try multiple claims for email (preferred_username, upn, email)
        email = id_claims.get("preferred_username") or id_claims.get("upn") or id_claims.get("email")
        user_id = id_claims.get("oid") or id_claims.get("sub")  # unique id

        if not user_id:
            return "Could not determine user id from id_token_claims", 400

        # store tokens linked to user_id (and email if available)
        user_tokens[user_id] = {
            "email": email,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "id_claims": id_claims
        }

        return (
            f"Authentication complete for {email or user_id}. "
            "You can close this window."
        )
    except Exception as e:
        return f"Authentication failed: {e}", 500

@flask_app.route("/tokens/<user_id>")
def get_tokens(user_id):
    tokens = user_tokens.get(user_id)
    if not tokens:
        return "No tokens for that user", 404
    return jsonify(tokens)

if __name__ == "__main__":
    flask_app.run(port=5200)
