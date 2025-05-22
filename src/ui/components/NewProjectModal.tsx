import React, { useState } from "react";
// import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import { useProjectContext } from "./ProjectContext";
import { useChainsContext } from "./ChainsContext";
import { useAlert } from "./CustomAlertContext";

interface NewProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const NewProjectModal: React.FC<NewProjectModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [projectName, setProjectName] = useState("");
  const [folderPath, setFolderPath] = useState("");
  const [validationMessage, setValidationMessage] = useState("");

  const { setSelectedProject } = useProjectContext(); // Destructure from context
  const { fetchOpenedProjects } = useProjectContext();
  const { fetchChainsData } = useChainsContext();
  const { showAlert } = useAlert();

  const resetFields = () => {
    setProjectName("");
    setFolderPath("");
  };

  const selectFolder = async () => {
    try {
      const response = await axios.get("http://localhost:5000/select-folder");
      if (response.data.status === "success") {
        setFolderPath(response.data.folder);
        setValidationMessage("");
      } else {
        alert("Failed to select a folder.");
      }
    } catch (error) {
      console.error("Error selecting folder:", error);
      alert("Failed to communicate with the backend.");
    }
  };

  const handleCreate = async () => {
    if (!projectName.trim()) {
      setValidationMessage("Project name cannot be empty.");
      return;
    }
    if (!folderPath.trim()) {
      setValidationMessage("Please select a project folder.");
      return;
    }

    try {
      const response = await axios.post(
        "http://localhost:5000/create-project",
        { name: projectName, folder: folderPath }
      );

      if (response.data.status === "success") {
        const message = `Project "${projectName}" created successfully in "${folderPath}`;
        await showAlert(message);
        setSelectedProject({
          id: response.data.project.id,
          name: projectName,
          folder: folderPath,
          open: true,
          selected: true,
        });
        await fetchOpenedProjects();
        fetchChainsData();
        resetFields(); // Clear fields only after successful creation
        onClose(); // Close the modal
      } else {
        setValidationMessage(response.data.message); // Show error
      }
    } catch (error) {
      console.error("Error creating project:", error);
      setValidationMessage("Error creating project. Please try again.");
    }
  };

  if (!isOpen) return null; // If close then don't render anything

  return (
    <div className="new-project-modal-overlay">
      <div className="new-project-modal">
        <h2>Create New Project</h2>
        <div className="new-project-data">
          <div className="project-name-input">
            <div className="project-data-label">
              <label>Project Name</label>
            </div>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="Enter project name"
            />
          </div>
          <div className="project-folder-input">
            <div className="project-data-label">
              <label>Project Folder</label>
            </div>
            <input
              type="text"
              value={folderPath}
              readOnly
              placeholder="Select a folder"
            />
            <button onClick={selectFolder}>Select Folder</button>
          </div>
        </div>
        {validationMessage && (
          <p className="validation-message">{validationMessage}</p>
        )}
        <div className="new-project-modal-buttons">
          <button
            onClick={() => {
              onClose();
              resetFields(); // Clear fields when closing without creating
            }}
          >
            Cancel
          </button>
          <button
            onClick={() => {
              handleCreate();
            }}
          >
            Create Project
          </button>
        </div>
      </div>
    </div>
  );
};

export default NewProjectModal;
