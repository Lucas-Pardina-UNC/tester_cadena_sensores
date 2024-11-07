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
            #print(f"File saved successfully to '{file_path}'.")
            return True  # Return True on success
        except PermissionError:
            print(f"Permission denied: Close the Excel file '{file_path}' and try again.")
            input("Press Enter when the file is closed...")  # Wait for user confirmation
        except InvalidFileException as e:
            print(f"Error saving file: {e}")
            return False  # Return False on error
        
def log_to_excel(log_data, timestamp=None, chain_id=0, filename="modbus_test_log.xlsx"):
    """Logs data to an Excel file with columns for timestamp, Slave ID, ADC label, ADC value, and temperature,
       starting in a specified column set based on chain_id."""
    
    # Check if the file exists
    if os.path.exists(filename):
        # If the file exists, open it
        workbook = openpyxl.load_workbook(filename)
        #print(f"Opened existing file: {filename}")
    else:
        # If the file does not exist, create a new workbook and add a sheet
        workbook = openpyxl.Workbook()
        print(f"Created new file: {filename}")
        # Select the active sheet
        sheet = workbook.active
        # Rename the active sheet
        sheet.title = "Log Data"
        
    # Select the active sheet
    sheet = workbook.active

    # Calculate the starting column based on chain_id (0 -> A, 1 -> F, 2 -> K, etc.), with each dataset taking 5 columns
    start_column = 1 + (chain_id * 5)  # Each chain_id starts 5 columns apart
    
    # Write headers if they're not present in the specified starting column
    if sheet.cell(row=1, column=start_column).value != "Timestamp":
        sheet.cell(row=1, column=start_column, value="Timestamp")  
        sheet.cell(row=1, column=start_column + 1, value="Slave_ID")  
        sheet.cell(row=1, column=start_column + 2, value="ADC_Value")  
        sheet.cell(row=1, column=start_column + 3, value="Temperature") 

    # Find the first empty row within the specific columns for the chain_id
    data_write_row = 2  # Start after header row
    while sheet.cell(row=data_write_row, column=start_column).value is not None or \
          sheet.cell(row=data_write_row, column=start_column + 1).value is not None or \
          sheet.cell(row=data_write_row, column=start_column + 2).value is not None or \
          sheet.cell(row=data_write_row, column=start_column + 3).value is not None:
        data_write_row += 1

    # Write each entry from log_data to the specified row and columns
    for entry in log_data:
        sheet.cell(row=data_write_row, column=start_column, value=timestamp)  # Timestamp
        sheet.cell(row=data_write_row, column=start_column + 1, value=entry[0])  # Slave_ID
        sheet.cell(row=data_write_row, column=start_column + 2, value=entry[1])  # ADC Value
        sheet.cell(row=data_write_row, column=start_column + 3, value=entry[2])  # Temperature
        data_write_row += 1  # Move to the next row for each log entry

    # Format cells
    center_and_adjust_columns(sheet)

    # Save the workbook
    save_workbook_safely(filename, workbook)
    #print(f"Data logged to {filename} in columns starting at {chr(64 + start_column)}")