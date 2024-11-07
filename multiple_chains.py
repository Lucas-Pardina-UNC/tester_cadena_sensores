import asyncio
from pymodbus.client import AsyncModbusSerialClient
from pymodbus import FramerType
from pymodbus import pymodbus_apply_logging_config
from conversion import *
from modbus_functions import * 
import time
import asyncio
from validate_time import *
from auto_test import auto_test_cycle, listen_for_quit
from get_set_available_slaves import *
from sensor_chain_tester import list_ports
from manual_modbus import *
from validate_inputs import *

def select_port_multiple(ports):
    """Allows the user to select a COM port by index or number, then removes it from the list to avoid reuse."""
    print("\nAvailable ports:")
    for i, port in enumerate(ports):
        print(f"{i + 1}: {port.device} - {port.description}")
    
    while True:
        selection = input("\nSelect the port number you want to connect to (index or port number, e.g., COM11), or 'q' to quit: ")
        
        if selection.lower() == 'q':
            print("Exiting the program.")
            exit()  # Ends the program if 'q' is entered
        
        try:
            index = int(selection) - 1
            if 0 <= index < len(ports):
                selected_port = ports.pop(index)  # Remove the selected port from the list
                return selected_port.device
        except ValueError:
            for port in ports:
                if port.device == selection.upper():
                    ports.remove(port)  # Remove the selected port by name
                    return port.device
        
        print("Please enter a valid index number or the exact port name (e.g., COM11).")

def multiple_chain():
    num_chains = int(input("Enter the number of chains you intend to test (1 - amount of connected chains (COM) in your PC): "))
    print("") # end line
    ports = list_ports()
    chains_ports = []
    log_file_names_raw = []
    slave_info_file_names = []

    for i in range(num_chains):
        print(f"Select the COM port for chain {i + 1}")
        selected_port = select_port_multiple(ports)  # Remove port from list after selection
        chains_ports.append(selected_port)
        log_file_names_raw.append(f"auto_test_log_{i}.txt")
        slave_info_file_names.append(f"available_slaves_chain_{i}.txt")

    # Output the selected chains and log files for verification
    print("") # end line
    print("Selected Chains:", chains_ports)
    print("Log Files (Raw):", log_file_names_raw)
    print("Slave Info Files:", slave_info_file_names)
    print("") # end line

    asyncio.run(run_client_multiple(num_chains, chains_ports, slave_info_file_names, log_file_names_raw))

async def run_client_multiple(num_chains, chains_ports, slave_info_file_names, log_file_names_raw):
    """Configures and runs the Modbus RTU client."""
    pymodbus_apply_logging_config("WARNING")

    chain_clients = []
    chain_avaiable_slaves = []

    for i in range(num_chains):
        # Create one client for each sensor chain
        client = AsyncModbusSerialClient(
            port=chains_ports[i],
            framer=FramerType.RTU,
            baudrate=9600,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=1
        )
        chain_clients.append(client)
        
        # Connect to each client
        print("") # end line
        print("Connecting to the server...")
        await client.connect()
        if client.connected:
            print(f"Successfully connected on port {chains_ports[i]}.")
        else:
            print(f"Connection attempt failed for sensor chain {i}, port {chains_ports[i]}.")
    
        # Check available slaves for each sensor chain
        responsive_slaves = []
        valid_file = False

        print(f"Checking for Available Slaves config for sensor chain {i}...")
        print("") # end line

        # Check for available_slaves.txt and its validity
        valid_file = file_is_valid(slave_info_file_names[i])

        # Provide options based on file validity
        if valid_file:
            print("Available options:")
            print("1. Use the information from available_slaves.txt")
            print("2. Detect the available slaves (this will modify the file)")
            print("3. Input the available slaves manually (this will also modify the file)")
            option = validate_three_options("Select an option (1, 2, or 3): ")

            if option == '1':
                responsive_slaves = get_responsive_slaves(slave_info_file_names[i]) 
                #pass  # Use the loaded responsive_slaves as is
            elif option == '2':
                responsive_slaves = await list_sensors(client, slave_info_file_names[i])
                #responsive_slaves = await list_sensors(client, chains_ports[i], slave_info_file_names[i])
            elif option == '3':
                await input_manual_slaves(responsive_slaves, slave_info_file_names[i])
            else:
                print("Invalid option selected. Exiting.")
                return

        else:
            print("Since no valid data was found, only these options are available:")
            print("1. Detect the available slaves (this will modify the file)")
            print("2. Input the available slaves manually (this will also modify the file)")
            option = validate_two_options("Select an option (1 or 2): ")

            if option == '1':
                responsive_slaves = await list_sensors(client, slave_info_file_names[i])
            elif option == '2':
                await input_manual_slaves(responsive_slaves)
            else:
                print("Invalid option selected. Exiting.")
                return

        chain_avaiable_slaves.append(responsive_slaves)

    while True:
        print("") # end line
        print("Select testing option:")
        print("1. Auto - Test")
        print("2. Manual Modbus (Single Chain)")
        print("3. Exit")
        test_option = validate_three_options("Select an option (1, 2, or 3): ")
        print("") # end line

        if test_option == '1':
            # Perform testiong options
            await auto_test_multiple(num_chains, chain_clients, chain_avaiable_slaves, log_file_names_raw)
        elif test_option == '2':
            print("Avaiable Chains:")
            for index, chain in enumerate(chain_clients):
                print(f"{index + 1}: Chain {index + 1} (port: {chains_ports[index]})")
            chain_number = (int)(validate_list_options(chain_clients, "Select which chain to communicate to ('1', '2', ...): ")) -1
            await manual_modbus(chain_clients[chain_number])
        elif test_option == '3':
            break

    # Close connections if they are open
    for i in range(num_chains):
        if chain_clients[i].connected:
            try:
                chain_clients[i].close()
            except Exception as e:
                print(f"Error closing client: {e}")

