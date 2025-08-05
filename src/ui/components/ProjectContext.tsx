import React, { createContext, useContext, useState, useEffect } from "react";
import { useBackendRequest } from "../utils/backendRequest";

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

  const { makeRequest, loading, error } = useBackendRequest();

  const fetchOpenedProjects = async () => {
    try {
      const response = await makeRequest("/api/projects/opened", {
        method: "GET",
      });
      const openedProjects: Project[] = response.data.opened_projects;
      setOpenedProjects(openedProjects);

      // Find the currently selected project
      const selected = openedProjects.find(
        (project: Project) => project.selected
      );
      setSelectedProject(selected || null);
    } catch (error) {
      console.error("Error fetching projects: ", error);
    }
  };

  const fetchNonOpenedProjects = async () => {
    try {
      if (!loading && !error) {
        const response = await makeRequest("/api/projects/non-opened", {
          method: "GET",
        });
        const nonOpenedProjects: Project[] = response.data.non_opened_projects; // Explicitly typed array
        setNonOpenedProjects(nonOpenedProjects);
      }
    } catch (error) {
      console.error("Error fetching projects:", error);
    }
  };

  useEffect(() => {
    if (!loading && !error) {
      fetchOpenedProjects();
      fetchNonOpenedProjects();
    }
  }, [loading, error]); // 👈 React will retry when backend becomes ready

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
