from flask import Blueprint, jsonify, request
from typing import List, Union
from pymodbus.client import AsyncModbusSerialClient
from .framer_selector import get_framer #from pymodbus import FramerType
from .modbus_functions import read_input_register
from .legacy_commands import legacy_measurement, legacy_get_sensor_id
from .conversion import get_sensor_type

Framer = get_framer()

slaves_bp = Blueprint("slaves", __name__)

class Slave:
    def __init__(self, slave_id : int, sensor_id: Union[str, int], sensor_type: str):
        self.slave_id = slave_id
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type

    def to_dict(self):
        return {
            "slave_id": self.slave_id,
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type
        }

@slaves_bp.route("/list_sensors", methods=["POST"])
async def list_sensors():
    """
    Detect sensors in a chain and return their IDs.
    """
    # Extract data from request JSON
    data = request.json
    first_slave = data.get("first_slave")
    last_slave = data.get("last_slave")
    chain_port = data.get("chain_port")
    chain_protocol = data.get("chain_protocol")
    connection_success = False

    # Validate input
    if not (isinstance(first_slave, int) and isinstance(last_slave, int)) or not (1 <= first_slave <= last_slave <= 255):
        return jsonify({"error": "Invalid slave range. 'first_slave' and 'last_slave' must be integers between 1 and 255, with first_slave <= last_slave."}), 400

    if chain_protocol not in ["modbus", "legacy"]:
        return jsonify({"error": "Invalid 'chain_protocol'. Must be 'modbus' or 'legacy'."}), 400

    responsive_slaves = []

    if chain_protocol == "modbus":
        client = AsyncModbusSerialClient(
            port=chain_port,
            framer=Framer,  # Use Framer (framer_selector.py) instead of FramerType.RTU for retrocompatiiility
            baudrate=9600,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=1
        )
        print("", flush=True)  # Línea vacía
        print("Conectando al servidor...", flush=True)
        await client.connect()
        if client.connected:
            connection_success = True
            print(f"Conexión exitosa en el puerto {chain_port}.", flush=True)
        else:
            print(f"Error de conexión para la cadena de sensores, puerto {chain_port}.", flush=True)

    for slave_id in range(first_slave, last_slave + 1):
        if chain_protocol == "modbus" and connection_success:
            read_value = await read_input_register(client, slave_id=slave_id, input_register_address=0)  
            if read_value is not None: 
                responsive_slaves.append(Slave(slave_id, read_value, get_sensor_type(read_value)))
                print(f"Modbus Slave {slave_id}: Sensor Type: {get_sensor_type(read_value)} ({read_value})", flush=True)
            else:
                print(f"Modbus Slave {slave_id}: No se detectó ningún sensor.", flush=True)
        elif chain_protocol == "legacy":
            read_value = legacy_get_sensor_id(chain_port, slave_id)
            if read_value is not None:
                [sensor_id, sensor_name] = read_value
                responsive_slaves.append(Slave(slave_id, sensor_id, get_sensor_type(sensor_id)))
                print(f"Legacy Slave {slave_id}: Sensor Type: {sensor_name} ({sensor_id})", flush=True)
            else:
                print(f"Legacy Slave {slave_id}: No se detectó ningún sensor.", flush=True)

    if chain_protocol == "modbus" and connection_success:
        print("Terminé de detectar, me desconecto", flush=True)
        try:
            await client.close()
        except Exception as e:
            print(f"Error al cerrar el cliente: {e}")

    if responsive_slaves:
        return jsonify({"responsive_slaves": [slave.to_dict() for slave in responsive_slaves]}), 200
    else:
        return jsonify({"error": "No Slaves detected."}), 400
