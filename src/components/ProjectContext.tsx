import React, { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";

interface Project {
  id: string;
  name: string;
  folder: string; // Added folder property
  open: boolean;
  selected: boolean;
}

interface ProjectContextType {
  openedProjects: Project[];
  selectedProject: Project | null;
  setSelectedProject: (project: Project | null) => void;
  fetchProjects: () => Promise<void>; // Exposed fetch function
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

export const ProjectProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [openedProjects, setOpenedProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  const fetchProjects = async () => {
    try {
      const response = await axios.get(
        "http://localhost:5000/api/projects/opened"
      );
      const openedProjects: Project[] = response.data.opened_projects; // Explicitly typed array
      setOpenedProjects(openedProjects);

      // Find the currently selected project
      const selected = openedProjects.find(
        (project: Project) => project.selected
      );
      setSelectedProject(selected || null);
    } catch (error) {
      console.error("Error fetching projects:", error);
    }
  };

  useEffect(() => {
    fetchProjects(); // Initial fetch on component mount
  }, []);

  return (
    <ProjectContext.Provider
      value={{
        openedProjects,
        selectedProject,
        setSelectedProject,
        fetchProjects,
      }}
    >
      {children}
    </ProjectContext.Provider>
  );
};

export const useProjectContext = () => {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error("useProjectContext must be used within a ProjectProvider");
  }
  return context;
};
