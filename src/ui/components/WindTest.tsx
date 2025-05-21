import React, { useState } from "react";

interface WindTestProps {
  isOpen: boolean;
  onClose: () => void;
}

const WindTest: React.FC<WindTestProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null; // Don't render the modal if it's not open

  // State variables for Wind Speed and Wind Direction
  // @ts-ignore
  const [windSpeed, setWindSpeed] = useState(" - ");
  // @ts-ignore
  const [windDirection, setWindDirection] = useState(" - ");

  // Placeholder function for "Run Test" button
  const handleRunTest = () => {
    // Logic to fetch data from the endpoint and update state will go here
    console.log("Run Test button pressed");
  };

  return (
    <div className="wind-or-radiation-modal-overlay">
      <div className="wind-or-radiation-modal">
        <h2>Wind Test</h2>
        <div className="wind-or-radiation--test-fields">
          <div className="wind-or-radiation-field">
            <label>Wind Speed:</label>
            <input type="text" value={windSpeed} readOnly />
          </div>
          <div className="wind-or-radiation-field">
            <label>Wind Direction:</label>
            <input type="text" value={windDirection} readOnly />
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

export default WindTest;
