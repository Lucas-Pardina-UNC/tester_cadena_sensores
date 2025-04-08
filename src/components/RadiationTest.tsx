import React, { useState } from "react";

interface RadiationTestProps {
  isOpen: boolean;
  onClose: () => void;
}

const RadiationTest: React.FC<RadiationTestProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null; // Don't render the modal if it's not open

  // State variables for Direct Radiation and Net Radiation
  const [directRadiation, setDirectRadiation] = useState(" - ");
  const [netRadiation, setNetRadiation] = useState(" - ");

  // Placeholder function for "Run Test" button
  const handleRunTest = () => {
    // Logic to fetch data from the endpoint and update state will go here
    console.log("Run Test button pressed");
  };

  return (
    <div className="wind-or-radiation-modal-overlay">
      <div className="wind-or-radiation-modal">
        <h2>Radiation Test</h2>
        <div className="wind-or-radiation-test-fields">
          <div className="wind-or-radiation-field">
            <label>Direct Radiation:</label>
            <input type="text" value={directRadiation} readOnly />
          </div>
          <div className="wind-or-radiation-field">
            <label>Net Radiation:</label>
            <input type="text" value={netRadiation} readOnly />
          </div>
        </div>
        <div className="wind-or-radiation-test-buttons">
          <button onClick={handleRunTest}>Run Test</button>
          <button onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
};

export default RadiationTest;
