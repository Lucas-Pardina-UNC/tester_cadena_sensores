""" import asyncio """
import serial.tools.list_ports
""" from pymodbus.client import AsyncModbusSerialClient
from pymodbus import FramerType """
from pymodbus import pymodbus_apply_logging_config
from PS103J2_table import *
from conversion import *
from auto_test import * 
from manual_modbus import *
from get_set_available_slaves import *
from calc_sheets import *
from multiple_chains import *
from validate_inputs import *
import pdb;

def list_ports():
    """Lists all available COM ports on the system."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No available ports found.")
    return ports

def select_port(ports):
    """Allows the user to select a COM port by index or number."""
    print("\nAvailable ports:")
    for i, port in enumerate(ports):
        print(f"{i + 1}: {port.device} - {port.description}")
    
    while True:
        selection = input("\nSelect the port number you want to connect to (index or port number, e.g., COM11), or 'q' to quit: ")
        #selection = validate_list_options(ports, "\nSelect the port number you want to connect to (index or port number, e.g., COM11), or 'q' to quit: ")
        print("") # end line
        if selection.lower() == 'q':
            print("Exiting the program.")
            exit()  # Termina el programa si se ingresa 'q'
        
        try:
            index = int(selection) - 1
            if 0 <= index < len(ports):
                return ports[index].device
        except ValueError:
            for port in ports:
                if port.device == selection.upper():
                    return port.device
        
        print("Please enter a valid index number or the exact port name (e.g., COM11).")

def main():
    while True:
        print("EML sensor tester - Select Option:")
        print("1. Start Test Config")
        print("2. Delete Log Files")
        print("3. Exit")

        menu_option = validate_three_options("Input selected option ('1', '2' or '3'): ")
        print("") # end line
        
        if menu_option == "1":
            multiple_chain()
            break
        elif menu_option == "2":  # Opción para eliminar archivos de registro
            delete_log_files()
        elif menu_option == "3":
            print("Exiting.")
            break

if __name__ == "__main__":
    main()