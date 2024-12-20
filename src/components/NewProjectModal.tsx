import React, { useState } from "react";
// import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import { useProjectContext } from "./ProjectContext";
import { useChainsContext } from "./ChainsContext";

interface NewProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  //onCreate: (projectName: string, folderPath: string) => void;
}

const NewProjectModal: React.FC<NewProjectModalProps> = ({
  isOpen,
  onClose,
  //onCreate,
}) => {
  const [projectName, setProjectName] = useState("");
  const [folderPath, setFolderPath] = useState("");
  const [validationMessage, setValidationMessage] = useState("");

  const { setSelectedProject } = useProjectContext(); // Destructure from context
  const { fetchProjects } = useProjectContext();
  const { setChainsData } = useChainsContext();

  const resetFields = () => {
    setProjectName("");
    setFolderPath("");
  };

  /* const handleProjectNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setProjectName(e.target.value);
  }; */

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
        /*alert(
          `Project "${projectName}" created successfully in "${folderPath}"!` // Este alert hace perder el focus.
        );*/
        //window.ipcRenderer.focusWindow(); // Esto en teoría lo soluciona, pero hay que lograr que lo tome
        //this.inputReference.current.focus();
        //onCreate(projectName, folderPath); // Notify the parent
        setSelectedProject({
          id: response.data.project.id,
          name: projectName,
          folder: folderPath,
          open: true,
          selected: true,
        });
        await fetchProjects();
        fetchChainsData(folderPath);
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

  const fetchChainsData = async (projectFolder: string) => {
    try {
      const response = await axios.get("http://localhost:5000/get-chains");

      if (response.data.status === "success") {
        const chains = response.data.chains;
        setChainsData(chains); // Update the ChainsContext with the chains data
      } else {
        console.error("Error fetching chains:", response.data.message);
      }
    } catch (error) {
      console.error("Error fetching chains:", error);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>Create New Project</h2>
        <div>
          <label>Project Name</label>
          <input
            //ref={inputReference}
            type="text"
            //autoFocus
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            //onChange={handleProjectNameChange}
            placeholder="Enter project name"
          />
        </div>
        <div>
          <label>Project Folder</label>
          <input
            type="text"
            value={folderPath}
            readOnly
            placeholder="Select a folder"
          />
          <button onClick={selectFolder}>Select Folder</button>
        </div>
        {validationMessage && (
          <p className="validation-message">{validationMessage}</p>
        )}
        <div className="modal-buttons">
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
