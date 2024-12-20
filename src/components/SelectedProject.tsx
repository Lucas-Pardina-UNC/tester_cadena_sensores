import React from "react";
import { useProjectContext } from "./ProjectContext";

const SelectedProject: React.FC = () => {
  const { selectedProject } = useProjectContext();

  if (!selectedProject) {
    return <div>No project is selected.</div>;
  }

  return (
    <div>
      <p>
        <strong>Selected Project:</strong>
        <strong></strong> {selectedProject.name}
        {/* <strong> Folder Path:</strong> {selectedProject.folder} */}
      </p>
    </div>
  );
};

export default SelectedProject;
