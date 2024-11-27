import os
from modbus_functions import read_input_register
from legacy_commands import *
from validate import *

async def list_sensors(client, chain_port, chain_protocol, filename="available_slaves.txt") -> list[int]:
    """Lee el registro de entrada 0 de cada esclavo hasta un número especificado y escribe los sensores detectados en un archivo."""
    while True:
        try:
            num_slaves_to_test = int(input("Ingresa el número de esclavos que deseas probar (1-255): "))
            if 1 <= num_slaves_to_test <= 255:
                break
            else:
                print("Por favor, ingresa un número entre 1 y 255.")
        except ValueError:
            print("Entrada no válida. Por favor, ingresa un número entero entre 1 y 255.")

    responsive_slaves = []

    for slave_id in range(1, num_slaves_to_test + 1):
        if chain_protocol == 'modbus':
            # Intentar leer el registro de entrada
            read_value = await read_input_register(client, slave_id, input_register_address=0)

            if read_value is not None:
                responsive_slaves.append(slave_id)  # Registrar el ID del esclavo que responde
                sensor_type = ""
                if read_value in [900, 999]:
                    sensor_type = "Sensor de temperatura"
                elif read_value == 200:
                    sensor_type = "Sensor de aire"
                elif read_value == 100:
                    sensor_type = "Sensor de energía"
                elif read_value == 1000:
                    sensor_type = "Sonda"
                else:
                    sensor_type = "ID de sensor desconocido"

                print(f"Esclavo {slave_id}: ID de sensor = {read_value}, Tipo de sensor = {sensor_type}")
            else:
                print(f"El esclavo {slave_id} no respondió.")
        elif chain_protocol == 'legacy':
            read_value = legacy_measurement(chain_port, slave_id)
            if read_value is not None:
                responsive_slaves.append(slave_id) 
                print(f"Esclavo {slave_id}: Funcional (legacy)")
            else:
                print(f"El esclavo {slave_id} no respondió")    

    print("\nSensores detectados:")
    print(f"Esclavos que respondieron: {responsive_slaves}")
    
    # Escribir los esclavos que respondieron en un archivo
    with open(filename, "w") as f:
        for slave in responsive_slaves:
            f.write(f"{slave}\n")
    print(f"Los IDs de los esclavos que respondieron han sido escritos en {filename}.")
    
    return responsive_slaves

async def input_manual_slaves(responsive_slaves: list[int], filename="available_slaves.txt") -> None:
    """Solicita al usuario ingresar manualmente los IDs de los esclavos."""
    print("Elige cómo ingresar los IDs de cada esclavo activo:")
    print("1. Ingresar cada ID uno por uno.")
    print("2. Ingresar un rango de IDs (por ejemplo, '2-14' para seleccionar los IDs del 2 al 14).")
    input_method = input("Ingresa '1' para IDs individuales o '2' para un rango: ")

    if input_method == '1':
        print("Ingresa los IDs de cada esclavo activo (1-255). Presiona Enter después de cada ID.")
        while True:
            try:
                slave_id = int(input("ID del esclavo (o presiona Enter para terminar): "))
                if 1 <= slave_id <= 255:
                    responsive_slaves.append(slave_id)
                else:
                    print("Por favor, ingresa un ID de esclavo válido entre 1 y 255.")
            except ValueError:
                break  # Salir del bucle con entrada vacía

    elif input_method == '2':
        responsive_slaves = []
        print("Ingresa el rango de IDs para los esclavos activos en el formato 'inicio-fin' (por ejemplo, '2-14').")
        while True:
            try:
                range_input = input("Ingresa el rango de IDs de los esclavos (o presiona Enter para terminar): ")
                if not range_input:  # Salir con entrada vacía
                    break
                start_id, end_id = map(int, range_input.split('-'))
                
                if 1 <= start_id <= 255 and 1 <= end_id <= 255 and start_id <= end_id:
                    responsive_slaves.extend(range(start_id, end_id + 1))
                else:
                    print("Por favor, ingresa un rango válido entre 1 y 255, con el ID de inicio menor o igual al ID de fin.")
            except ValueError:
                print("Entrada no válida. Por favor, ingresa el rango en el formato 'inicio-fin'.")

    # Guardar los IDs de los esclavos que respondieron en el archivo disponible_slaves.txt
    with open(filename, "w") as f:
        for slave in responsive_slaves:
            f.write(f"{slave}\n")
    print(f"Los IDs de los esclavos que respondieron han sido escritos en {filename}.")

