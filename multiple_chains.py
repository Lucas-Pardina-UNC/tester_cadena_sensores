import asyncio
from pymodbus.client import AsyncModbusSerialClient
from pymodbus import FramerType
from pymodbus import pymodbus_apply_logging_config
from conversion import *
from modbus_functions import * 
import time
from validate_time import *
from auto_test import auto_test_cycle, listen_for_quit
from get_set_available_slaves import *
from sensor_chain_tester import list_ports
from manual_modbus import *
from validate_inputs import *

def select_port_multiple(ports: list) -> str:
    """Permite al usuario seleccionar un puerto COM por índice o número, y luego lo elimina de la lista para evitar su reutilización."""
    print("\nPuertos disponibles:")
    for i, port in enumerate(ports):
        print(f"{i + 1}: {port.device} - {port.description}")
    
    while True:
        selection = input("\nSeleccione el número de puerto al que desea conectarse (índice o número de puerto, ej. COM11), o 'q' para salir: ")
        
        if selection.lower() == 'q':
            print("Saliendo del programa.")
            exit()  # Finaliza el programa si se ingresa 'q'
        
        try:
            index = int(selection) - 1
            if 0 <= index < len(ports):
                selected_port = ports.pop(index)  # Elimina el puerto seleccionado de la lista
                return selected_port.device
        except ValueError:
            for port in ports:
                if port.device == selection.upper():
                    ports.remove(port)  # Elimina el puerto seleccionado por nombre
                    return port.device
        
        print("Por favor, ingrese un número de índice válido o el nombre exacto del puerto (ej. COM11).")


def multiple_chain() -> None:
    num_chains = int(input("Ingrese el número de cadenas que planea probar (1 - cantidad de cadenas conectadas (COM) en su PC): "))
    print("")  # Línea vacía
    ports = list_ports()
    chains_ports = []
    log_file_names_raw = []
    slave_info_file_names = []

    for i in range(num_chains):
        print(f"Seleccione el puerto COM para la cadena {i + 1}")
        selected_port = select_port_multiple(ports)  # Elimina el puerto de la lista después de seleccionarlo
        chains_ports.append(selected_port)
        log_file_names_raw.append(f"auto_test_log_{i}.txt")
        slave_info_file_names.append(f"available_slaves_chain_{i}.txt")

    # Muestra las cadenas y archivos de registro seleccionados para verificación
    print("")  # Línea vacía
    print("Cadenas seleccionadas:", chains_ports)
    print("Archivos de registro (crudo):", log_file_names_raw)
    print("Archivos de información de esclavos:", slave_info_file_names)
    print("")  # Línea vacía

    asyncio.run(run_client_multiple(num_chains, chains_ports, slave_info_file_names, log_file_names_raw))

async def run_client_multiple(num_chains: int, chains_ports: list[str], slave_info_file_names: list[str], log_file_names_raw: list[str]) -> None:
    """Configura y ejecuta el cliente Modbus RTU."""
    pymodbus_apply_logging_config("WARNING")

    chain_clients = []
    chain_available_slaves = []

    for i in range(num_chains):
        # Crea un cliente para cada cadena de sensores
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
        
        # Conecta cada cliente
        print("")  # Línea vacía
        print("Conectando al servidor...")
        await client.connect()
        if client.connected:
            print(f"Conexión exitosa en el puerto {chains_ports[i]}.")
        else:
            print(f"Error de conexión para la cadena de sensores {i}, puerto {chains_ports[i]}.")
    
        # Verifica los esclavos disponibles para cada cadena de sensores
        responsive_slaves = []
        valid_file = False

        print(f"Verificando la configuración de esclavos disponibles para la cadena de sensores {i}...")
        print("")  # Línea vacía

        # Verifica la existencia y validez del archivo available_slaves.txt
        valid_file = file_is_valid(slave_info_file_names[i])

        # Ofrece opciones según la validez del archivo
        if valid_file:
            print("Opciones disponibles:")
            print("1. Usar la información del archivo available_slaves.txt")
            print("2. Detectar los esclavos disponibles (esto modificará el archivo)")
            print("3. Ingresar los esclavos disponibles manualmente (esto también modificará el archivo)")
            option = validate_three_options("Seleccione una opción (1, 2, o 3): ")

            if option == '1':
                responsive_slaves = get_responsive_slaves(slave_info_file_names[i]) 
            elif option == '2':
                responsive_slaves = await list_sensors(client, slave_info_file_names[i])
            elif option == '3':
                await input_manual_slaves(responsive_slaves, slave_info_file_names[i])
            else:
                print("Opción inválida. Saliendo.")
                return

        else:
            print("No se encontró un archivo válido, las únicas opciones disponibles son:")
            print("1. Detectar los esclavos disponibles (esto modificará el archivo)")
            print("2. Ingresar los esclavos disponibles manualmente (esto también modificará el archivo)")
            option = validate_two_options("Seleccione una opción (1 o 2): ")

            if option == '1':
                responsive_slaves = await list_sensors(client, slave_info_file_names[i])
            elif option == '2':
                await input_manual_slaves(responsive_slaves)
            else:
                print("Opción inválida. Saliendo.")
                return

        chain_available_slaves.append(responsive_slaves)

    while True:
        print("")  # Línea vacía
        print("Seleccione opción de prueba:")
        print("1. Prueba automática")
        print("2. Modbus manual (una sola cadena)")
        print("3. Salir")
        test_option = validate_three_options("Seleccione una opción (1, 2, o 3): ")
        print("")  # Línea vacía

        if test_option == '1':
            # Realiza las opciones de prueba
            await auto_test_multiple(num_chains, chain_clients, chain_available_slaves, log_file_names_raw)
        elif test_option == '2':
            print("Cadenas disponibles:")
            for index, chain in enumerate(chain_clients):
                print(f"{index + 1}: Cadena {index + 1} (puerto: {chains_ports[index]})")
            chain_number = int(validate_list_options(chain_clients, "Seleccione la cadena para comunicarse ('1', '2', ...): ")) - 1
            await manual_modbus(chain_clients[chain_number])
        elif test_option == '3':
            break

    # Cierra las conexiones si están abiertas
    for i in range(num_chains):
        if chain_clients[i].connected:
            try:
                chain_clients[i].close()
            except Exception as e:
                print(f"Error al cerrar el cliente: {e}")

