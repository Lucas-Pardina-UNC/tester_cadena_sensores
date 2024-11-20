from modbus_functions import *

async def manual_modbus(client: AsyncModbusSerialClient) -> None:
    """Permite el uso manual de comandos Modbus."""
    register_value = 0

    while True:
        print("\nModo Manual Modbus")
        print("1. Escribir en Registro de Mantenimiento")
        print("2. Leer Registro de Mantenimiento")
        print("3. Escribir Bobina")
        print("4. Leer Registro de Entrada")
        print("5. Salir")
        choice = input("Selecciona una opción: ")

        if choice == "1":
            slave_id = int(input("Ingresa el ID del esclavo: "))
            register_address = int(input("Ingresa la dirección del registro: "))
            value = int(input("Ingresa el valor a escribir: "))
            await write_holding_register(client, slave_id, register_address, value)
        elif choice == "2":
            slave_id = int(input("Ingresa el ID del esclavo: "))
            register_address = int(input("Ingresa la dirección del registro: "))
            await read_holding_register(client, slave_id, register_address)
        elif choice == "3":
            slave_id = int(input("Ingresa el ID del esclavo: "))
            coil_address = int(input("Ingresa la dirección de la bobina: "))
            value = bool(int(input("Ingresa el valor (0 o 1): ")))
            await write_coil(client, slave_id, coil_address, value)
        elif choice == "4":
            slave_id = int(input("Ingresa el ID del esclavo: "))
            register_address = int(input("Ingresa la dirección del registro: "))
            register_value = await read_input_register(client, slave_id, register_address)
            if register_value is not None:
                print(f"Valor obtenido del Registro de Entrada: {register_value}")
            else:
                print(f"No se pudo leer el registro de entrada {register_address} para el esclavo {slave_id}")
        elif choice == "5":
            break
        else:
            print("Opción no válida. Por favor, selecciona de nuevo.")