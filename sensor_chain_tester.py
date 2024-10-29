import asyncio
import serial.tools.list_ports
from pymodbus.client import AsyncModbusSerialClient
from pymodbus import ModbusException, ExceptionResponse, FramerType
from pymodbus import pymodbus_apply_logging_config
import math
from datetime import datetime
from PS103J2_table import *
from conversion import *
from auto_test import * 
from manual_modbus import *
from modbus_functions import (
    write_holding_register,
    read_holding_register,
    write_coil,
    read_input_register,
)

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


async def list_sensors(client):
    """Reads input register 0 of each slave up to a specified number and displays all detected sensors."""
    while True:
        try:
            num_slaves_to_test = int(input("Enter the number of slaves you want to test (1-255): "))
            if 1 <= num_slaves_to_test <= 255:
                break
            else:
                print("Please enter a number between 1 and 255.")
        except ValueError:
            print("Invalid input. Please enter an integer between 1 and 255.")

    responsive_slaves = []

    for slave_id in range(1, num_slaves_to_test + 1):
        # Check if client is connected; if not, attempt to reconnect
        if not client.connected:
            print(f"Client disconnected. Attempting to reconnect before querying slave {slave_id}...")
            await client.connect()
            if client.connected:
                print("Reconnection successful.")
            else:
                print("Failed to reconnect. Exiting sensor detection.")
                break

        # Attempt to read the input register
        read_value = await read_input_register(client, slave_id, input_register_address=0)
        
        if read_value is not None:
            responsive_slaves.append(slave_id)  # Track the responsive slave ID
            sensor_type = ""
            if read_value in [900, 999]:
                sensor_type = "Temperature sensor"
            elif read_value == 200:
                sensor_type = "Air sensor"
            elif read_value == 100:
                sensor_type = "Energy sensor"
            elif read_value == 1000:
                sensor_type = "Probe"
            else:
                sensor_type = "Unknown sensor ID"

            print(f"Slave {slave_id}: Sensor ID = {read_value}, Sensor type = {sensor_type}")
        else:
            print(f"Slave {slave_id} did not respond.")

    print("\nDetected sensors:")
    print(f"Responsive slaves: {responsive_slaves}")
    return responsive_slaves


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

        # Ask user whether to detect slaves or input manually
        detect_slaves = input("Do you want to detect the number of slaves? (y/n): ").strip().lower()

        if detect_slaves == 'y':
            responsive_slaves = await list_sensors(client)
        elif detect_slaves == 'n':
            num_slaves = int(input("Enter the number of slaves: "))
            responsive_slaves = []

            print("Choose how to enter the IDs of each active slave:")
            print("1. Enter each ID one by one.")
            print("2. Enter a range of IDs (e.g., '2-14' to select IDs from 2 to 14).")
            input_method = input("Enter '1' for individual IDs or '2' for a range: ")

            if input_method == '1':
                # Option 1: Enter each slave ID one by one
                print("Enter the IDs of each active slave (1-255). Press Enter after each ID.")
                for _ in range(num_slaves):
                    while True:
                        try:
                            slave_id = int(input("Slave ID: "))
                            if 1 <= slave_id <= 255:
                                responsive_slaves.append(slave_id)
                                break
                            else:
                                print("Please enter a valid slave ID between 1 and 255.")
                        except ValueError:
                            print("Invalid input. Please enter an integer.")

            elif input_method == '2':
                # Option 2: Enter a range of slave IDs
                print("Enter the range of IDs for active slaves in the format 'start-end' (e.g., '2-14').")
                while True:
                    try:
                        range_input = input("Enter slave ID range: ")
                        start_id, end_id = map(int, range_input.split('-'))
                        
                        # Validate range input
                        if 1 <= start_id <= 255 and 1 <= end_id <= 255 and start_id <= end_id:
                            responsive_slaves.extend(range(start_id, end_id + 1))
                            break
                        else:
                            print("Please enter a valid range between 1 and 255, with start ID less than or equal to end ID.")
                    except ValueError:
                        print("Invalid input. Please enter the range in the format 'start-end'.")

            else:
                print("Invalid option selected. Exiting.")
                return


    else:
        print(f"Could not connect to port {com_port}.")
        return

    if not client.connected:
        await client.connect()
        if client.connected:
            print("Reconnection success after slave detection\n")
        else:
            print("Reconnection failed after slave detection\n")

    if client.connected:
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
    else:
        print("Reconnection failed. Exiting.")

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

def delete_log_files():
    """Elimina archivos de registro especificados."""
    log_files = ["temp_string.tmp", "temp_string.txt", "modbus_test_log.txt", "convertion_log.txt"]
    
    for file in log_files:
        try:
            os.remove(file)
            print(f"Deleted file: {file}")
        except FileNotFoundError:
            print(f"File not found: {file}")
        except Exception as e:
            print(f"Error deleting file {file}: {e}")
