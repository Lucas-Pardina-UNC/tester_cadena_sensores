from flask import Flask, Blueprint, request, jsonify

project_data_bp = Blueprint("project_data", __name__)

# Project data management class
class ProjectDataManager:
    def __init__(self):
        # In-memory storage (could be replaced with persistent storage later)
        self.projects_data = {}

    def get_project_data(self, project_name):
        return self.projects_data.get(project_name)

    def save_project_data(self, project_name, project_data):
        self.projects_data[project_name] = project_data

    def add_chain_to_project(self, project_name, chain_data):
        project_data = self.get_project_data(project_name) or {"chains": []}
        project_data["chains"].append(chain_data)
        self.save_project_data(project_name, project_data)

    def update_chain_data(self, project_name, chain_port, updated_chain_data):
        project_data = self.get_project_data(project_name)
        if not project_data:
            raise ValueError(f"Project {project_name} not found.")
        
        for chain in project_data["chains"]:
            if chain["chain_port"] == chain_port:
                chain.update(updated_chain_data)
                break
        else:
            raise ValueError(f"Chain with port {chain_port} not found in project {project_name}.")

# Initialize the manager globally
project_data_manager = ProjectDataManager()

# Blueprint for project data routes
project_data_bp = Blueprint("project_data", __name__)

@project_data_bp.route("/get_project_data/<project_name>", methods=["GET"])
def get_project_data(project_name):
    project_data = project_data_manager.get_project_data(project_name)
    if not project_data:
        return jsonify({"error": "Project not found"}), 404
    return jsonify(project_data), 200


@project_data_bp.route("/save_project_data", methods=["POST"])
def save_project_data():
    data = request.json
    project_name = data.get("project_name")
    project_data = data.get("project_data")

    if not project_name or not project_data:
        return jsonify({"error": "Missing project_name or project_data"}), 400

    project_data_manager.save_project_data(project_name, project_data)
    return jsonify({"message": f"Project {project_name} data saved successfully."}), 200


@project_data_bp.route("/add_chain_to_project", methods=["POST"])
def add_chain_to_project():
    data = request.json
    project_name = data.get("project_name")
    chain_data = data.get("chain_data")

    if not project_name or not chain_data:
        return jsonify({"error": "Missing project_name or chain_data"}), 400

    project_data_manager.add_chain_to_project(project_name, chain_data)
    return jsonify({"message": f"Chain added to project {project_name} successfully."}), 200
