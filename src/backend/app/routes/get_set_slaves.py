from flask import Blueprint, jsonify, request
from typing import List
from pymodbus.client import AsyncModbusSerialClient
from pymodbus import FramerType
from .modbus_functions import read_input_register
from .legacy_commands import legacy_measurement 

slaves_bp = Blueprint("slaves", __name__)

@slaves_bp.route("/list_sensors", methods=["POST"])
async def list_sensors():
    """
    Detect sensors in a chain and return their IDs.
    """
    # Extract data from request JSON
    data = request.json
    num_slaves_to_test = data.get("num_slaves_to_test")
    chain_port = data.get("chain_port")
    chain_protocol = data.get("chain_protocol")

    # Validate input
    if not isinstance(num_slaves_to_test, int) or not (1 <= num_slaves_to_test <= 255):
        return jsonify({"error": "Invalid 'num_slaves_to_test'. Must be an integer between 1 and 255."}), 400

    if chain_protocol not in ["modbus", "legacy"]:
        return jsonify({"error": "Invalid 'chain_protocol'. Must be 'modbus' or 'legacy'."}), 400

    responsive_slaves = []

    for slave_id in range(1, num_slaves_to_test + 1):
        if chain_protocol == "modbus":
            client = AsyncModbusSerialClient(
                port=chain_port,
                framer=FramerType.RTU,
                baudrate=9600,
                bytesize=8,
                parity="N",
                stopbits=1,
                timeout=1
            )
            read_value = await read_input_register(client, slave_id=slave_id, input_register_address=0)  # Replace 'client' as needed
            if read_value is not None:
                responsive_slaves.append(slave_id)
        elif chain_protocol == "legacy":
            read_value = legacy_measurement(chain_port, slave_id)
            if read_value is not None:
                responsive_slaves.append(slave_id)

    # Return responsive slaves in response
    return jsonify({"responsive_slaves": responsive_slaves}), 200