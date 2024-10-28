import asyncio
import serial.tools.list_ports
from pymodbus.client import AsyncModbusSerialClient
from pymodbus import ModbusException, ExceptionResponse, FramerType
from pymodbus import pymodbus_apply_logging_config
import math
from PS103J2_table import *
from conversion import *
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
        selection = input("\nSelect the port number you want to connect to (index or port number, e.g., COM11): ")
        
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
    """Reads input register 0 of each slave until one does not respond and displays all detected sensors."""
    num_slaves = 0
    slave_id = 1

    while True:
        read_value = await read_input_register(client, slave_id, input_register_address=0)
        
        if read_value is not None:
            num_slaves += 1
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
            slave_id += 1           
        else:
            print(f"Slave {slave_id} did not respond. Stopping the search.")
            try:
                client.close()
            except Exception as e:
                print(f"Error closing client: {e}")
            break

    print("\nDetected sensors:")
    print(f"\nNumber of slaves that responded: {num_slaves}")
    return num_slaves

async def auto_test(client, num_slaves, filename):
    """Performs an automatic test, writing to coil 0 and reading input register 2 of each slave periodically."""
    log_data = []
    # Pedir al usuario que ingrese el tiempo de intervalo y la duración total
    interval = float(input("Enter the interval time in seconds for the auto-test: "))
    total_time = float(input("Enter the total duration in seconds for the auto-test: "))

    # Calcular el número de ciclos de prueba usando math.ceil para redondear hacia arriba
    num_cycles = math.ceil(total_time / interval)
    print(f"Performing auto test for {num_cycles} cycles with an interval of {interval} seconds.")

    async def auto_test_cycle():
        """A single cycle of the auto-test, logging temperatures."""
        nonlocal log_data
        for slave_id in range(1, num_slaves + 1):
            try:
                write_response = await client.write_coil(0, True, slave=slave_id)
                if not write_response.isError():
                    read_response = await client.read_input_registers(2, count=1, slave=slave_id)
                    if not read_response.isError():
                        temperature = read_response.registers[0]
                        log_data.append((slave_id, temperature))
            except ModbusException:
                continue

        # Log data to file
        with open("modbus_test_log.txt", "w") as log_file:
            for entry in log_data:
                log_file.write(f"Slave {entry[0]}: Temperature = {entry[1]}\n")

    # Ejecutar el ciclo de auto-test `num_cycles` veces
    for _ in range(num_cycles):
        await auto_test_cycle()
        await asyncio.sleep(interval)  # Esperar el intervalo antes del siguiente ciclo

    print("Auto-test completed. Running temperature conversion...")
    client.close()

    # Run convertTempString on the log file
    convertTempString(filename)
    print(f"Temperature conversion completed on file: {filename}")


async def manual_modbus(client):
    """Allows manual use of Modbus commands."""
    register_value = 0

    while True:
        print("\nModbus Manual Mode")
        print("1. Write Holding Register")
        print("2. Read Holding Register")
        print("3. Write Coil")
        print("4. Read Input Register")
        print("5. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            slave_id = int(input("Enter slave ID: "))
            register_address = int(input("Enter register address: "))
            value = int(input("Enter value to write: "))
            await write_holding_register(client, slave_id, register_address, value)
        elif choice == "2":
            slave_id = int(input("Enter slave ID: "))
            register_address = int(input("Enter register address: "))
            await read_holding_register(client, slave_id, register_address)
        elif choice == "3":
            slave_id = int(input("Enter slave ID: "))
            coil_address = int(input("Enter coil address: "))
            value = bool(int(input("Enter value (0 or 1): ")))
            await write_coil(client, slave_id, coil_address, value)
        elif choice == "4":
            slave_id = int(input("Enter slave ID: "))
            register_address = int(input("Enter register address: "))
            register_value = await read_input_register(client, slave_id, register_address)
            if(register_value != None):
                print(f"Obtained Input Register value: {register_value}")
            else: 
                print(f"Could not read input register {register_address} for slave {slave_id}")
        elif choice == "5":
            break
        else:
            print("Invalid option. Please select again.")

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
            num_slaves = await list_sensors(client)
        elif detect_slaves == 'n':
            num_slaves = int(input("Enter the number of slaves: "))
        else:
            print("Invalid option. Exiting.")
            return
    else:
        print(f"Could not connect to port {com_port}.")
        return

    if client.connected:
        print("\nSelect mode:")
        print("1. Auto-test")
        print("2. Modbus Manual")
        print("3. Exit")
        mode = input("Enter mode (1, 2, or 3): ")

        if mode == "1":
            await auto_test(client, num_slaves, filename)
        elif mode == "2":
            await manual_modbus(client)
        elif mode == "3":
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
