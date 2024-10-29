import asyncio
import sys
from datetime import datetime
from pymodbus import ModbusException
from conversion import *
from modbus_functions import * 
import time
import math
import asyncio
from datetime import datetime
from pymodbus.exceptions import ModbusException

async def listen_for_quit():
    """
    Listens for 'q' input from the user to quit the continuous mode.
    Runs as a separate asynchronous task.
    """
    loop = asyncio.get_running_loop()
    future = loop.run_in_executor(None, sys.stdin.readline)
    result = await future
    return result.strip() == 'q'

async def auto_test(client, responsive_slaves, filename):
    """Performs an automatic test based on user-selected mode."""
    log_data = []

    print("Select testing mode:")
    print("1. By cycles")
    print("2. By time")
    print("3. Continuous")
    mode = int(input("Enter the mode (1, 2, or 3): "))

    if mode == 1:
        num_cycles = int(input("Enter the number of cycles for the auto-test: "))
        print(f"Performing auto test for {num_cycles} cycles")
        
        for i in range(num_cycles):
            print(f"Cycle: {i}")
            await auto_test_cycle(client, responsive_slaves, log_data)

    elif mode == 2:
        total_time = float(input("Enter the total duration in seconds for the auto-test: "))
        end_time = time.time() + total_time
        interval = float(input("Enter the interval time in seconds between measurements: "))
        
        print(f"Performing auto test for {total_time} seconds with an interval of {interval} seconds.")
        
        while time.time() < end_time:
            await auto_test_cycle(client, responsive_slaves, log_data)
            await asyncio.sleep(interval)  # Wait for the specified interval

    elif mode == 3:
        print("Continuous mode. Press 'q' and Enter to stop.")

        try:
            quit_task = asyncio.create_task(listen_for_quit())
            
            while True:
                test_task = asyncio.create_task(auto_test_cycle(client, responsive_slaves, log_data))
                await asyncio.sleep(1)  # Short period between measurements
                done, _ = await asyncio.wait([quit_task, test_task], return_when=asyncio.FIRST_COMPLETED)

                if quit_task in done:
                    # 'q' was pressed
                    print("Exiting continuous mode.")
                    quit_task.cancel()
                    break
        except KeyboardInterrupt:
            print("Auto-test interrupted.")

    else:
        print("Invalid option selected. Please select again.")
        return

    print("Auto-test completed. Running temperature conversion...")
    client.close()

    # Run convertTempString on the log file after all cycles are complete
    convertTempString(filename)
    print(f"Temperature conversion completed on file: {filename}")


async def auto_test_cycle(client, responsive_slaves, log_data):
    """A single cycle of the auto-test, logging temperatures for responsive slaves."""
    log_data.clear()  # Clear log_data at the beginning of each cycle

    for slave_id in responsive_slaves:
        try:
            write_response = await client.write_coil(0, True, slave=slave_id)
            if not write_response.isError():
                read_response = await client.read_input_registers(2, count=1, slave=slave_id)
                if not read_response.isError():
                    temperature = read_response.registers[0]
                    log_data.append((slave_id, temperature))
        except ModbusException:
            continue

    # Obtain current date/time
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    # Log data to file
    log_to_file(log_data, current_timestamp)


def log_to_file(log_data, timestamp=None):
    """Logs data to a file."""
    with open("modbus_test_log.txt", "a") as log_file:  # Use "a" to append to the file
        for entry in log_data:
            if timestamp:
                log_file.write(f"{timestamp}_Slave_{entry[0]} Temperature = {entry[1]}\n")
            else:
                log_file.write(f"Slave_{entry[0]} Temperature = {entry[1]}\n")