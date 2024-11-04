import asyncio
import sys
from datetime import datetime
from pymodbus import ModbusException
from conversion import *
from modbus_functions import * 
import time
import re
#import math
import asyncio
from datetime import datetime
from pymodbus.exceptions import ModbusException
import openpyxl  #pip install openpyxl
from openpyxl import Workbook
import os
from conversion import adc_to_temperature
from calc_sheets import *

async def listen_for_quit():
    """
    Listens for 'q' input from the user to quit the continuous mode.
    Runs as a separate asynchronous task.
    """
    loop = asyncio.get_running_loop()
    future = loop.run_in_executor(None, sys.stdin.readline)
    result = await future
    return result.strip() == 'q'

def parse_time_input(time_str):
    days, hours, minutes, seconds = map(int, time_str.split(":"))
    return days * 86400 + hours * 3600 + minutes * 60 + seconds

def validate_time_input(prompt):
    while True:
        time_input = input(prompt)
        # Regular expression for matching format "DD:HH:MM:SS"
        if re.match(r"^\d+:\d{2}:\d{2}:\d{2}$", time_input):
            return time_input
        else:
            print("Invalid format. Please enter time in 'DD:HH:MM:SS' format.")

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

    print("Auto-test completed.")
    #client.close()


async def auto_test_cycle(client, responsive_slaves, log_data):
    """A single cycle of the auto-test, logging temperatures for responsive slaves."""
    log_data.clear()  # Clear log_data at the beginning of each cycle

    for slave_id in responsive_slaves:
        try:
            write_response = await client.write_coil(0, True, slave=slave_id)
            if not write_response.isError():
                read_response = await client.read_input_registers(2, count=1, slave=slave_id)
                if not read_response.isError():
                    ADC_value = read_response.registers[0]
                    #temperature = read_response.registers[0]
                    temperature = adc_to_temperature(ADC_value)
                    log_data.append((slave_id, ADC_value, temperature))
        except ModbusException:
            continue

    # Obtain current date/time
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    # Log data to file
    log_to_file(log_data, current_timestamp)
    
    # Log to excel
    log_to_excel(log_data, current_timestamp)
    #row = row + 1


def log_to_file(log_data, timestamp=None):
    """Logs data to a file."""
    with open("modbus_test_log.txt", "a") as log_file:  # Use "a" to append to the file
        for entry in log_data:
            if timestamp:
                log_file.write(f"{timestamp} | Slave {entry[0]} | ADC_Value = {entry[1]} | Temperature = {entry[2]}\n")
            else:
                log_file.write(f"Slave {entry[0]} | ADC_Value = {entry[1]} | Temperature = {entry[2]}\n")


def delete_log_files():
    """Elimina archivos de registro especificados."""
    log_files = ["temp_string.tmp", "temp_string.txt", "modbus_test_log.txt", "modbus_test_log.xlsx", "convertion_log.txt"]
    
    for file in log_files:
        try:
            os.remove(file)
            print(f"Deleted file: {file}")
        except FileNotFoundError:
            print(f"File not found: {file}")
        except Exception as e:
            print(f"Error deleting file {file}: {e}")