import streamlit as st
import pickle
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the Gmail API scope
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    creds = None

    # Build the credentials JSON from Streamlit secrets
    credentials_json = {
        "installed": {
            "client_id": st.secrets["gmail"]["client_id"],
            "client_secret": st.secrets["gmail"]["client_secret"],
            "auth_uri": st.secrets["gmail"]["auth_uri"],
            "token_uri": st.secrets["gmail"]["token_uri"],
            "redirect_uris": st.secrets["gmail"]["redirect_uris"]
        }
    }

    # Write the credentials to a temp file (required by InstalledAppFlow)
    with open("temp_credentials.json", "w") as f:
        json.dump(credentials_json, f)

    # Initialize OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file("temp_credentials.json", SCOPES)
    auth_url, _ = flow.authorization_url(prompt="consent")

    # Step 1: Show the auth link
    st.write("### Step 1: Click the link below to authenticate:")
    st.markdown(f"[Authenticate with Google]({auth_url})", unsafe_allow_html=True)

    # Step 2: Get the code from the user
    auth_code = st.text_input("### Step 2: Paste the authorization code here:")

    if auth_code:
        try:
            flow.fetch_token(code=auth_code)
            creds = flow.credentials

            # Save token for reuse
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

            # Cleanup and notify user
            os.remove("temp_credentials.json")
            st.session_state["authenticated"] = True
            st.success("✅ Authentication successful! Token saved.")
            return creds
        except Exception as e:
            st.error(f"❌ Authentication failed: {str(e)}")

    return None

# Streamlit UI
st.title("📧 Gmail Authentication for Personal Accounts")

# Session state to remember if already authenticated
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    authenticate_gmail()
else:
    st.success("🎉 You're already authenticated!")
