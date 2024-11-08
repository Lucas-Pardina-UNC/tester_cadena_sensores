from pymodbus import ModbusException
from pymodbus.client import AsyncModbusSerialClient

async def write_holding_register(client: AsyncModbusSerialClient, slave_id: int, register_address: int, value: int) -> None:
    """Escribe en un registro de mantenimiento específico de un esclavo específico."""
    try:
        # Escribir el valor en el registro de mantenimiento
        write_response = await client.write_register(register_address, value, slave=slave_id)
        if write_response.isError():
            print(f"Error al escribir en el registro de mantenimiento {register_address} del esclavo {slave_id}: {write_response}")
        else:
            print(f"Escritura exitosa en el registro de mantenimiento {register_address} del esclavo {slave_id}.")
    except ModbusException as exc:
        print(f"ModbusException al escribir en el registro de mantenimiento: {exc}")

async def read_holding_register(client: AsyncModbusSerialClient, slave_id: int, register_address: int) -> int:
    """Lee un registro de mantenimiento específico de un esclavo específico."""
    try:
        # Leer el registro de mantenimiento
        read_response = await client.read_holding_registers(register_address, count=1, slave=slave_id)
        if read_response.isError():
            print(f"Error al leer el registro de mantenimiento {register_address} del esclavo {slave_id}: {read_response}")
        else:
            value = read_response.registers[0]
            print(f"Valor del registro de mantenimiento {register_address} del esclavo {slave_id}: {value}")
            return value  # Retorna el valor leído
    except ModbusException as exc:
        print(f"ModbusException al leer el registro de mantenimiento: {exc}")
        return None  # Retorna None en caso de error

async def write_coil(client: AsyncModbusSerialClient, slave_id: int, coil_address: int, value: bool) -> None:
    """Escribe en una bobina específica de un esclavo específico."""
    try:
        # Escribir el valor en la bobina
        write_response = await client.write_coil(coil_address, value, slave=slave_id)
        if write_response.isError():
            print(f"Error al escribir en la bobina {coil_address} del esclavo {slave_id}: {write_response}")
        else:
            print(f"Escritura exitosa en la bobina {coil_address} del esclavo {slave_id}.")
    except ModbusException as exc:
        print(f"ModbusException al escribir en la bobina: {exc}")

async def read_input_register(client: AsyncModbusSerialClient, slave_id: int, input_register_address: int) -> int:
    """Lee un registro de entrada específico de un esclavo específico."""
    try:
        # Leer el registro de entrada
        read_response = await client.read_input_registers(input_register_address, count=1, slave=slave_id)
        if read_response.isError():
            print(f"Error al leer el registro de entrada {input_register_address} del esclavo {slave_id}: {read_response}")
        else:
            value = read_response.registers[0]
            return value  # Retorna el valor leído
    except ModbusException as exc:
        print(f"ModbusException al leer el registro de entrada: {exc}")
        print("Cerrando la conexión...")
        try:
            client.close()
        except Exception as e:
            print(f"Error al cerrar el cliente: {e}")
        if not client.connected:
            print("El cliente no está conectado, intentando reconexión...")
            await client.connect()
            if client.connected:
                print("Reconexión exitosa.")
            else:
                print("No se pudo reconectar. Saliendo de la detección del sensor.")
        return None  # Retorna None en caso de error