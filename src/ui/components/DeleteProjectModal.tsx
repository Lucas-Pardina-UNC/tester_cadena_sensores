import React, { useState } from "react";
import { useBackendRequest } from "../utils/backendRequest";

interface DeleteProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  projectId: string | null;
}

const DeleteProjectModal: React.FC<DeleteProjectModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  projectId,
}) => {
  const [deleteFolder, setDeleteFolder] = useState(false);
  const [deleteConfigFile, setDeleteConfigFile] = useState(false);
  const { makeRequest } = useBackendRequest();

  const handleAccept = async () => {
    if (!projectId) return;

    try {
      await makeRequest(`/delete-project/${projectId}`, {
        method: "DELETE",
        data: { deleteFolder, deleteConfigFile },
      });
      onSuccess();
      onClose();
    } catch (error) {
      console.error("Error deleting project:", error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>Delete Project</h2>
        <p>Are you sure you want to delete this project?</p>
        <div>
          <label>
            <input
              type="checkbox"
              checked={deleteFolder}
              onChange={(e) => setDeleteFolder(e.target.checked)}
            />
            Delete Project Folder
          </label>
        </div>
        <div>
          <label>
            <input
              type="checkbox"
              checked={deleteConfigFile}
              onChange={(e) => setDeleteConfigFile(e.target.checked)}
            />
            Delete Project Config File
          </label>
        </div>
        <div className="modal-actions">
          <button onClick={onClose}>Cancel</button>
          <button onClick={handleAccept}>Delete</button>
        </div>
      </div>
    </div>
  );
};

export default DeleteProjectModal;
