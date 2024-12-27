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

@projects_bp.route('/api/projects/non-opened', methods=['GET'])
def get_non_opened_projects():
    """Returns a list of all non-opened projects."""
    projects = load_projects()
    non_opened_projects = [project for project in projects if not project["open"]]
    return jsonify({"status": "success", "non_opened_projects": non_opened_projects})

#@projects_bp.route('/open-selected-project/<project_id>', methods=['PATCH'])
@projects_bp.route('/open-project/<project_id>', methods=['PATCH'])
def open_selected_project(project_id):
    """Open a project by its ID and mark it as selected."""
    projects = load_projects()

    # Find the project to open
    project_to_open = next((project for project in projects if project["id"] == project_id), None)

    if not project_to_open:
        return jsonify({"status": "error", "message": "Project not found."}), 404

    # Set all other projects' selected field to False and their open status unchanged
    for project in projects:
        if project["id"] == project_id:
            project["open"] = True
            project["selected"] = True
        else:
            project["selected"] = False

    # Save the updated projects list
    save_projects(projects)

    return jsonify({"status": "success", "message": f"Project {project_id} is now open and selected.", "project": project_to_open})

@projects_bp.route('/close-selected-project', methods=['PATCH'])
def close_selected_project():
    """Close the currently selected project by setting its open status to false."""
    projects = load_projects()

    # Find the currently selected project
    selected_project = next((project for project in projects if project["selected"]), None)

    if not selected_project:
        return jsonify({"status": "error", "message": "No project is currently selected."}), 404

    # Set the open status of the selected project to False
    selected_project["open"] = False
    selected_project["selected"] = False

    # Save the updated projects list
    save_projects(projects)

    return jsonify({"status": "success", "message": f"Project {selected_project['id']} has been closed."})


@projects_bp.route('/delete-project/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project by its ID and remove it from the myProjects.json file and the project folder's config.json"""
    # Load existing projects
    projects = load_projects()

    # Find the project to delete
    project_to_delete = next((project for project in projects if project["id"] == project_id), None)

    if not project_to_delete:
        return jsonify({"status": "error", "message": "Project not found."}), 404

    # Get the folder path of the project
    project_folder = project_to_delete["folder"]

    # Remove the config.json file from the project folder
    config_file_path = os.path.join(project_folder, "config.json")
    if os.path.exists(config_file_path):
        os.remove(config_file_path)

    # Remove the project from the list
    projects.remove(project_to_delete)

    # Save the updated projects list
    save_projects(projects)

    return jsonify({"status": "success", "message": f"Project {project_id} and its config.json have been deleted."})
