import React, { useState } from "react";
import Projects from "./Projects"; // Adjust the path if necessary
import SelectedProject from "./SelectedProject"; // Adjust the path if necessary
import ChainsList from "./ChainsList"; // Adjust the path if necessary
import AddChainModal from "./AddChainModal";
import AutoTestModal from "./AutoTestModal"; // Import the AutoTestModal

const MainPanel: React.FC = () => {
  const [isAddChainModalOpen, setIsAddChainModalOpen] = useState(false);
  const [isAutoTestModalOpen, setIsAutoTestModalOpen] = useState(false);

  return (
    <>
      <div className="main-panel">
        {/* Left panel with Projects */}
        <div className="main-panel__left">
          <Projects />
        </div>

        {/* Right panel with SelectedProject and ChainsList */}
        <div className="main-panel__right">
          <SelectedProject />
          <ChainsList />
          <button onClick={() => setIsAddChainModalOpen(true)}>
            Add Chain
          </button>
          <button onClick={() => setIsAutoTestModalOpen(true)}>Run Test</button>
        </div>
      </div>

      <AddChainModal
        isOpen={isAddChainModalOpen}
        onClose={() => setIsAddChainModalOpen(false)}
      />

      <AutoTestModal
        isOpen={isAutoTestModalOpen}
        onClose={() => setIsAutoTestModalOpen(false)}
      />
    </>
  );
};

export default MainPanel;
