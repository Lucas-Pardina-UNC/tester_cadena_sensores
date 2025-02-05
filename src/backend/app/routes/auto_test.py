from flask import Blueprint, request, jsonify
from typing import List, Tuple
import asyncio
from datetime import datetime, timedelta
from datetime import datetime
from pymodbus import ModbusException
from pymodbus.exceptions import ModbusException
from .calc_sheets import *
from .legacy_commands import *
from .project_data import *
from .conversion import *

auto_test_bp = Blueprint("auto_test", __name__)

@auto_test_bp.route("/auto_test", methods=["POST"])
async def auto_test():
    data = request.json
    file_path = data.get("file_path")
    log_data = []

    if not file_path:
        return jsonify({"error": "file_path is required"}), 400
    else:
        # Load the project from the provided file path
        load_project_from_file(file_path)

        project = get_project_instance()

        excel_file_path = project.project_folder + "/auto-test.xlsx"
        num_chains = project.num_chains
        chain_protocol = project.chains[0].chain_protocol
        available_slaves = project.chains[0].chain_available_slaves

        for j in range(project.num_chains):
            if(project.chains[j].chain_protocol == "modbus"):
                await project.chains[j].chain_client.connect()
                if project.chains[j].chain_client.connected:
                    print(f"Conexión exitosa en cadena {j} - puerto {project.chains[0].chain_port}.")
                else:
                    print(f"Error de conexión para la cadena {j} - puerto {project.chains[0].chain_port}.")

        for i in range(3):
                print(f"Ciclo: {i}")
                for j in range(project.num_chains):
                    await auto_test_cycle(project.chains[j].chain_client, project.chains[j].chain_port, project.chains[j].chain_protocol, project.chains[j].chain_available_slaves,log_data, excel_file_path , j)

        # Cierra las conexiones si están abiertas
        for i in range(num_chains):
            if(project.chains[j].chain_protocol == "modbus"):
                if project.chains[j].chain_client.connected:
                    try:
                        project.chains[j].chain_client.close()
                    except Exception as e:
                        pass
                        """ print(f"Error al cerrar el cliente: {e}") """
    
    return jsonify({"status": "success" , "num_chains": num_chains, "chain_protocol" :  chain_protocol, "available_slaves" : available_slaves})

@auto_test_bp.route("/auto_test_by_cycles", methods=["POST"])
async def auto_test_by_cycles():
    data = request.json
    file_path = data.get("file_path")
    num_cycles = data.get("num_cycles", 3)  # Default to 3 cycles if not provided
    log_data = []
    
    if not file_path:
        return jsonify({"error": "file_path is required"}), 400
    else:
        # Load the project from the provided file path
        load_project_from_file(file_path)

        project = get_project_instance()

        excel_file_path = project.project_folder + "/auto-test.xlsx"
        num_chains = project.num_chains
        chain_protocol = project.chains[0].chain_protocol
        available_slaves = project.chains[0].chain_available_slaves

        for j in range(project.num_chains):
            if(project.chains[j].chain_protocol == "modbus"):
                await project.chains[j].chain_client.connect()
                if project.chains[j].chain_client.connected:
                    print(f"Conexión exitosa en cadena {j} - puerto {project.chains[0].chain_port}.")
                else:
                    print(f"Error de conexión para la cadena {j} - puerto {project.chains[0].chain_port}.")

        for i in range(num_cycles):
            #print(f"Ciclo: {i}")
            for j in range(project.num_chains):
                await auto_test_cycle(project.chains[j].chain_client, project.chains[j].chain_port, project.chains[j].chain_protocol, project.chains[j].chain_available_slaves, log_data, excel_file_path, j)

        # Cierra las conexiones si están abiertas
        for i in range(num_chains):
            if(project.chains[j].chain_protocol == "modbus"):
                if project.chains[j].chain_client.connected:
                    try:
                        project.chains[j].chain_client.close()
                    except Exception as e:
                        pass
                        # print(f"Error al cerrar el cliente: {e}")

    return jsonify({"status": "success", "num_chains": num_chains, "chain_protocol": chain_protocol, "available_slaves": available_slaves})

