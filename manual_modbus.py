from modbus_functions import * 

async def manual_modbus(client):
    """Allows manual use of Modbus commands."""
    register_value = 0

    while True:
        print("\nModbus Manual Mode")
        print("1. Write Holding Register")
        print("2. Read Holding Register")
        print("3. Write Coil")
        print("4. Read Input Register")
        print("5. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            slave_id = int(input("Enter slave ID: "))
            register_address = int(input("Enter register address: "))
            value = int(input("Enter value to write: "))
            await write_holding_register(client, slave_id, register_address, value)
        elif choice == "2":
            slave_id = int(input("Enter slave ID: "))
            register_address = int(input("Enter register address: "))
            await read_holding_register(client, slave_id, register_address)
        elif choice == "3":
            slave_id = int(input("Enter slave ID: "))
            coil_address = int(input("Enter coil address: "))
            value = bool(int(input("Enter value (0 or 1): ")))
            await write_coil(client, slave_id, coil_address, value)
        elif choice == "4":
            slave_id = int(input("Enter slave ID: "))
            register_address = int(input("Enter register address: "))
            register_value = await read_input_register(client, slave_id, register_address)
            if register_value is not None:
                print(f"Obtained Input Register value: {register_value}")
            else: 
                print(f"Could not read input register {register_address} for slave {slave_id}")
        elif choice == "5":
            break
        else:
            print("Invalid option. Please select again.")