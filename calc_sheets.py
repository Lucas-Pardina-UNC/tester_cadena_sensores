import os
import openpyxl  #pip install openpyxl
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from openpyxl.utils.exceptions import InvalidFileException

def center_and_adjust_columns(sheet):
    # Center-align content of all cells that have data
    for row in sheet.iter_rows():
        for cell in row:
            if cell.value is not None:
                cell.alignment = Alignment(horizontal='center')
    
    # Adjust column widths to fit the content
    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter  # Get the letter of the column
        
        for cell in column:
            if cell.value is not None:
                max_length = max(max_length, len(str(cell.value)))
        
        # Set the width with some padding
        adjusted_width = max_length + 2
        sheet.column_dimensions[column_letter].width = adjusted_width

def save_workbook_safely(file_path, workbook):
    while True:
        try:
            workbook.save(file_path)
            print(f"File saved successfully to '{file_path}'.")
            return True  # Return True on success
        except PermissionError:
            print(f"Permission denied: Close the Excel file '{file_path}' and try again.")
            input("Press Enter when the file is closed...")  # Wait for user confirmation
        except InvalidFileException as e:
            print(f"Error saving file: {e}")
            return False  # Return False on error
        
def log_to_excel(log_data, timestamp=None):
    """Logs data to an Excel file with columns for timestamp, ADC label, ADC value, temperature label, and temperature."""
    filename = "modbus_test_log.xlsx"
    
    # Check if the file exists
    if os.path.exists(filename):
        # If the file exists, open it
        workbook = openpyxl.load_workbook(filename)
        print(f"Opened existing file: {filename}")
    else:
        # If the file does not exist, create a new workbook and add a sheet
        workbook = openpyxl.Workbook()
        print(f"Created new file: {filename}")
        # Select the active sheet
        sheet = workbook.active
        # Rename the active sheet
        sheet.title = 'test_1'
        sheet = workbook.active
        sheet.title = "Log Data"
        
        sheet.cell(row=1, column=1, value="Timestamp")  
        sheet.cell(row=1, column=2, value="ADC_Value")  
        sheet.cell(row=1, column=3, value="Temperature") 
        
    # Select the active sheet
    sheet = workbook.active

    # Find the first empty row
    data_write_row = sheet.max_row + 1 # first_empty_row

    # Write each entry from log_data to the specified row
    for entry in log_data:
        sheet.cell(row=data_write_row, column=1, value=timestamp)  # Timestamp
        sheet.cell(row=data_write_row, column=2, value=entry[1])  # ADC Value
        sheet.cell(row=data_write_row, column=3, value=entry[2])  # Temperature
        data_write_row += 1  # Move to the next row for each log entry

    # Format cells
    center_and_adjust_columns(sheet)

    # Save the workbook
    #workbook.save(filename)
    save_workbook_safely(filename,workbook)
    print(f"Data logged to {filename}")