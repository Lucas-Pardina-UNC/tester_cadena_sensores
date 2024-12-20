
from flask import Blueprint, jsonify, request
from serial.tools.list_ports_common import ListPortInfo
import serial.tools.list_ports
import os
from .projects import load_projects, save_projects

other_bp = Blueprint("other", __name__)

@other_bp.route('/api/project-files', methods=['POST'])
def get_project_files():
    """Returns a list of files in the specified project folder"""
    data = request.json
    folder_path = data.get("folder")

    if not folder_path or not os.path.exists(folder_path):
        return jsonify({"status": "error", "message": "Invalid folder path."}), 400

    try:
        files = os.listdir(folder_path)
        return jsonify({"status": "success", "files": files})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@other_bp.route('/delete-project/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project by ID"""
    projects = load_projects()
    updated_projects = [project for project in projects if project["id"] != project_id]

    if len(updated_projects) == len(projects):
        return jsonify({"status": "error", "message": "Project not found."}), 404

    save_projects(updated_projects)
    return jsonify({"status": "success", "message": f"Project {project_id} has been deleted."})

@other_bp.route('/selected-project', methods=['GET'])
def get_selected_project():
    #Returns the selected project's name and folder path
    projects = load_projects()
    selected_project = next((project for project in projects if project["selected"]), None)

    print(f"sel project: {selected_project}")

    if selected_project:
        return jsonify({
            "status": "success",
            "name": selected_project["name"],
            "folder": selected_project["folder"]
        })
    else:
        return jsonify({"status": "error", "message": "No project is selected."}), 404
    
@other_bp.route('/selected-project-id', methods=['GET'])
def get_selected_project_id():
    """Returns the selected project's ID"""
    projects = load_projects()
    selected_project = next((project for project in projects if project["selected"]), None)

    if selected_project:
        return jsonify({
            "status": "success",
            "id": selected_project["id"]
        })
    else:
        return jsonify({"status": "error", "message": "No project is selected."}), 404


@other_bp.route('/list-com-ports', methods=['GET'])
def list_com_ports():
    """Endpoint to list all available COM ports."""
    ports = serial.tools.list_ports.comports()
    port_list = [{"device": port.device, "description": port.description} for port in ports]
    return jsonify({"status": "success", "ports": port_list})