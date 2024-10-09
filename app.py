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
    """List and log all worksheets in the spreadsheet."""
    try:
        worksheet_list = spreadsheet.worksheets()
        logger.info(f"Worksheets in the spreadsheet: {worksheet_list}")
        return worksheet_list
    except Exception as e:
        logger.exception("Failed to retrieve worksheets: %s", str(e))
        return []


# Function to create a new worksheet
def create_new_worksheet(spreadsheet):
    """Prompt the user to create a new worksheet."""
    sheet_name = input("Enter the name of the new worksheet: ")
    rows = int(input("Enter the number of rows: "))
    cols = int(input("Enter the number of columns: "))

    try:
        worksheet = spreadsheet.add_worksheet(
            title=sheet_name, rows=str(rows), cols=str(cols)
        )
        logger.info(
            f"New worksheet '{sheet_name}' created with "
            f"{rows} rows and {cols} columns."
        )
        return worksheet
    except Exception as e:
        logger.exception("Failed to create new worksheet: %s", str(e))
        return None


def select_worksheet(spreadsheet):
    """Allow the user to select a worksheet from the spreadsheet."""
    worksheets = list_worksheets(spreadsheet)

    if not worksheets:
        print("No worksheets found.")
        return None

    print("Available Worksheets:")
    for idx, worksheet in enumerate(worksheets, 1):
        print(f"{idx}. {worksheet.title}")

    try:
        selection = int(input("Select a worksheet by number: "))
        if 1 <= selection <= len(worksheets):
            selected_worksheet = worksheets[selection - 1]
            logger.info(f"Selected worksheet: {selected_worksheet.title}")
            return selected_worksheet
        else:
            print("Invalid selection.")
            return None
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None


def display_worksheet_data(worksheet):
    """Display the contents of the selected worksheet."""
    try:
        data = worksheet.get_all_values()
        if data:
            print("Worksheet Data:")
            for row in data:
                print(row)
        else:
            print("The worksheet is empty.")
    except Exception as e:
        logger.exception("Failed to retrieve worksheet data: %s", str(e))


def update_student_grade(worksheet):
    """Update a student's grade for a specific assignment."""
    student_id = input("Enter the Student ID: ")
    grade_column = int(
        input(
            "Enter column number to update grade (e.g., 3 for Assignment 1): "
        )
    )
    new_grade = input("Enter the new grade: ")

    try:
        cell = worksheet.find(student_id)
        worksheet.update_cell(cell.row, grade_column, new_grade)
        print(f"Updated grade for Student ID {student_id} to {new_grade}.")
    except Exception as e:
        logger.exception(
            f"Failed to update grade for {student_id}: %s", str(e)
        )


def update_student_attendance(worksheet):
    """Update attendance for a student."""
    student_id = input("Enter the Student ID: ")
    try:
        cell = worksheet.find(student_id)
        attendance_cell = worksheet.cell(
            cell.row, 7
        )  # Assume column 7 is attendance count
        attendance_count = int(attendance_cell.value) + 1
        worksheet.update_cell(cell.row, 7, attendance_count)
        print(f"Updated attendance for Student ID {student_id}.")
    except Exception as e:
        logger.exception(
            f"Failed to update attendance for {student_id}: %s", str(e)
        )


def calculate_final_grades(worksheet):
    """Calculate final grades for all students."""
    data = worksheet.get_all_records()
    for i, student in enumerate(data):
        # Assuming weights: 40% Exam, 30% Assignment, 30% Quiz
        final_grade = (
            student["Assignment 1"] * 0.3
            + student["Quiz 1"] * 0.3
            + student["Exam 1"] * 0.4
        )
        worksheet.update_cell(
            i + 2, 6, round(final_grade, 2)
        )  # Column 6 is Final Grade
    print("Final grades calculated and updated.")


def calculate_attendance_percentage(worksheet, total_classes):
    """Calculate attendance percentage for all students."""
    data = worksheet.get_all_records()
    for i, student in enumerate(data):
        attendance_count = student["Attendance Count"]
        attendance_percentage = (attendance_count / total_classes) * 100
        worksheet.update_cell(
            i + 2, 8, round(attendance_percentage, 2)
        )  # Column 8 is Attendance Percentage
    print("Attendance percentages calculated and updated.")


def display_menu():
    """Display a menu for user interaction."""
    print("\n--- Student Grades and Attendance Tracker Menu ---")
    print("1. List Worksheets")
    print("2. Create a New Worksheet")
    print("3. Select a Worksheet")
    print("4. Update a Student's Grade")
    print("5. Update a Student's Attendance")
    print("6. Calculate Final Grades")
    print("7. Calculate Attendance Percentage")
    print("8. Exit")


def main():
    """Main function to execute the entire workflow with a menu."""
    spreadsheet_name, share_to_email = load_env_variables()
    gc = authenticate_with_google()
    spreadsheet = get_or_create_spreadsheet(
        gc, spreadsheet_name, share_to_email
    )
    current_worksheet = None
    total_classes = (
        10  # Set total number of classes for attendance calculation
    )

    while True:
        display_menu()
        try:
            choice = input("Select an option (1/2/3/4/5/6/7/8): ")
        except EOFError:
            print("Input stream closed. Exiting program.")
            break

        if choice == "1":
            worksheets = list_worksheets(spreadsheet)
            print(f"Worksheets: {[ws.title for ws in worksheets]}")
        elif choice == "2":
            create_new_worksheet(spreadsheet)
        elif choice == "3":
            current_worksheet = select_worksheet(spreadsheet)
            if current_worksheet:
                print(f"Current worksheet set to: {current_worksheet.title}")
                display_worksheet_data(current_worksheet)
        elif choice == "4" and current_worksheet:
            update_student_grade(current_worksheet)
        elif choice == "5" and current_worksheet:
            update_student_attendance(current_worksheet)
        elif choice == "6" and current_worksheet:
            calculate_final_grades(current_worksheet)
        elif choice == "7" and current_worksheet:
            calculate_attendance_percentage(current_worksheet, total_classes)
        elif choice == "8":
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid option or no worksheet selected. Please try again.")


# Run the main function
if __name__ == "__main__":
    main()
