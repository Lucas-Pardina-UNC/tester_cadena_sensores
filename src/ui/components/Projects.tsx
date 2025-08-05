import { useState, useEffect } from "react";
import CustomSelect from "./CustomSelect";
import NewProjectModal from "./NewProjectModal";
import OpenedProjects from "./OpenedProjects";
import DeleteProjectModal from "./DeleteProjectModal";
import { useProjectContext } from "./ProjectContext"; // Import context
import { useChainsContext } from "./ChainsContext";
import { useAlert } from "./CustomAlertContext";
import { useBackendRequest } from "../utils/backendRequest";

function Projects() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const { selectedProject, fetchOpenedProjects } = useProjectContext(); // Access selectedProject and fetchProjects
  const { nonOpenedProjects, fetchNonOpenedProjects } = useProjectContext();
  const { fetchChainsData } = useChainsContext();
  const { showAlert } = useAlert();

  const handleNewProject = () => {
    setIsModalOpen(true);
  };

  const handleDeleteSelectedProject = () => {
    if (selectedProject) {
      setIsDeleteModalOpen(true);
    } else {
      alert("No project selected.");
    }
  };

  const handleDeleteSuccess = async () => {
    await fetchOpenedProjects();
    await showAlert("Project deleted successfully!");
  };

  const { makeRequest } = useBackendRequest();

  const handleOpenProjectDialog = async () => {
    try {
      // Call the open-project API endpoint to trigger the file dialog
      const response = await makeRequest("/open-project", {
        method: "POST",
      });

      if (response.data.status === "success") {
        await showAlert("Project opened successfully!");
        fetchOpenedProjects(); // Refresh opened projects
        fetchNonOpenedProjects(); // Refresh non-opened projects
        fetchChainsData();
      } else {
        await showAlert(response.data.message || "Failed to open project.");
      }
    } catch (error) {
      console.error("Error opening project:", error);
      await showAlert("Failed to open project.");
    }
  };

  const handleOpenProject = async (projectId: string) => {
    try {
      await makeRequest(`/open-recent-project/${projectId}`, {
        method: "PATCH",
      });
      /*await axios.patch(
        `http://localhost:5000/open-recent-project/${projectId}`
      );*/
      await showAlert("Project opened successfully!");
      fetchNonOpenedProjects(); // Refresh non-opened projects
      fetchOpenedProjects();
      fetchChainsData();
    } catch (error) {
      console.error("Error opening project:", error);
      await showAlert("Failed to open the project.");
    }
  };

  const handleCloseSelectedProject = async () => {
    try {
      // Make API call to close the selected project
      await makeRequest("/close-selected-project", {
        method: "PATCH",
      });
      //await axios.patch(`http://localhost:5000/close-selected-project`);
      // Refresh projects list after closing
      fetchOpenedProjects();
      fetchNonOpenedProjects();
      fetchChainsData();
      await showAlert("Selected project closed successfully!");
    } catch (error) {
      console.error("Error closing selected project:", error);
      await showAlert("Failed to close the selected project.");
    }
  };

  useEffect(() => {
    fetchNonOpenedProjects();
  }, []);

  return (
    <>
      {/* <div className="projects-container"> */}
      <CustomSelect
        className="projects-dropdown"
        direction="down" // Change to "right" to see the right dropdown
        placeholder="Select an option"
        selected="Projects"
        options={[
          <div key="option1" onClick={handleNewProject}>
            New Project
          </div>,
          <div key="option2" onClick={handleOpenProjectDialog}>
            Open Project
          </div>,
          <div key="option3" onClick={handleCloseSelectedProject}>
            Close Selected Project
          </div>,
          <div key="option3" onClick={handleDeleteSelectedProject}>
            Delete Selected Project
          </div>,
          <CustomSelect
            direction="right" // Change to "right" to see the right dropdown
            placeholder="Select an option"
            selected="Open Recent Project"
            options={
              nonOpenedProjects.length > 0
                ? nonOpenedProjects.map((project) => (
                    <div
                      key={project.id}
                      onClick={() => handleOpenProject(project.id)}
                    >
                      {project.name}
                    </div>
                  ))
                : [<div key="no-projects">No Recent Projects Available</div>]
            }
            onClick={() => fetchNonOpenedProjects()}
          />,
        ]}
      />
      <OpenedProjects />
      <NewProjectModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
      <DeleteProjectModal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onSuccess={handleDeleteSuccess}
        projectId={selectedProject?.id || null}
      />
      {/* </div> */}
    </>
  );
}

export default Projects;
