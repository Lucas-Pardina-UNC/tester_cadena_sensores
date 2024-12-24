import { useState } from "react";
/* import axios from "axios"; */
import CustomSelect from "./CustomSelect";
//import SelectedProject from "./SelectedProject";
import NewProjectModal from "./NewProjectModal";
import OpenedProjects from "./OpenedProjects";

function Projects() {
  const handleSelect = (message: string) => {
    console.log(message);
  };

  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleNewProject = () => {
    setIsModalOpen(true);
  };

  return (
    <>
      <CustomSelect
        direction="down" // Change to "right" to see the right dropdown
        placeholder="Select an option"
        selected="Projects"
        options={[
          <div key="option1" onClick={handleNewProject}>
            New Project
          </div>,
          <div key="option2" onClick={() => handleSelect("Open Project")}>
            Open Project
          </div>,
          <div key="option3" onClick={() => handleSelect("Close Project")}>
            Close Project
          </div>,
          <div key="option3" onClick={() => handleSelect("Close Project")}>
            Delete Selected Project
          </div>,
          <CustomSelect
            direction="right" // Change to "right" to see the right dropdown
            placeholder="Select an option"
            selected="Open Recent Project"
            options={[
              <div key="A" onClick={() => handleSelect("Project A")}>
                Project A
              </div>,
              <div key="B" onClick={() => handleSelect("Project B")}>
                Project B
              </div>,
              <div key="C" onClick={() => handleSelect("Project C")}>
                Project C
              </div>,
            ]}
          />,
        ]}
      />
      <OpenedProjects />
      <NewProjectModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </>
  );
}

export default Projects;
