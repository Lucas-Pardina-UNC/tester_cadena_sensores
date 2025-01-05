from flask import Flask, Blueprint, request, jsonify
from typing import List, Tuple, Optional
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