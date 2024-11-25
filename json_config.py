import json
import os
from pymodbus.client import AsyncModbusSerialClient
from pymodbus import FramerType
from typing import List
from validate import *
from get_set_available_slaves import *
from manage_ports import list_ports
from manage_ports import select_port_multiple

class Config:
    def __init__(self, num_chains: int, chains_ports: List[str], chain_available_slaves: List[List[int]], log_file_names_raw: List[str]):
        self.num_chains = num_chains
        self.chains_ports = chains_ports
        self.chain_available_slaves = chain_available_slaves
        self.log_file_names_raw = log_file_names_raw

    # Método para guardar la configuración en un archivo JSON
    def save_to_json(self, filename: str):
        with open(filename, 'w') as file:
            json.dump(self.__dict__, file, indent=4)

    # Método estático para cargar la configuración desde un archivo JSON
    @staticmethod
    def load_from_json(filename: str) -> 'Config':
        with open(filename, 'r') as file:
            data = json.load(file)
            return Config(
                num_chains=data['num_chains'],
                chains_ports=data['chains_ports'],
                chain_available_slaves=data['chain_available_slaves'],
                log_file_names_raw=data['log_file_names_raw']
            )
        
async def config_menu(filename):
    print ("config menu")
    chain_clients = []

    config = Config(
        num_chains=0,
        chains_ports=[],
        chain_available_slaves=[],
        log_file_names_raw=[]
    )
    
    config_file_exists = os.path.exists(filename)
    config_option = 0
    if config_file_exists:
        print("")
        print("1. Usar la útlima configuración guardada")
        print("2. Configurar (número de cadenas, puertos, información de sensores disponibles, etc)")
        config_option = validate_two_options("Seleccione una opción (1 o 2): ")
    if config_option == '1' and config_file_exists:
        if validate_config_file(filename):
            config = load_config(filename)
            for i in range(config.num_chains):
                # Crea un cliente para cada cadena de sensores
                client = AsyncModbusSerialClient(
                    port = config.chains_ports[i],
                    framer = FramerType.RTU,
                    baudrate = 9600,
                    bytesize = 8,
                    parity = "N",
                    stopbits = 1,
                    timeout = 1
                )
                print("")  # Línea vacía
                print("Conectando al servidor...")
                await client.connect()
                if client.connected:
                    print(f"Conexión exitosa en el puerto {config.chains_ports[i]}.")
                else:
                    print(f"Error de conexión para la cadena de sensores {i}, puerto {config.chains_ports[i]}.")
                chain_clients.append(client)
        else:
            print("Deberá realizar la configuración nuevamente")
            config, chain_clients= await set_config(filename)            
    elif config_option == '2' or not config_file_exists:
        config, chain_clients= await set_config(filename)

    # Muestra las cadenas y archivos de registro seleccionados para verificación
    print("")  # Línea vacía
    print("Cadenas seleccionadas:", config.chains_ports)
    print("Archivos de registro (crudo):", config.log_file_names_raw)
    print("")  # Línea vacía

    print("config: ")
    print(f"num_chains= {config.num_chains}")
    print(f"chains_ports= {config.chains_ports}")
    print(f"chain_available_slaves= {config.chain_available_slaves}")
    print(f"log_file_names_raw= {config.log_file_names_raw}")
    
    return config, chain_clients

def load_config(filename: str) -> Config | None:
    """
    Carga la configuración desde un archivo JSON y la retorna como un objeto Config.

    Args:
        filename (str): Nombre del archivo JSON.

    Returns:
        Config | None: Objeto Config si la carga es exitosa, None en caso de error.
    """
    if not validate_config_file(filename):
        return None

    try:
        with open(filename, 'r') as file:
            config_data = json.load(file)

        return Config(
            num_chains=config_data["num_chains"],
            chains_ports=config_data["chains_ports"],
            chain_available_slaves=config_data["chain_available_slaves"],
            log_file_names_raw=config_data["log_file_names_raw"]
        )
    except Exception as e:
        print(f"Error al cargar la configuración: {e}")
        return None

async def set_config(filename):   
    chain_clients = []
    
    config = Config(
        num_chains=0,
        chains_ports=[],
        chain_available_slaves=[],
        log_file_names_raw=[]
    )
    
    config.num_chains = validate_positive_number("Ingrese el número de cadenas que planea probar (1 - cantidad de cadenas conectadas (COM) en su PC): ")
    print("")  # Línea vacía
    ports = list_ports()        

    for i in range(config.num_chains):
        print(f"Seleccione el puerto COM para la cadena {i + 1}")
        selected_port = select_port_multiple(ports)  
        config.chains_ports.append(selected_port)
        config.log_file_names_raw.append(f"auto_test_log_{i}.txt")
        # Crea un cliente para cada cadena de sensores
        client = AsyncModbusSerialClient(
            port = config.chains_ports[i],
            framer = FramerType.RTU,
            baudrate = 9600,
            bytesize = 8,
            parity = "N",
            stopbits = 1,
            timeout = 1
        )
        
        print("")  # Línea vacía
        print("Conectando al servidor...")
        await client.connect()
        if client.connected:
            print(f"Conexión exitosa en el puerto {config.chains_ports[i]}.")
        else:
            print(f"Error de conexión para la cadena de sensores {i}, puerto {config.chains_ports[i]}.")
        
        chain_clients.append(client)
        config.chain_available_slaves.append(await slave_data_menu(chain_clients[i]))

    config.save_to_json(filename)

    return config, chain_clients