from msal import PublicClientApplication
import json

# Public client ID for Power BI (Microsoft's official client)
CLIENT_ID = "ea0616ba-638b-4df5-95b9-636659ae5121"
AUTHORITY = "https://login.microsoftonline.com/organizations"
SCOPE = ["https://analysis.windows.net/powerbi/api/.default"]

# Create application instance
app = PublicClientApplication(
    CLIENT_ID,
    authority=AUTHORITY
)

# Interactive login
result = app.acquire_token_interactive(scopes=SCOPE)

if "access_token" in result:
    print("✓ Token acquired successfully!")
    print("\nYour Access Token:")
    print(result["access_token"])
    print("\nExpires at:", result.get("expires_in"), "seconds")
else:
    print("Error:", result.get("error"))
    print("Description:", result.get("error_description"))