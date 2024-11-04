import asyncio
import serial.tools.list_ports
from pymodbus.client import AsyncModbusSerialClient
from pymodbus import FramerType
from pymodbus import pymodbus_apply_logging_config
from PS103J2_table import *
from conversion import *
from auto_test import * 
from manual_modbus import *
from get_set_available_slaves import *
from calc_sheets import *
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


async def run_client(com_port, filename):
    """Configures and runs the Modbus RTU client."""
    pymodbus_apply_logging_config("WARNING")

    client = AsyncModbusSerialClient(
        port=com_port,
        framer=FramerType.RTU,
        baudrate=9600,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=1
    )

    print("Connecting to the server...")
    await client.connect()

    if client.connected:
        print(f"Successfully connected on port {com_port}.")

                # Check for available_slaves.txt and its validity
        responsive_slaves = []
        valid_file = False

        valid_file = file_is_valid()
        responsive_slaves = get_responsive_slaves()

        # Provide options based on file validity
        if valid_file:
            print("Available options:")
            print("1. Use the information from available_slaves.txt")
            print("2. Detect the available slaves (this will modify the file)")
            print("3. Input the available slaves manually (this will also modify the file)")
            option = input("Select an option (1, 2, or 3): ")

            if option == '1':
                pass  # Use the loaded responsive_slaves as is
            elif option == '2':
                responsive_slaves = await list_sensors(client, com_port)
            elif option == '3':
                await input_manual_slaves(responsive_slaves)
            else:
                print("Invalid option selected. Exiting.")
                return

        else:
            print("Since no valid data was found, only these options are available:")
            print("1. Detect the available slaves (this will modify the file)")
            print("2. Input the available slaves manually (this will also modify the file)")
            option = input("Select an option (1 or 2): ")

            if option == '1':
                responsive_slaves = await list_sensors(client, com_port)
            elif option == '2':
                await input_manual_slaves(responsive_slaves)
            else:
                print("Invalid option selected. Exiting.")
                return

    else:
        print(f"Could not connect to port {com_port}.")
        return

    if client.connected:
        test_continue = "s"
        while test_continue != "n":
            print("\nSelect mode:")
            print("1. Auto-test")
            print("2. Modbus Manual")
            print("3. Delete Log Files")  # Nueva opción para eliminar archivos de registro
            print("4. Exit")
            mode = input("Enter mode (1, 2, 3, or 4): ")

            if mode == "1":
                await auto_test(client, responsive_slaves, filename)
            elif mode == "2":
                await manual_modbus(client)
            elif mode == "3":  # Opción para eliminar archivos de registro
                delete_log_files()
            elif mode == "4":
                print("Exiting.")
            else:
                print("Invalid option. Exiting.")

            while True:
                test_continue = input("Would you like to continue testing? (s/n): ").strip().lower()  # Get user input and normalize it
                if test_continue in ('s', 'n'):  # Check if the input is either 's' or 'n'
                    break
                else:
                    print("Invalid input. Please enter 's' for yes or 'n' for no.")  # Prompt for valid input
            
    else:
        print("Failed to load main menu, the client is not connected. Exiting.")



    if client.connected:
        print("Closing the connection...")
        try:
            client.close()
        except Exception as e:
            print(f"Error closing client: {e}")

def main():
    ports = list_ports()
    if not ports:
        print("No available ports to connect.")
        return
    
    selected_com = select_port(ports)
    filename = "modbus_test_log"  # Filename for temperature conversion after auto-test
    print(f"Attempting to connect to {selected_com}...")
    
    asyncio.run(run_client(selected_com, filename))

if __name__ == "__main__":
    main()