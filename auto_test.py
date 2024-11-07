import asyncio
import sys
from datetime import datetime
from pymodbus import ModbusException
from conversion import *
from modbus_functions import * 
import time
import re
import asyncio
from datetime import datetime
from pymodbus.exceptions import ModbusException
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

async def auto_test_cycle(client, responsive_slaves, log_data, filename = "modbus_test_log.txt", chain_id = 0):
    """A single cycle of the auto-test, logging temperatures for responsive slaves."""
    log_data.clear()  # Clear log_data at the beginning of each cycle

    for slave_id in responsive_slaves:
        try:
            write_response = await client.write_coil(0, True, slave=slave_id)
            if not write_response.isError():
                read_response = await client.read_input_registers(2, count=1, slave=slave_id)
                if not read_response.isError():
                    ADC_value = read_response.registers[0]
                    temperature = adc_to_temperature(ADC_value)
                    log_data.append((slave_id, ADC_value, temperature))
                else:
                    print(f"Error when reading input register 2 for slave {slave_id}")  
            else:
                print(f"Error when writting coil 0 for slave {slave_id}")    
        except ModbusException:
            continue

    # Obtain current date/time
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    # Log data to file
    log_to_file(log_data, current_timestamp, filename)
    
    # Log to excel
    log_to_excel(log_data, current_timestamp, chain_id)


def log_to_file(log_data, timestamp=None, filename = "modbus_test_log.txt"):
    """Logs data to a file."""
    with open(filename, "a") as log_file:  # Use "a" to append to the file
        for entry in log_data:
            if timestamp:
                log_file.write(f"{timestamp} | Slave {entry[0]} | ADC_Value = {entry[1]} | Temperature = {entry[2]}\n")
            else:
                log_file.write(f"Slave {entry[0]} | ADC_Value = {entry[1]} | Temperature = {entry[2]}\n")


def delete_log_files():
    """Elimina archivos de registro especificados."""
    log_files = ["temp_string.tmp", "temp_string.txt", "modbus_test_log.txt", "auto_test_log_0.txt", "auto_test_log_1.txt", "modbus_test_log.xlsx", "convertion_log.txt"]
    
    for file in log_files:
        try:
            os.remove(file)
            print(f"Deleted file: {file}")
        except FileNotFoundError:
            print(f"File not found: {file}")
        except Exception as e:
            print(f"Error deleting file {file}: {e}")