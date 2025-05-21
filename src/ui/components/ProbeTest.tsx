import React, { useState } from "react";

interface ProbeTestProps {
  isOpen: boolean;
  onClose: () => void;
}

const ProbeTest: React.FC<ProbeTestProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null; // Don't render the modal if it's not open

  // State variables for Probe Test data
  // @ts-ignore
  const [phycocyaninLevel, setPhycocyaninLevel] = useState(" - ");
  // @ts-ignore
  const [chlorophyllLevel, setChlorophyllLevel] = useState(" - ");
  // @ts-ignore
  const [turbidityLevel, setTurbidityLevel] = useState(" - ");
  // @ts-ignore
  const [ph, setPH] = useState(" - ");
  // @ts-ignore
  const [phORP, setPHORP] = useState(" - ");
  // @ts-ignore
  const [odTemp, setODTemp] = useState(" - ");
  // @ts-ignore
  const [od, setOD] = useState(" - ");
  // @ts-ignore
  const [odMgl, setODMgl] = useState(" - ");
  // @ts-ignore
  const [odPPM, setODPPM] = useState(" - ");

  // Placeholder function for "Run Test" button
  const handleRunTest = () => {
    // Logic to fetch data from the endpoint and update state will go here
    console.log("Run Test button pressed");
  };

  // Placeholder function for "Test Mechanical Brush" button
  const handleTestMechanicalBrush = () => {
    // Logic to test the mechanical brush will go here
    console.log("Test Mechanical Brush button pressed");
  };

  return (
    <div className="probe-modal-overlay">
      <div className="probe-modal">
        <h2>Probe Test</h2>
        <div className="probe-test-fields">
          <div className="probe-field">
            <label>Phycocyanin Level:</label>
            <input type="text" value={phycocyaninLevel} readOnly />
          </div>
          <div className="probe-field">
            <label>Chlorophyll Level:</label>
            <input type="text" value={chlorophyllLevel} readOnly />
          </div>
          <div className="probe-field">
            <label>Turbidity Level:</label>
            <input type="text" value={turbidityLevel} readOnly />
          </div>
          <div className="probe-field">
            <label>PH:</label>
            <input type="text" value={ph} readOnly />
          </div>
          <div className="probe-field">
            <label>PH ORP:</label>
            <input type="text" value={phORP} readOnly />
          </div>
          <div className="probe-field">
            <label>OD Temp:</label>
            <input type="text" value={odTemp} readOnly />
          </div>
          <div className="probe-field">
            <label>OD:</label>
            <input type="text" value={od} readOnly />
          </div>
          <div className="probe-field">
            <label>OD Mgl:</label>
            <input type="text" value={odMgl} readOnly />
          </div>
          <div className="probe-field">
            <label>OD PPM:</label>
            <input type="text" value={odPPM} readOnly />
          </div>
        </div>
        <div className="probe-test-buttons">
          <button onClick={handleRunTest}>Run Test</button>
          <button onClick={handleTestMechanicalBrush}>
            Test Mechanical Brush
          </button>
          <button onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
};

export default ProbeTest;