async def list_sensors_json(client, chain_port = "", chain_protocol="modbus") -> list[int]:
    """Reads input register 0 of each slave up to a specified number and writes detected sensors to a JSON file."""
    # Get the number of slaves to test
    while True:
        try:
            num_slaves_to_test = int(input("Ingresa el número de esclavos que deseas probar (1-255): "))
            print("")
            if 1 <= num_slaves_to_test <= 255:
                break
            else:
                print("Por favor, ingresa un número entre 1 y 255.")
        except ValueError:
            print("Entrada no válida. Por favor, ingresa un número entero entre 1 y 255.")
    
    responsive_slaves = []

    # Detect responsive slaves
    for slave_id in range(1, num_slaves_to_test + 1):
        if chain_protocol == 'modbus':
            # Intentar leer el registro de entrada
            read_value = await read_input_register(client, slave_id, input_register_address=0)

            if read_value is not None:
                responsive_slaves.append(slave_id)  # Registrar el ID del esclavo que responde
                sensor_type = ""
                if read_value in [900, 999]:
                    sensor_type = "Sensor de temperatura"
                elif read_value == 200:
                    sensor_type = "Sensor de aire"
                elif read_value == 100:
                    sensor_type = "Sensor de energía"
                elif read_value == 1000:
                    sensor_type = "Sonda"
                else:
                    sensor_type = "ID de sensor desconocido"

                print(f"Esclavo {slave_id}: ID de sensor = {read_value}, Tipo de sensor = {sensor_type}")
            else:
                print(f"El esclavo {slave_id} no respondió.")
        elif chain_protocol == 'legacy':
            read_value = legacy_measurement(chain_port, slave_id)
            if read_value is not None:
                responsive_slaves.append(slave_id) 
                print(f"Esclavo {slave_id}: Funcional (legacy)")
            else:
                print(f"El esclavo {slave_id} no respondió")

    print("\nDetected sensors:")
    print(f"Responsive slaves: {responsive_slaves}")
    
    return responsive_slaves

async def input_manual_slaves_json() -> list[int]:
    """Prompts the user to input slave IDs manually and saves them to a JSON file."""

    responsive_slaves = []

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

    return responsive_slaves

def file_is_valid(filename="available_slaves.txt") -> bool:
    """Verifica si el archivo existe y contiene IDs de esclavos válidos."""
    if os.path.exists(filename):
        with open(filename, "r") as f:
            lines = f.readlines()
            # Verificar si el archivo está vacío o contiene solo espacios
            if not lines or all(not line.strip() for line in lines):
                print(f"{filename} está vacío o no contiene números válidos.")
                return False
            else:
                try:
                    # Verificar si todas las líneas se pueden convertir a enteros
                    [int(line.strip()) for line in lines]
                    return True
                except ValueError:
                    print(f"Se encontraron datos inválidos en {filename}. Por favor, detecta los esclavos o ingrésalos manualmente.")
                    return False
    else:
        print(f"No se encontró {filename}. Por favor, detecta los esclavos o ingrésalos manualmente.")
        return False
    
def get_responsive_slaves(filename="available_slaves.txt") -> list[int]:
    """Recupera una lista de IDs de esclavos que responden desde el archivo."""
    responsive_slaves = []
    
    if file_is_valid(filename):
        with open(filename, "r") as f:
            lines = f.readlines()
            try:
                responsive_slaves = [int(line.strip()) for line in lines if line.strip()]
                # Filtrar para asegurar que todos los IDs estén en el rango 1-255
                responsive_slaves = [slave_id for slave_id in responsive_slaves if 1 <= slave_id <= 255]
                
                if responsive_slaves:
                    print(f"Esclavos que respondieron cargados desde {filename}: {responsive_slaves}")
                else:
                    print(f"No se encontraron IDs de esclavos válidos en {filename}.")
            except ValueError:
                print(f"Error al convertir los datos en {filename}.")
    
    return responsive_slaves

async def slave_data_menu(client, com_port, protocol):
    responsive_slaves = []
    print("")
    print("-------- Obtención de Slaves Disponivles --------")
    print("1. Detectar los esclavos disponibles (esto modificará el archivo)")
    print("2. Ingresar los esclavos disponibles manualmente (esto también modificará el archivo)")
    option = validate_two_options("Seleccione una opción (1 o 2): ")

    if option == '1':
        if protocol == 'modbus':
            responsive_slaves = await list_sensors_json(client)
        elif protocol == 'legacy':
             responsive_slaves = await list_sensors_json(client, com_port, protocol)
    elif option == '2':
        responsive_slaves = await input_manual_slaves_json()

    return responsive_slaves