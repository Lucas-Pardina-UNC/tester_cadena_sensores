import re
import json 
import os
from typing import List

def validate_two_options(message: str = "") -> str:
    while True:
        menu_option = input(f"{message}")
        if menu_option in ('1', '2'):
            return menu_option
        else:
            print("Entrada inválida. Por favor, ingrese '1' o '2'.")

def validate_three_options(message: str = "") -> str:
    while True:
        menu_option = input(f"{message}")
        if menu_option in ('1', '2', '3'):
            return menu_option
        else:
            print("Entrada inválida. Por favor, ingrese '1', '2' o '3'.")

def validate_four_options(message: str = "") -> str:
    while True:
        menu_option = input(f"{message}")
        if menu_option in ('1', '2', '3', '4'):
            return menu_option
        else:
            print("Entrada inválida. Por favor, ingrese '1', '2', '3' o '4'.")

def validate_list_options(items: List[str], message: str = "") -> str:
    while True:
        user_input = input(f"{message}")
        if user_input.isdigit():
            option = int(user_input)
            if 1 <= option <= len(items):
                return user_input
            else:
                print(f"Entrada inválida. Por favor, ingrese un número entre 1 y {len(items)}.")
        else:
            print("Entrada inválida. Por favor, ingrese un número.")

def validate_positive_number(message: str = "") -> int:
    while True:
        user_input = input(f"{message}")
        if user_input.isdigit():  # Check if the input is a digit
            number = int(user_input)
            if number > 0:  # Check if it's positive
                return number
            else:
                print("Entrada inválida. Por favor, ingrese un número positivo.")
        else:
            print("Entrada inválida. Por favor, ingrese un número válido.")

def parse_time_input(time_str: str) -> int:
    days, hours, minutes, seconds = map(int, time_str.split(":"))
    return days * 86400 + hours * 3600 + minutes * 60 + seconds

def validate_time_input(prompt: str) -> str:
    while True:
        time_input = input(prompt)
        # Regular expression for matching format "DD:HH:MM:SS"
        if re.match(r"^\d+:\d{2}:\d{2}:\d{2}$", time_input):
            return time_input
        else:
            print("Formato inválido. Por favor ingrese el tiempo en el formato 'DD:HH:MM:SS'.")

def validate_config_file(filename: str) -> bool:
    """
    Valida si el archivo de configuración JSON es válido.

    Args:
        filename (str): Nombre del archivo JSON.

    Returns:
        bool: True si el archivo es válido, False en caso contrario.
    """
    if not os.path.exists(filename):
        print(f"Error: El archivo {filename} no existe.")
        return False

    try:
        with open(filename, 'r') as file:
            config_data = json.load(file)
    except json.JSONDecodeError:
        print(f"Error: El archivo {filename} no tiene un formato JSON válido.")
        return False

    required_fields = ["num_chains", "chains_ports", "chain_available_slaves", "log_file_names_raw"]
    for field in required_fields:
        if field not in config_data:
            print(f"Error: El archivo {filename} no contiene el campo requerido '{field}'.")
            return False

    num_chains = config_data.get("num_chains")
    if not isinstance(num_chains, int) or num_chains <= 0:
        print("Error: El campo 'num_chains' debe ser un número entero mayor a cero.")
        return False

    chains_ports = config_data.get("chains_ports")
    if not isinstance(chains_ports, list) or not all(isinstance(port, str) for port in chains_ports):
        print("Error: El campo 'chains_ports' debe ser una lista de strings.")
        return False
    if len(chains_ports) != num_chains:
        print("Error: El número de 'chains_ports' debe coincidir con 'num_chains'.")
        return False

    chain_available_slaves = config_data.get("chain_available_slaves")
    if not isinstance(chain_available_slaves, list) or not all(isinstance(slave_list, list) for slave_list in chain_available_slaves):
        print("Error: El campo 'chain_available_slaves' debe ser una lista de listas.")
        return False
    for slave_list in chain_available_slaves:
        if not all(isinstance(slave, int) and 1 <= slave <= 255 for slave in slave_list):
            print("Error: Cada lista en 'chain_available_slaves' debe contener enteros entre 1 y 255.")
            return False
    if len(chain_available_slaves) != num_chains:
        print("Error: El número de listas en 'chain_available_slaves' debe coincidir con 'num_chains'.")
        return False

    log_file_names_raw = config_data.get("log_file_names_raw")
    if not isinstance(log_file_names_raw, list) or not all(isinstance(name, str) for name in log_file_names_raw):
        print("Error: El campo 'log_file_names_raw' debe ser una lista de strings.")
        return False
    if len(log_file_names_raw) != num_chains:
        print("Error: El número de 'log_file_names_raw' debe coincidir con 'num_chains'.")
        return False

    return True
