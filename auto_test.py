import asyncio
import sys
from datetime import datetime
from pymodbus import ModbusException
from conversion import *
from modbus_functions import *
from datetime import datetime
from pymodbus.exceptions import ModbusException
import os
from conversion import adc_to_temperature
from calc_sheets import *
from typing import List, Tuple, Optional

async def listen_for_quit() -> bool:
    """
    Listens for 'q' input from the user to quit the continuous mode.
    Runs as a separate asynchronous task.
    
    Returns:
        bool: Returns True if the user enters 'q', indicating the program should quit.
    """
    loop = asyncio.get_running_loop()
    future = loop.run_in_executor(None, sys.stdin.readline)
    result = await future
    return result.strip() == 'q'

async def auto_test_cycle(client, responsive_slaves: List[int], log_data: List[Tuple[int, int, float]], filename: str = "modbus_test_log.txt", chain_id: int = 0) -> None:
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
                    print(f"Error al leer el registro de entrada 2 para el esclavo {slave_id}")  
            else:
                print(f"Error al escribir en la bobina 0 para el esclavo {slave_id}")    
        except ModbusException:
            continue

    # Obtain current date/time
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    # Log data to file
    log_to_file(log_data, current_timestamp, filename)
    
    # Log to excel
    log_to_excel(log_data, current_timestamp, chain_id)


def log_to_file(log_data: List[Tuple[int, int, float]], timestamp: Optional[str] = None, filename: str = "modbus_test_log.txt") -> None:
    """Logs data to a file."""
    with open(filename, "a") as log_file:  # Use "a" to append to the file
        for entry in log_data:
            if timestamp:
                log_file.write(f"{timestamp} | Esclavo {entry[0]} | ADC_Value = {entry[1]} | Temperatura = {entry[2]}\n")
            else:
                log_file.write(f"Esclavo {entry[0]} | ADC_Value = {entry[1]} | Temperatura = {entry[2]}\n")


def delete_log_files() -> None:
    """Elimina archivos de registro especificados."""
    log_files = ["temp_string.tmp", "temp_string.txt", "modbus_test_log.txt", "auto_test_log_0.txt", "auto_test_log_1.txt", "modbus_test_log.xlsx", "convertion_log.txt"]
    
    for file in log_files:
        try:
            os.remove(file)
            print(f"Archivo eliminado: {file}")
        except FileNotFoundError:
            print(f"Archivo no encontrado: {file}")
        except Exception as e:
            print(f"Error al eliminar el archivo {file}: {e}")