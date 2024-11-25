from PS103J2_table import *
from conversion import *
from auto_test import * 
from manual_modbus import *
from get_set_available_slaves import *
from calc_sheets import *
from multiple_chains import *
from validate import *

def main():
    while True:
        print("Probador de sensor EML - Seleccione una opción:")
        print("1. Iniciar configuración de las cadenas de sensores")
        print("2. Eliminar archivos log")
        print("3. Salir")

        menu_option = validate_three_options("Ingrese la opción seleccionada ('1', '2' o '3'): ")
        print("")  # línea en blanco
        
        if menu_option == "1":
            asyncio.run(multiple_chain()) 
            break
        elif menu_option == "2":  # Opción para eliminar archivos de registro
            delete_log_files()
        elif menu_option == "3":
            print("Saliendo.")
            break

if __name__ == "__main__":
    main()