async def auto_test_multiple(num_chains: int, chain_clients: list[AsyncModbusSerialClient], chain_responsive_slaves: list[list[int]], log_file_names_raw: list[str]) -> None:    
    """Realiza una prueba automática basada en el modo seleccionado por el usuario."""
    log_data = []

    test_continue = "s"
    while test_continue != "n":
        print("Seleccione el modo de prueba:")
        print("1. Por ciclos")
        print("2. Por tiempo")
        print("3. Continuo")
        print("4. Volver al menú anterior")
        mode = validate_four_options("Ingrese el modo (1, 2, o 3) o 4 para volver al menú anterior: ")
        print("")

        if mode == "1":
            num_cycles = int(input("Ingrese el número de ciclos para la prueba automática: "))
            print(f"Realizando prueba automática por {num_cycles} ciclos.")
            
            for i in range(num_cycles):
                print(f"Ciclo: {i}")
                for j in range(num_chains):
                    await auto_test_cycle(chain_clients[j], chain_responsive_slaves[j], log_data, log_file_names_raw[j], j)

        elif mode == "2":
            # Ask for total duration in "dd:hh:mm:ss" format
            total_time_str = validate_time_input("Ingrese la duración total para la prueba automática (formato dd:hh:mm:ss): ")

            # Convert total testing time to seconds
            total_time = parse_time_input(total_time_str)
            
            # Ask for interval time in "hh:mm:ss" format
            interval_time_str = validate_time_input("Ingrese el tiempo de intervalo entre mediciones (formato dd:hh:mm:ss): ")

            # Convert interval time to seconds
            interval = parse_time_input(interval_time_str)

            while interval >= total_time:
                print("El tiempo de intervalo no puede ser mayor o igual a la duración total.")
                interval_time_str = validate_time_input("Ingrese el tiempo de intervalo (dd:hh:mm:ss): ")
                interval = parse_time_input(interval_time_str)

            # Split the total time and interval into days, hours, minutes, and seconds
            total_days, total_hours, total_minutes, total_seconds = total_time_str.split(":")
            #interval_days = "0"  # Interval has no days
            interval_days, interval_hours, interval_minutes, interval_seconds = interval_time_str.split(":")

            print(f"Realizando prueba automática por {total_days} días, {total_hours} horas, {total_minutes} minutos y {total_seconds} segundos.")
            print(f"Intervalo de {interval_days} días, {interval_hours} horas, {interval_minutes} minutos y {interval_seconds} segundos.")

            # Obtain end time
            end_time = time.time() + total_time
            # Loop to perform auto-test until end time is reached
            
            while time.time() < end_time:
                for j in range(num_chains):
                    await auto_test_cycle(chain_clients[j], chain_responsive_slaves[j], log_data, log_file_names_raw[j], j)
                await asyncio.sleep(interval)  # Wait for the specified interval

        elif mode == "3":
            print("Realizando prueba automática continua. Presione Ctrl+C para detener la prueba.")

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
                        print("Saliendo del modo continuo.")
                        quit_task.cancel()
                        break
            except KeyboardInterrupt:
                print("Auto-test interrumpido.")

        elif mode == "4":
            print("Saliendo")
            break


        print("Auto test completado")
    
        while True:
                test_continue = input("¿Desea continuar con la prueba automática? (s/n): ").strip().lower()  # Get user input and normalize it
                if test_continue in ('s', 'n'):  # Check if the input is either 's' or 'n'
                    break
                else:
                    print("Entrada no válida. Por favor ingrese 's' para sí o 'n' para no.")  # Prompt for valid input