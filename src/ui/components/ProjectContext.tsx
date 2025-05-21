import React, { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";

interface Project {
  id: string;
  name: string;
  folder: string;
  open: boolean;
  selected: boolean;
}

interface ProjectContextType {
  openedProjects: Project[];
  nonOpenedProjects: Project[];
  selectedProject: Project | null;
  setSelectedProject: (project: Project | null) => void;
  fetchOpenedProjects: () => Promise<void>;
  fetchNonOpenedProjects: () => Promise<void>;
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

export const ProjectProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [openedProjects, setOpenedProjects] = useState<Project[]>([]);
  const [nonOpenedProjects, setNonOpenedProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  const fetchOpenedProjects = async () => {
    try {
      const response = await axios.get(
        "http://localhost:5000/api/projects/opened"
      );
      const openedProjects: Project[] = response.data.opened_projects;
      setOpenedProjects(openedProjects);

      // Find the currently selected project
      const selected = openedProjects.find(
        (project: Project) => project.selected
      );
      setSelectedProject(selected || null);
    } catch (error) {
      console.error("Error fetching projects: Hola", error);
    }
  };

  const fetchNonOpenedProjects = async () => {
    try {
      const response = await axios.get(
        "http://localhost:5000/api/projects/non-opened"
      );
      const nonOpenedProjects: Project[] = response.data.non_opened_projects; // Explicitly typed array
      setNonOpenedProjects(nonOpenedProjects);
      //setOpenedProjects(openedProjects);
    } catch (error) {
      console.error("Error fetching projects:", error);
    }
  };

  useEffect(() => {
    fetchOpenedProjects(); // Initial fetch on component mount
    //fetchNonOpenedProjects();
  }, []);

  return (
    <ProjectContext.Provider
      value={{
        openedProjects,
        nonOpenedProjects,
        selectedProject,
        setSelectedProject,
        fetchOpenedProjects,
        fetchNonOpenedProjects,
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
