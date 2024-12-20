from flask import Blueprint, jsonify, request
import os
import json
import uuid

PROJECTS_FILE = os.path.join(os.path.dirname(__file__), "..", "myProjects.json")

projects_bp = Blueprint("projects", __name__)

def load_projects():
    """Load existing projects from the JSON file, or return an empty list if file doesn't exist"""
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, "r") as file:
            return json.load(file)
    else:
        return []


def save_projects(projects):
    """Save the list of projects to the JSON file"""
    with open(PROJECTS_FILE, "w") as file:
        json.dump(projects, file, indent=4)

@projects_bp.route('/create-project', methods=['POST'])
def create_project():
    """Create a new project and store it in the JSON file"""
    data = request.json
    project_name = data.get("name")
    folder_path = data.get("folder")

    if not project_name or not folder_path:
        return jsonify({"status": "error", "message": "Project name and folder are required."}), 400

    # Load existing projects
    projects = load_projects()

    # Check if a project with the same name already exists
    if any(project["name"] == project_name for project in projects):
        return jsonify({"status": "error", "message": "A project with this name already exists."}), 400

    # Create a new project entry with a sequential id
    new_project = {
        "id": str(uuid.uuid4()),  # Generate a unique ID
        "name": project_name,
        "folder": folder_path,
        "open": True,  # Default to open
        "selected": True  # Set newly created project as selected
    }

    # Set all other projects' selected field to False
    for project in projects:
        project["selected"] = False

    # Add the new project to the list
    projects.append(new_project)

    # Create the config.json file inside the project folder
    config_file_path = os.path.join(folder_path, "config.json")
    config_data = {
        "num_chains": 0,
        "chains": []
    }
    with open(config_file_path, "w") as config_file:
        json.dump(config_data, config_file, indent=4)

    # Save the updated projects list
    save_projects(projects)

    return jsonify({"status": "success", "message": "Project created successfully.", "project": new_project})

@projects_bp.route('/select-project/<project_id>', methods=['PATCH'])
def select_project(project_id):
    """Select a project by ID, setting it as selected and all others as unselected"""
    projects = load_projects()

    # Set the selected field to True for the given project, and False for all others
    for project in projects:
        if project["id"] == project_id:
            project["selected"] = True
        else:
            project["selected"] = False

    # Save the updated projects list
    save_projects(projects)

    return jsonify({"status": "success", "message": f"Project {project_id} is now selected."})


@projects_bp.route('/open-project/<project_id>', methods=['PATCH'])
def open_project(project_id):
    """Set a project's open status to true"""
    projects = load_projects()
    for project in projects:
        if project["id"] == project_id:
            project["open"] = True
            save_projects(projects)
            return jsonify({"status": "success", "message": f"Project {project_id} is now open."})

    return jsonify({"status": "error", "message": "Project not found."}), 404


@projects_bp.route('/close-project/<project_id>', methods=['PATCH'])
def close_project(project_id):
    """Set a project's open status to false"""
    projects = load_projects()
    for project in projects:
        if project["id"] == project_id:
            project["open"] = False
            save_projects(projects)
            return jsonify({"status": "success", "message": f"Project {project_id} is now closed."})

    return jsonify({"status": "error", "message": "Project not found."}), 404

@projects_bp.route('/projects', methods=['GET'])
def get_projects():
    with open('myProjects.json', 'r') as f:
        projects = json.load(f)
    return jsonify(projects)

@projects_bp.route('/api/projects/opened', methods=['GET'])
def get_opened_projects():
    #Returns a list of all opened projects
    projects = load_projects()
    opened_projects = [project for project in projects if project["open"]]
    return jsonify({"status": "success", "opened_projects": opened_projects})