async def auto_test_multiple(num_chains, chain_clients, chain_responsive_slaves, log_file_names_raw):
    """Performs an automatic test based on user-selected mode."""
    log_data = []

    test_continue = "s"
    while test_continue != "n":
        print("Select testing mode:")
        print("1. By cycles")
        print("2. By time")
        print("3. Continuous")
        print("4. Back to previous menu")
        mode = validate_four_options("Enter the mode (1, 2, or 3) or 4 for to go back to the previous menu: ")
        print("")
        #mode = int(input("Enter the mode (1, 2, or 3): "))

        if mode == "1":
            num_cycles = int(input("Enter the number of cycles for the auto-test: "))
            print(f"Performing auto test for {num_cycles} cycles")
            
            for i in range(num_cycles):
                print(f"Cycle: {i}")
                for j in range(num_chains):
                    await auto_test_cycle(chain_clients[j], chain_responsive_slaves[j], log_data, log_file_names_raw[j], j)

        elif mode == "2":
            # Ask for total duration in "dd:hh:mm:ss" format
            total_time_str = validate_time_input("Enter the total duration for the auto-test (format dd:hh:mm:ss): ")
            
            # Convert total testing time to seconds
            total_time = parse_time_input(total_time_str)
            
            # Ask for interval time in "hh:mm:ss" format
            interval_time_str = validate_time_input("Enter the interval time between measurements (format dd:hh:mm:ss): ")

            # Convert interval time to seconds
            interval = parse_time_input(interval_time_str)

            while interval >= total_time:
                print("Interval time cannot be greater than or equal to the total duration.")
                interval_time_str = validate_time_input("Enter the interval time (DD:HH:MM:SS): ")
                interval = parse_time_input(interval_time_str)

            # Split the total time and interval into days, hours, minutes, and seconds
            total_days, total_hours, total_minutes, total_seconds = total_time_str.split(":")
            #interval_days = "0"  # Interval has no days
            interval_days, interval_hours, interval_minutes, interval_seconds = interval_time_str.split(":")

            print(f"Performing auto-test for {total_days} days, {total_hours} hours, {total_minutes} minutes, "
                f"{total_seconds} seconds with an interval of {interval_days} days, {interval_hours} hours, {interval_minutes} minutes, "
                f"{interval_seconds} seconds.")
            #print(f"Performing auto-test for {total_time_str} with an interval of {interval_time_str}.")

            # Obtain end time
            end_time = time.time() + total_time
            # Loop to perform auto-test until end time is reached
            
            while time.time() < end_time:
                for j in range(num_chains):
                    await auto_test_cycle(chain_clients[j], chain_responsive_slaves[j], log_data, log_file_names_raw[j], j)
                await asyncio.sleep(interval)  # Wait for the specified interval

        elif mode == "3":
            print("Continuous mode. Press 'q' and Enter to stop.")

            async def multiple_auto_test_cycles():
                for j in range (num_chains):
                    await auto_test_cycle(chain_clients[j], chain_responsive_slaves[j], log_data, log_file_names_raw[j], j)

            try:
                quit_task = asyncio.create_task(listen_for_quit())
                
                while True:
                    # Create the test task for each chain and append to the list
                    test_task = asyncio.create_task(multiple_auto_test_cycles())
                    #test_tasks.append(asyncio.create_task(auto_test_cycle(chain_clients[j], chain_responsive_slaves[j], log_data, log_file_names_raw[j])))
                    await asyncio.sleep(1)  # Short period between measurements
                    done, _ = await asyncio.wait([quit_task, test_task], return_when=asyncio.FIRST_COMPLETED)

                    if quit_task in done:
                        # 'q' was pressed
                        print("Exiting continuous mode.")
                        quit_task.cancel()
                        break
            except KeyboardInterrupt:
                print("Auto-test interrupted.")

        elif mode == "4":
            print("Exiting")
            break


        print("Auto test completed")
    
        while True:
                test_continue = input("Would you like to continue testing? (s/n): ").strip().lower()  # Get user input and normalize it
                if test_continue in ('s', 'n'):  # Check if the input is either 's' or 'n'
                    break
                else:
                    print("Invalid input. Please enter 's' for yes or 'n' for no.")  # Prompt for valid input