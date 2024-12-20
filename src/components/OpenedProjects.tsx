import React, { useEffect, useState } from "react";
import axios from "axios";
import { useProjectContext } from "./ProjectContext";
import { useChainsContext } from "./ChainsContext";

const OpenedProjects: React.FC = () => {
  const { openedProjects, selectedProject, setSelectedProject } =
    useProjectContext();
  const { setChainsData } = useChainsContext();

  const handleSelectProject = async (id: string) => {
    try {
      // Update the selected project in the backend
      await axios.patch(`http://localhost:5000/select-project/${id}`);

      // Update the selected project in the context
      const updatedProjects = openedProjects.map((project) =>
        project.id === id
          ? { ...project, selected: true }
          : { ...project, selected: false }
      );

      const newSelectedProject =
        updatedProjects.find((project) => project.id === id) ?? null;

      setSelectedProject(newSelectedProject);
      // Fetch chains for the new selected project
      if (newSelectedProject?.folder) {
        // Fetch chains for the new selected project if its folder exists
        fetchChainsData(newSelectedProject.folder);
      }
    } catch (error) {
      console.error("Error selecting project:", error);
    }
  };

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
    <div>
      <h2>Opened Projects</h2>
      <ul>
        {openedProjects.map((project) => (
          <li
            key={project.id}
            onClick={() => handleSelectProject(project.id)}
            style={{
              fontWeight:
                project.id === selectedProject?.id ? "bold" : "normal",
              cursor: "pointer",
            }}
          >
            {project.name}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default OpenedProjects;