@auto_test_bp.route("/auto_test_with_interval", methods=["POST"])
async def auto_test_with_interval():
    """
    Endpoint to perform an auto-test for a specified total duration and interval between measurements.
    Expects a JSON payload with the keys:
        - file_path: str (path to the project file)
        - total_duration: int (total testing time in seconds)
        - interval: int (interval time between measurements in seconds)
    """
    data = request.json
    file_path = data.get("file_path")
    total_duration = data.get("total_duration")  # in seconds
    interval = data.get("interval")  # in seconds

    if not file_path or total_duration is None or interval is None:
        return jsonify({"error": "file_path, total_duration, and interval are required"}), 400

    if interval >= total_duration:
        return jsonify({"error": "Interval cannot be greater than or equal to total duration"}), 400

    log_data = []

    try:
        # Load the project from the provided file path
        load_project_from_file(file_path)
        project = get_project_instance()

        excel_file_path = project.project_folder + "/auto-test.xlsx"
        num_chains = project.num_chains

        # Connect all chains
        for j in range(num_chains):
            if project.chains[j].chain_protocol == "modbus":
                await project.chains[j].chain_client.connect()
                if project.chains[j].chain_client.connected:
                    print(f"Conexión exitosa en cadena {j} - puerto {project.chains[j].chain_port}.")
                else:
                    print(f"Error de conexión para la cadena {j} - puerto {project.chains[j].chain_port}.")

        # Calculate end time
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=total_duration)

        print(f"Inicio de prueba automática: {start_time}")
        print(f"Fin de prueba automática: {end_time}")

        # Perform auto-test until end time is reached
        while datetime.now() < end_time:
            for j in range(num_chains):
                await auto_test_cycle(
                    project.chains[j].chain_client,
                    project.chains[j].chain_port,
                    project.chains[j].chain_protocol,
                    project.chains[j].chain_available_slaves,
                    log_data,
                    excel_file_path,
                    j
                )
            await asyncio.sleep(interval)  # Wait for the specified interval

        # Close connections if open
        for j in range(num_chains):
            if project.chains[j].chain_protocol == "modbus" and project.chains[j].chain_client.connected:
                try:
                    project.chains[j].chain_client.close()
                except Exception as e:
                    print(f"Error al cerrar el cliente de la cadena {j}: {e}")

        return jsonify({
            "status": "success",
            "message": "Auto-test completed successfully",
            "num_chains": num_chains
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auto_test_bp.route("/read_sensor", methods=["POST"])
async def read_sensor():
    """
    Endpoint to read the sensor value of a specific slave.
    Expects JSON payload with "chain_id" and "slave_id".
    """
    data = request.json
    file_path = data.get("file_path")
    chain_id = data.get("chain_id")
    slave_id = data.get("slave_id")

    chain_id_type = type(chain_id)
    slave_id_type = type(slave_id)

    if chain_id is None or slave_id is None:
        return jsonify({"error": "chain_id and slave_id are required"}), 400

    if not file_path:
            return jsonify({"error": "file_path is required"}), 400

    try:
        # Get the current project instance
        load_project_from_file(file_path)
        project = get_project_instance()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Validate chain_id
    if chain_id < 0 or chain_id > project.num_chains:
        return jsonify({"error": "Invalid chain_id"}), 400
    
    chain = project.chains[chain_id -1]

    # Ensure the chain uses the Modbus protocol
    if chain.chain_protocol == "modbus":
        #return jsonify({"error": "Only Modbus protocol is supported for this operation"}), 400

        # Connect to the chain's client if not already connected
        if not chain.chain_client.connected:
            await chain.chain_client.connect()

        if not chain.chain_client.connected:
            return jsonify({"error": f"Failed to connect to chain {chain_id}"}), 500

        # Perform the sensor reading
        try:
            write_response = await chain.chain_client.write_coil(0, True, slave=slave_id)
            if write_response.isError():
                return jsonify({"error": f"Failed to write to coil 0 for slave {slave_id}"}), 500

            read_response = await chain.chain_client.read_input_registers(2, count=1, slave=slave_id)
            if read_response.isError():
                return jsonify({"error": f"Failed to read input register 2 for slave {slave_id}"}), 500

            # Process the sensor data
            adc_value = read_response.registers[0]
            temperature = adc_to_temperature(adc_value)

            # Close connections if open
            if chain.chain_client.connected:
                try:
                    chain.chain_client.close()
                except Exception as e:
                    print(f"Error al cerrar el cliente de la cadena {chain_id}: {e}", flush=True)
        except ModbusException as e:
            return jsonify({"error": f"Modbus error: {str(e)}"}), 500
    
    elif chain.chain_protocol == "legacy":
        adc_value = legacy_measurement(chain.chain_port, slave_id)
        print(f"ADC_Value: {adc_value}", flush=True)
        print(f"Type of legacy adc value= {type(adc_value)}", flush=True)
        temperature = adc_to_temperature(int(adc_value))

    return jsonify({
            "status": "success",
            "chain_id": chain_id,
            "slave_id": slave_id,
            "adc_value": adc_value,
            "temperature": temperature
        }), 200
    
@auto_test_bp.route("/get_sensor_id_and_type", methods=["POST"])
async def read_slave_id():
    """
    Endpoint to read the ID and sensor type from input register 0 for a specific slave in a specific chain.
    Expects a JSON payload with the keys 'chain_id' and 'slave_id'.
    """
    try:
        # Parse JSON payload
        data = request.json
        file_path = data.get("file_path")
        chain_id = data.get("chain_id")
        slave_id = data.get("slave_id")

        if chain_id is None or slave_id is None:
            return jsonify({"error": "Both 'chain_id' and 'slave_id' are required"}), 400

        # Get the current project instance
        load_project_from_file(file_path)
        project = get_project_instance()

        # Validate chain_id
        if chain_id < 0 or chain_id > project.num_chains:
            return jsonify({"error": f"Invalid chain_id. Must be between 0 and {project.num_chains - 1}"}), 400

        chain = project.chains[chain_id -1]

        # Validate that the chain uses Modbus protocol
        if chain.chain_protocol == "modbus":
            #return jsonify({"error": "This chain does not use the Modbus protocol"}), 400

            # Establish connection if not already connected
            if not chain.chain_client.connected:
                await chain.chain_client.connect()

            if not chain.chain_client.connected:
                return jsonify({"error": f"Failed to connect to chain {chain_id}"}), 500

            # Read the input register 0
            sensor_id = None
            sensor_type = "Unknown sensor type"
            try:
                read_response = await chain.chain_client.read_input_registers(0, count=1, slave=slave_id)
                if not read_response.isError():
                    sensor_id = read_response.registers[0]

                    # Determine the sensor type
                    if sensor_id in [900, 999]:
                        sensor_type = "Temperature sensor"
                    elif sensor_id == 200:
                        sensor_type = "Air sensor"
                    elif sensor_id == 100:
                        sensor_type = "Energy sensor"
                    elif sensor_id == 1000:
                        sensor_type = "Probe"
                    else:
                        sensor_type = "Unknown sensor ID"
                else:
                    return jsonify({"error": f"Failed to read input register 0 for slave {slave_id}"}), 500
            except ModbusException:
                return jsonify({"error": f"Modbus exception occurred while reading from slave {slave_id}"}), 500
            except Exception as e:
                return jsonify({"error": str(e)}), 500

            # Close connections if open
            if chain.chain_client.connected:
                try:
                    chain.chain_client.close()
                except Exception as e:
                    print(f"Error al cerrar el cliente de la cadena {chain_id}: {e}")
        elif chain.chain_protocol == "legacy":
            [sensor_id, sensor_type] = legacy_get_sensor_id(chain.chain_port, slave_id)
        # Return the sensor ID and type
        return jsonify({
            "status": "success",
            "chain_id": chain_id,
            "slave_id": slave_id,
            "sensor_id": sensor_id,
            "sensor_type": sensor_type
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

async def auto_test_cycle(client, chain_port, chain_protocol, responsive_slaves: List[int], log_data: List[Tuple[int, int, float]], filepath , chain_id: int = 0) -> None:
    """A single cycle of the auto-test, logging temperatures for responsive slaves."""
    log_data.clear()  # Clear log_data at the beginning of each cycle

    for slave_id in responsive_slaves:
        if chain_protocol == "modbus":
            try:
                write_response = await client.write_coil(0, True, slave=slave_id)
                if not write_response.isError():
                    read_response = await client.read_input_registers(2, count=1, slave=slave_id)
                    if not read_response.isError():
                        ADC_value = read_response.registers[0]
                        temperature = adc_to_temperature(ADC_value)
                        log_data.append((slave_id, ADC_value, temperature))
                    else:
                        print(f"Error al leer el registro de entrada 2 para el esclavo {slave_id}")  
                else:
                    print(f"Error al escribir en la bobina 0 para el esclavo {slave_id}")    
            except ModbusException:
                continue
        elif chain_protocol == "legacy": 
            legacy_value = legacy_measurement(chain_port, slave_id)
            if legacy_value:
                temperature = adc_to_temperature(int(legacy_value))
            else:
                temperature = 4444
            log_data.append((slave_id, legacy_value, temperature))

    # Obtain current date/time
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    
    # Log to excel
    log_to_excel(log_data, current_timestamp, chain_id, filepath)


@auto_test_bp.route("/load_project", methods=["POST"])
async def load_project():
    """
    Endpoint to load a project from a JSON file.
    Expects a JSON payload with the key "file_path" containing the file path to the JSON.
    """
    try:
        data = request.get_json()
        file_path = data.get("file_path")

        if not file_path:
            return jsonify({"error": "file_path is required"}), 400

        # Load the project from the provided file path
        load_project_from_file(file_path)

        # Get the current project instance
        project = get_project_instance()

        # Return the entire project instance as a JSON response
        return jsonify({"message": "Project loaded successfully", "project_data": project.to_json()}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500