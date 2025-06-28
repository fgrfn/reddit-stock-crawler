import os
from dotenv import load_dotenv

# Load .env once when this module is imported
load_dotenv(dotenv_path="secret.env")

def get_config():
    """
    Reads environment configuration from .env file
    and returns a structured config dictionary.
    """
    config = {
        "reddit": {
            "client_id": os.getenv("REDDIT_CLIENT_ID"),
            "client_secret": os.getenv("REDDIT_CLIENT_SECRET"),
            "user_agent": os.getenv("REDDIT_USER_AGENT"),
        },
        "webhook_url": os.getenv("WEBHOOK_URL"),
        "google_sheets": {
            "keyfile": os.getenv("GOOGLE_SHEETS_KEYFILE"),
            "spreadsheet": os.getenv("GOOGLE_SHEETS_SPREADSHEET"),
        },
        "cleanup_days": int(os.getenv("CLEANUP_DAYS", 7))
    }

    return config
