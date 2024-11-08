from typing import List, Optional
from serial.tools.list_ports_common import ListPortInfo
import serial.tools.list_ports
from PS103J2_table import *
from conversion import *
from auto_test import * 
from manual_modbus import *
from get_set_available_slaves import *
from calc_sheets import *
from multiple_chains import *
from validate_inputs import *

def list_ports() -> Optional[List[ListPortInfo]]:
    """Muestra todos los puertos COM disponibles en el sistema."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No se encontraron puertos disponibles.")
    return ports

def select_port(ports: List[ListPortInfo]) -> str:
    """Permite al usuario seleccionar un puerto COM por índice o número."""
    print("\nPuertos disponibles:")
    for i, port in enumerate(ports):
        print(f"{i + 1}: {port.device} - {port.description}")
    
    while True:
        selection = input("\nSeleccione el número de puerto al que desea conectarse (índice o nombre de puerto, ej., COM11), o 'q' para salir: ")
        print("")  # línea en blanco
        if selection.lower() == 'q':
            print("Saliendo del programa.")
            exit()  # Termina el programa si se ingresa 'q'
        
        try:
            index = int(selection) - 1
            if 0 <= index < len(ports):
                return ports[index].device
        except ValueError:
            for port in ports:
                if port.device == selection.upper():
                    return port.device
        
        print("Por favor ingrese un número de índice válido o el nombre exacto del puerto (ej., COM11).")

def main():
    while True:
        print("Probador de sensor EML - Seleccione una opción:")
        print("1. Iniciar configuración de las cadenas de sensores")
        print("2. Eliminar archivos log")
        print("3. Salir")

        menu_option = validate_three_options("Ingrese la opción seleccionada ('1', '2' o '3'): ")
        print("")  # línea en blanco
        
        if menu_option == "1":
            multiple_chain()
            break
        elif menu_option == "2":  # Opción para eliminar archivos de registro
            delete_log_files()
        elif menu_option == "3":
            print("Saliendo.")
            break

if __name__ == "__main__":
    main()