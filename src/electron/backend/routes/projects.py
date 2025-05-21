from flask import Blueprint, jsonify, request
from multiprocessing import Process, Queue
from tkinter import Tk, filedialog
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
    project_id = str(uuid.uuid4())
    new_project = {
        "id": project_id,  # Generate a unique ID
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
        "id": project_id,  # Include the project ID as the first field
        "name": project_name,
        "project_folder": folder_path,
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

def open_file_dialog(queue):
    """Function to select a file using tkinter"""
    root = Tk()
    root.withdraw()  # Hide the main tkinter window
    root.attributes('-topmost', True)  # Bring the file dialog to the front
    file_path = filedialog.askopenfilename(
        title="Select config.json file",
        filetypes=[("JSON Files", "*.json")],
    )
    queue.put(file_path)

@projects_bp.route('/open-project', methods=['POST'])
def open_project():
    """Open an existing project by selecting its config.json file"""
    queue = Queue()
    process = Process(target=open_file_dialog, args=(queue,))
    process.start()
    process.join()
    file_path = queue.get()

    if not file_path or not os.path.isfile(file_path):
        return jsonify({"status": "error", "message": "No file selected or file does not exist."}), 400

    # Ensure the selected file is named config.json
    if not file_path.endswith("config.json"):
        return jsonify({"status": "error", "message": "Invalid file selected. Please select a config.json file."}), 400

    # Load the contents of the config.json file
    try:
        with open(file_path, "r") as config_file:
            config_data = json.load(config_file)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to read the config.json file: {e}"}), 400

    # Extract the project ID and name from the config.json file
    project_id = config_data.get("id")
    project_name = config_data.get("name")
    if not project_id or not project_name:
        return jsonify({"status": "error", "message": "Invalid config.json file. Missing 'id' or 'name'."}), 400

    # Load existing projects (implement your `load_projects` function)
    projects = load_projects()

    # Check if the project is already in the list
    if any(project["id"] == project_id for project in projects):
        return jsonify({"status": "error", "message": "This project is already added."}), 400

    # Add the project to the projects list
    new_project = {
        "id": project_id,
        "name": project_name,
        "folder": os.path.dirname(file_path),
        "open": True,
        "selected": True
    }

    # Set all other projects' selected field to False
    for project in projects:
        project["selected"] = False

    projects.append(new_project)

    # Save the updated projects list (implement your `save_projects` function)
    save_projects(projects)

    return jsonify({"status": "success", "message": "Project opened successfully.", "project": new_project})

#@projects_bp.route('/open-selected-project/<project_id>', methods=['PATCH'])
@projects_bp.route('/open-recent-project/<project_id>', methods=['PATCH'])
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
    """Delete a project by its ID based on the received flags (deleteFolder, deleteConfigFile)."""
    # Parse JSON data from the request
    data = request.get_json()
    delete_folder = data.get("deleteFolder", False)
    delete_config_file = data.get("deleteConfigFile", False)

    # Load existing projects
    projects = load_projects()

    # Find the project to delete
    project_to_delete = next((project for project in projects if project["id"] == project_id), None)

    if not project_to_delete:
        return jsonify({"status": "error", "message": "Project not found."}), 404

    # Get the folder path of the project
    project_folder = project_to_delete["folder"]
    config_file_path = os.path.join(project_folder, "config.json")

    # Delete config.json if requested
    if delete_config_file and os.path.exists(config_file_path):
        try:
            os.remove(config_file_path)
        except Exception as e:
            return jsonify({"status": "error", "message": f"Failed to delete config.json: {str(e)}"}), 500

    # Delete the project folder if requested
    if delete_folder and os.path.exists(project_folder):
        try:
            # Remove all files in the folder
            for filename in os.listdir(project_folder):
                file_path = os.path.join(project_folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    # Recursively remove subdirectories if needed
                    import shutil
                    shutil.rmtree(file_path)
            os.rmdir(project_folder)  # Removes now-empty folder
        except OSError as e:
            return jsonify({"status": "error", "message": f"Failed to delete folder: {str(e)}"}), 500

    # Remove the project from the list
    projects.remove(project_to_delete)

    # Save the updated projects list
    save_projects(projects)

    return jsonify({
        "status": "success",
        "message": f"Project {project_id} deleted.",
        "folderDeleted": delete_folder,
        "configFileDeleted": delete_config_file
    })