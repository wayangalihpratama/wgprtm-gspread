import os
import gspread
import logging
from google.oauth2.service_account import Credentials

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_env_variables():
    """
    Load environment variables for
    spreadsheet name and email to share with.
    """
    spreadsheet_name = os.getenv("SPREADSHEET_NAME", "example-spreadsheet")
    share_to_email = os.getenv("SHARE_TO_EMAIL", None)
    return spreadsheet_name, share_to_email


def authenticate_with_google():
    """
    Authenticate using the service account and
    return the authorized gspread client.
    """
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    try:
        credentials = Credentials.from_service_account_file(
            "credentials.json", scopes=scopes
        )
        gc = gspread.authorize(credentials)
        logger.info("Successfully authenticated with Google Sheets API.")
        return gc
    except Exception as e:
        logger.exception("Error during authentication: %s", str(e))
        raise


def get_or_create_spreadsheet(gc, spreadsheet_name, share_to_email=None):
    """
    Try to open the spreadsheet, or create it if it doesn't exist.
    """
    try:
        sh = gc.open(spreadsheet_name)
        logger.info(f"Opened existing spreadsheet: {spreadsheet_name}")
    except gspread.SpreadsheetNotFound:
        logger.info(
            f"Spreadsheet '{spreadsheet_name}' not found, creating a new one."
        )
        sh = gc.create(spreadsheet_name)
        if share_to_email:
            try:
                sh.share(share_to_email, perm_type="user", role="writer")
                logger.info(f"Spreadsheet shared with {share_to_email}")
            except Exception as e:
                logger.exception(
                    f"Failed to share spreadsheet with {share_to_email}: %s",
                    str(e),
                )
    return sh


def list_worksheets(spreadsheet):
    """
    List and log all worksheets in the spreadsheet.
    """
    try:
        worksheet_list = spreadsheet.worksheets()
        logger.info(f"Worksheets in the spreadsheet: {worksheet_list}")
        return worksheet_list
    except Exception as e:
        logger.exception(f"Failed to retrieve worksheets: %s", str(e))
        return []


def main():
    """Main function to execute the entire workflow."""
    spreadsheet_name, share_to_email = load_env_variables()
    gc = authenticate_with_google()
    spreadsheet = get_or_create_spreadsheet(
        gc, spreadsheet_name, share_to_email
    )
    list_worksheets(spreadsheet)


# Run the main function
if __name__ == "__main__":
    main()
