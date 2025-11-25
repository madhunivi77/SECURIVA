"""
Salesforce OAuth token management utilities
"""
import os
import json
import time
import requests
from pathlib import Path


def get_oauth_file_path():
    """Get the path to oauth.json file"""
    return Path(__file__).parent / "oauth.json"


def load_oauth_data():
    """Load oauth.json data"""
    with open(get_oauth_file_path(), "r") as f:
        return json.load(f)


def save_oauth_data(data):
    """Save data to oauth.json"""
    with open(get_oauth_file_path(), "w") as f:
        json.dump(data, f, indent=2)


def refresh_salesforce_token(user_id):
    """
    Refresh Salesforce access token using refresh token.

    Args:
        user_id: The user ID to refresh tokens for

    Returns:
        dict: Updated credentials with new access_token, or None if refresh failed
    """
    try:
        # Load current credentials
        data = load_oauth_data()

        # Find user
        user = None
        for u in data.get("users", []):
            if u["user_id"] == user_id:
                user = u
                break

        if not user:
            print(f"User {user_id} not found in oauth.json")
            return None

        # Get Salesforce service data
        sf_service = user.get("services", {}).get("salesforce")
        if not sf_service:
            print(f"Salesforce service not configured for user {user_id}")
            return None

        sf_creds = sf_service.get("credentials")
        if not sf_creds or "refresh_token" not in sf_creds:
            print(f"No refresh token found for user {user_id}")
            return None

        refresh_token = sf_creds["refresh_token"]

        # Get environment variables
        SF_CLIENT_ID = os.getenv("SF_CLIENT_ID")
        SF_CLIENT_SECRET = os.getenv("SF_CLIENT_SECRET")
        SF_DOMAIN = os.getenv("SF_DOMAIN", "login")

        if not SF_CLIENT_ID or not SF_CLIENT_SECRET:
            print("Salesforce credentials not configured in environment")
            return None

        # Request new access token
        token_url = f"https://{SF_DOMAIN}.salesforce.com/services/oauth2/token"

        print(f"Refreshing Salesforce token for user {user_id}...")

        response = requests.post(
            token_url,
            data={
                "grant_type": "refresh_token",
                "client_id": SF_CLIENT_ID,
                "client_secret": SF_CLIENT_SECRET,
                "refresh_token": refresh_token
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )

        if response.status_code == 200:
            new_token_data = response.json()

            # Update stored credentials
            sf_creds["access_token"] = new_token_data["access_token"]
            sf_creds["issued_at"] = new_token_data["issued_at"]
            sf_creds["signature"] = new_token_data.get("signature", sf_creds.get("signature"))

            # Save updated credentials
            save_oauth_data(data)

            print(f"Token refreshed successfully for user {user_id}")
            return sf_creds
        else:
            error_data = response.json() if response.headers.get("content-type") == "application/json" else {}
            error_msg = error_data.get("error", "unknown")
            error_desc = error_data.get("error_description", response.text)

            print(f"Token refresh failed for user {user_id}: {error_msg} - {error_desc}")

            # If refresh token is invalid, user needs to re-authenticate
            if error_msg == "invalid_grant":
                print("Refresh token is invalid. User must re-authenticate with Salesforce.")

            return None

    except Exception as e:
        print(f"Error refreshing Salesforce token for user {user_id}: {e}")
        return None


def should_refresh_token(issued_at_ms):
    """
    Check if token should be refreshed based on age.
    Tokens are refreshed if older than 90 minutes (5400 seconds).

    Args:
        issued_at_ms: Token issue timestamp in milliseconds

    Returns:
        bool: True if token should be refreshed
    """
    if not issued_at_ms:
        return True

    try:
        issued_at_sec = int(issued_at_ms) / 1000
        current_time = time.time()
        age_seconds = current_time - issued_at_sec

        # Refresh if older than 90 minutes (5400 seconds)
        # This gives 30 minute buffer before typical 2-hour expiration
        return age_seconds > 5400
    except (ValueError, TypeError):
        # If we can't parse the timestamp, refresh to be safe
        return True


def get_fresh_salesforce_credentials(user_id, current_creds):
    """
    Get fresh Salesforce credentials, refreshing if necessary.

    Args:
        user_id: The user ID
        current_creds: Current stored credentials

    Returns:
        dict: Fresh credentials, or None if refresh failed
    """
    if not current_creds:
        return None

    issued_at = current_creds.get("issued_at")

    if should_refresh_token(issued_at):
        print(f"Token is stale (issued_at: {issued_at}), refreshing...")
        refreshed_creds = refresh_salesforce_token(user_id)
        return refreshed_creds if refreshed_creds else current_creds

    return current_creds
