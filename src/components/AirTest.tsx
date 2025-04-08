import React, { useState } from "react";

interface AirTestProps {
  isOpen: boolean;
  onClose: () => void;
}

const AirTest: React.FC<AirTestProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null; // Don't render the modal if it's not open

  // State variables for Humidity, Pressure, and Temperature
  const [humidity, setHumidity] = useState(" - ");
  const [pressure, setPressure] = useState(" - ");
  const [temperature, setTemperature] = useState(" - ");

  // Placeholder function for "Run Test" button
  const handleRunTest = () => {
    // Logic to fetch data from the endpoint and update state will go here
    console.log("Run Test button pressed");
  };

  // Placeholder function for "Export Calibration Coefficients" button
  const handleExportCoefficients = () => {
    // Logic to export calibration coefficients will go here
    console.log("Export Calibration Coefficients button pressed");
  };

  return (
    <div className="air-modal-overlay">
      <div className="air-modal">
        <h2>Air Test</h2>
        <button onClick={handleExportCoefficients}>
          Export Calibration Coefficients
        </button>
        <div className="air-test-fields">
          <div className="air-field">
            <label>Humidity:</label>
            <input type="text" value={humidity} readOnly />
          </div>
          <div className="air-field">
            <label>Pressure:</label>
            <input type="text" value={pressure} readOnly />
          </div>
          <div className="air-field">
            <label>Temperature:</label>
            <input type="text" value={temperature} readOnly />
          </div>
        </div>
        <div className="air-test-buttons">
          <button onClick={onClose}>Close</button>
          <button onClick={handleRunTest}>Run Test</button>
        </div>
      </div>
    </div>
  );
};

export default AirTest;
