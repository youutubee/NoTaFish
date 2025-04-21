import json
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Constants
CREDS_FILE = 'captured_credentials.json'


def initialize_creds_file():
    """Initialize the credentials file if it doesn't exist"""
    if not os.path.exists(CREDS_FILE):
        with open(CREDS_FILE, 'w') as f:
            json.dump({}, f)
        logger.info(f"Created new credentials file: {CREDS_FILE}")


def save_credentials(user_id, creds):
    """Save captured credentials to JSON file"""
    try:
        # Load existing data
        with open(CREDS_FILE, 'r') as f:
            all_creds = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_creds = {}

    # Add credentials to user's collection
    if user_id not in all_creds:
        all_creds[user_id] = []

    all_creds[user_id].append(creds)

    # Save updated data
    with open(CREDS_FILE, 'w') as f:
        json.dump(all_creds, f, indent=2)

    logger.info(f"Saved credentials for user {user_id}")


def get_user_history(user_id):
    """Get a user's credential capture history"""
    try:
        with open(CREDS_FILE, 'r') as f:
            all_creds = json.load(f)

        if user_id in all_creds and all_creds[user_id]:
            # User has captured credentials
            count = len(all_creds[user_id])

            # Get the most recent 5 captures
            recent = all_creds[user_id][-5:]

            return {
                "success": True,
                "count": count,
                "recent": recent
            }
        else:
            # No credentials captured yet
            return {
                "success": True,
                "count": 0,
                "recent": []
            }
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "success": False,
            "error": "No credentials history found"
        }