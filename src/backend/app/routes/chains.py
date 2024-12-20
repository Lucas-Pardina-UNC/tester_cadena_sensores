
from flask import Blueprint, jsonify, request
import os
import json

from .projects import load_projects

chains_bp = Blueprint("chains", __name__)

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
    result_columns = f"{start_column}1-{end_column}3"

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