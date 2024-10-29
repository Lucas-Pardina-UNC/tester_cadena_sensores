from modbus_functions import read_input_register
import os

async def list_sensors(client):
    """Reads input register 0 of each slave up to a specified number and writes detected sensors to a file."""
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
    
    # Write responsive slaves to a file
    with open("available_slaves.txt", "w") as f:
        for slave in responsive_slaves:
            f.write(f"{slave}\n")
    print("Responsive slave IDs have been written to available_slaves.txt.")
    
    return responsive_slaves

async def input_manual_slaves(responsive_slaves):
    """Prompts the user to input slave IDs manually."""
    print("Choose how to enter the IDs of each active slave:")
    print("1. Enter each ID one by one.")
    print("2. Enter a range of IDs (e.g., '2-14' to select IDs from 2 to 14).")
    input_method = input("Enter '1' for individual IDs or '2' for a range: ")

    if input_method == '1':
        print("Enter the IDs of each active slave (1-255). Press Enter after each ID.")
        while True:
            try:
                slave_id = int(input("Slave ID (or press Enter to finish): "))
                if 1 <= slave_id <= 255:
                    responsive_slaves.append(slave_id)
                else:
                    print("Please enter a valid slave ID between 1 and 255.")
            except ValueError:
                break  # Exit loop on empty input

    elif input_method == '2':
        print("Enter the range of IDs for active slaves in the format 'start-end' (e.g., '2-14').")
        while True:
            try:
                range_input = input("Enter slave ID range (or press Enter to finish): ")
                if not range_input:  # Break on empty input
                    break
                start_id, end_id = map(int, range_input.split('-'))
                
                if 1 <= start_id <= 255 and 1 <= end_id <= 255 and start_id <= end_id:
                    responsive_slaves.extend(range(start_id, end_id + 1))
                else:
                    print("Please enter a valid range between 1 and 255, with start ID less than or equal to end ID.")
            except ValueError:
                print("Invalid input. Please enter the range in the format 'start-end'.")

    # Save responsive_slaves to the available_slaves.txt file
    with open("available_slaves.txt", "w") as f:
        for slave in responsive_slaves:
            f.write(f"{slave}\n")
    print("Responsive slave IDs have been written to available_slaves.txt.")

def file_is_valid(filename="available_slaves.txt"):
    """Check if the file exists and contains valid slave IDs."""
    if os.path.exists(filename):
        with open(filename, "r") as f:
            lines = f.readlines()
            # Check if the file is empty or contains only whitespace
            if not lines or all(not line.strip() for line in lines):
                print(f"{filename} is empty or contains no valid numbers.")
                return False
            else:
                try:
                    # Check if all lines can be converted to integers
                    [int(line.strip()) for line in lines]
                    return True
                except ValueError:
                    print(f"Invalid data found in {filename}. Please detect slaves or enter them manually.")
                    return False
    else:
        print(f"{filename} not found. Please detect slaves or enter them manually.")
        return False
    
def get_responsive_slaves(filename="available_slaves.txt"):
    """Retrieve a list of responsive slave IDs from the file."""
    responsive_slaves = []
    
    if file_is_valid(filename):
        with open(filename, "r") as f:
            lines = f.readlines()
            try:
                responsive_slaves = [int(line.strip()) for line in lines if line.strip()]
                # Filter to ensure all IDs are within the range 1-255
                responsive_slaves = [slave_id for slave_id in responsive_slaves if 1 <= slave_id <= 255]
                
                if responsive_slaves:
                    print(f"Loaded responsive slaves from {filename}: {responsive_slaves}")
                else:
                    print(f"No valid slave IDs found in {filename}.")
            except ValueError:
                print(f"Error converting data in {filename}.")
    
    return responsive_slaves