from serial.tools.list_ports_common import ListPortInfo
import serial.tools.list_ports
from typing import Optional, List

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