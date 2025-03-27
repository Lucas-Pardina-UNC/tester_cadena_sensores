from typing import Union
from flask import Blueprint, jsonify, request
import os
import json

from .projects import load_projects

chains_bp = Blueprint("chains", __name__)

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

@chains_bp.route('/add-chain/<project_id>', methods=['POST'])
def add_sensor_chain(project_id):
    """Add a sensor chain to the project config.json"""
    data = request.json
    chain_data = {
        "chain_port": data.get("chain_port"),
        "baudrate": data.get("baudrate"),
        "bytesize": data.get("bytesize"),
        "parity": data.get("parity"),
        "stopbits": data.get("stopbits"),
        "timeout": data.get("timeout"),
        "chain_protocol": data.get("chain_protocol"),
        "chain_available_slaves": data.get("chain_available_slaves")
    }

    # For aerials, slave 8 has sensor_id = "TE" as default, but in truth it contains the calibration coefficients => sensor_id = "COEF"
    if(chain_data["chain_protocol"] == "legacy"):
        if((chain_data["chain_available_slaves"][0]["sensor_id"] == "TE") and (chain_data["chain_available_slaves"][1]["sensor_id"] == "HU") and (chain_data["chain_available_slaves"][2]["sensor_id"] == "PA") and (chain_data["chain_available_slaves"][3]["sensor_id"] == "TE")):
            chain_data["chain_available_slaves"][3]["sensor_id"] = "COEF"
            chain_data["chain_available_slaves"][3]["sensor_type"] = "Calibration_Coefficients"

    # Load existing projects
    projects = load_projects()

    # Find the project by ID
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        return jsonify({"status": "error", "message": "Project not found."}), 404

    # Load the config.json file inside the project folder
    config_file_path = os.path.join(project["folder"], "config.json")
    if not os.path.exists(config_file_path):
        return jsonify({"status": "error", "message": "Config file not found."}), 404

    with open(config_file_path, "r") as config_file:
        config_data = json.load(config_file)

    # Determine the new chain ID and result_columns
    new_chain_id = config_data["num_chains"] + 1
    column_start = (new_chain_id - 1) * 4
    column_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    start_column = column_letters[column_start]
    mid_column = column_letters[column_start + 1]
    end_column = column_letters[column_start + 2]
    result_columns = f"{start_column}-{end_column}"

    # Update the chain data with ID and result_columns
    chain_data["id"] = new_chain_id
    chain_data["result_columns"] = result_columns

    # Add the new chain to the config
    config_data["chains"].append(chain_data)
    config_data["num_chains"] += 1

    # Save the updated config
    with open(config_file_path, "w") as config_file:
        json.dump(config_data, config_file, indent=4)

    return jsonify({"status": "success", "message": "Sensor chain added successfully.", "chain": chain_data})


@chains_bp.route('/get-chains', methods=['GET'])
def get_chains():
    """Return the list of sensor chains for the selected project."""
    # Get the selected project
    projects = load_projects()
    selected_project = next((project for project in projects if project["selected"]), None)

    if not selected_project:
        return jsonify({"status": "error", "message": "No project is selected."}), 404

    # Path to the config.json file
    config_file_path = os.path.join(selected_project["folder"], "config.json")

    if not os.path.exists(config_file_path):
        return jsonify({"status": "error", "message": "Config file not found."}), 404

    try:
        # Load the config.json
        with open(config_file_path, "r") as config_file:
            config_data = json.load(config_file)

        # Return the chains data
        return jsonify({
            "status": "success",
            "chains": config_data.get("chains", [])
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@chains_bp.route('/update-chain/<int:chain_id>', methods=['PUT'])
def update_sensor_chain(chain_id):
    """
    Update an existing sensor chain in the project config.json by its ID.
    """
    data = request.json

    # Load existing projects
    projects = load_projects()

    # Get the selected project
    selected_project = next((project for project in projects if project["selected"]), None)

    if not selected_project:
        return jsonify({"status": "error", "message": "No project is selected."}), 404

    # Path to the config.json file
    config_file_path = os.path.join(selected_project["folder"], "config.json")

    if not os.path.exists(config_file_path):
        return jsonify({"status": "error", "message": "Config file not found."}), 404

    try:
        # Load the config.json
        with open(config_file_path, "r") as config_file:
            config_data = json.load(config_file)

        # Find the chain to update by its ID
        chain_to_update = next((chain for chain in config_data.get("chains", []) if chain["id"] == chain_id), None)

        if not chain_to_update:
            return jsonify({"status": "error", "message": f"Chain with ID {chain_id} not found."}), 404

        # Update the chain properties
        for key, value in data.items():
            if key in chain_to_update:
                chain_to_update[key] = value

        # Save the updated config
        with open(config_file_path, "w") as config_file:
            json.dump(config_data, config_file, indent=4)

        return jsonify({
            "status": "success",
            "message": f"Sensor chain with ID {chain_id} updated successfully.",
            "chain": chain_to_update
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@chains_bp.route('/delete-chain/<int:chain_id>', methods=['DELETE'])
def delete_sensor_chain(chain_id):
    """
    Delete a sensor chain from the project config.json by its ID
    and rearrange the IDs and result_columns of remaining chains.
    """
    # Load existing projects
    projects = load_projects()

    # Get the selected project
    selected_project = next((project for project in projects if project["selected"]), None)

    if not selected_project:
        return jsonify({"status": "error", "message": "No project is selected."}), 404

    # Path to the config.json file
    config_file_path = os.path.join(selected_project["folder"], "config.json")

    if not os.path.exists(config_file_path):
        return jsonify({"status": "error", "message": "Config file not found."}), 404

    try:
        # Load the config.json
        with open(config_file_path, "r") as config_file:
            config_data = json.load(config_file)

        # Find the chain to delete by its ID
        chain_to_delete = next((chain for chain in config_data.get("chains", []) if chain["id"] == chain_id), None)

        if not chain_to_delete:
            return jsonify({"status": "error", "message": f"Chain with ID {chain_id} not found."}), 404

        # Remove the chain from the list
        config_data["chains"] = [chain for chain in config_data["chains"] if chain["id"] != chain_id]

        # Reindex the remaining chains and update result_columns
        base_columns = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # Adjust for Excel-style columns
        for index, chain in enumerate(config_data["chains"]):
            new_id = index + 1
            chain["id"] = new_id

            # Calculate result_columns: 3 columns per chain + 1 gap column
            start_col_index = (new_id - 1) * 4  # 4 columns per chain (3 data + 1 gap)
            start_col = base_columns[start_col_index]
            end_col = base_columns[start_col_index + 2]  # End of the 3-column range
            chain["result_columns"] = f"{start_col}-{end_col}"

        # Update the number of chains
        config_data["num_chains"] = len(config_data["chains"])

        # Save the updated config
        with open(config_file_path, "w") as config_file:
            json.dump(config_data, config_file, indent=4)

        return jsonify({
            "status": "success",
            "message": f"Sensor chain with ID {chain_id} deleted successfully.",
            "updated_chains": config_data["chains"]
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500