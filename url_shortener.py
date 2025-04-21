import requests
import os
import logging
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get Bit.ly token
BITLY_ACCESS_TOKEN = os.getenv("BITLY_ACCESS_TOKEN")


def validate_bitly_token():
    """Validate that the Bit.ly access token is available"""
    if not BITLY_ACCESS_TOKEN:
        logger.warning("BITLY_ACCESS_TOKEN not found in .env file. URL shortening will be disabled.")
        return False
    logger.info("Bit.ly API token loaded successfully.")
    return True


def shorten_url(long_url):
    """Shorten a URL using the Bit.ly API"""
    # Check if token exists
    if not BITLY_ACCESS_TOKEN:
        logger.warning("No Bit.ly access token. Returning original URL.")
        return long_url

    try:
        headers = {
            'Authorization': f'Bearer {BITLY_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        payload = {
            'long_url': long_url
        }
        response = requests.post('https://api-ssl.bitly.com/v4/shorten', headers=headers, json=payload)

        if response.status_code == 200:
            return response.json().get('link')
        else:
            logger.error(f"Bit.ly API error: {response.status_code} - {response.text}")
            return long_url  # Return original URL if shortening fails
    except Exception as e:
        logger.error(f"Error shortening URL with Bit.ly: {e}")
        return long_url  # Return original URL if shortening fails