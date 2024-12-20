from flask import Blueprint, jsonify
import os
import tkinter as tk
from tkinter import filedialog
from multiprocessing import Process, Queue

folders_bp = Blueprint("folders", __name__)

def select_empty_folder(queue):
    """Function to select an empty folder using tkinter"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', 1)  # Set the window to always stay on top
    folder_path = filedialog.askdirectory(title="Select an empty folder")
    if folder_path and not os.listdir(folder_path):  # Check if folder is empty
        queue.put(folder_path)  # Send the result back to the main process
    else:
        queue.put(None)

def run_file_dialog():
    """Run the file dialog in a separate process and return the result"""
    queue = Queue()  # Create a Queue to get data back from the process
    process = Process(target=select_empty_folder, args=(queue,))
    process.start()
    process.join()  # Wait for the process to finish
    folder_path = queue.get()  # Get the result from the queue
    return folder_path

@folders_bp.route('/select-folder', methods=['GET'])
def select_folder():
    """Flask route to trigger folder selection"""
    folder_path = run_file_dialog()
    if folder_path:
        return jsonify({"status": "success", "folder": folder_path})
    else:
        return jsonify({"status": "error", "message": "Failed to select an empty folder."})