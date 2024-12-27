import React from "react";
import { useProjectContext } from "./ProjectContext";

const SelectedProject: React.FC = () => {
  const { selectedProject } = useProjectContext();

  if (!selectedProject) {
    return <div>No project is selected.</div>;
  }

  return (
    <div className="selected-project">
      <p>
        <strong>Selected Project: </strong>
        {selectedProject.name}
      </p>
      <p>
        <strong>Folder Path: </strong>
        {selectedProject.folder}
      </p>
    </div>
  );
};

export default SelectedProject;
