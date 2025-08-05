import React, { useState } from "react";
import { useBackendRequest } from "../utils/backendRequest";
//import axios from "axios";

interface RadiationTestProps {
  isOpen: boolean;
  onClose: () => void;
  projectFolder: string; // Receiving project folder
  selectedChainId: string; // Receiving selected chain ID
}

const RadiationTest: React.FC<RadiationTestProps> = ({
  isOpen,
  onClose,
  projectFolder,
  selectedChainId,
}) => {
  if (!isOpen) return null; // Don't render the modal if it's not open

  // State variables for Direct Radiation and Net Radiation
  const [directRadiation, setDirectRadiation] = useState(" - ");
  const [netRadiation, setNetRadiation] = useState(" - ");

  // State variables for Offset and Gain
  const [offset, setOffset] = useState("");
  const [gain, setGain] = useState("");

  const { makeRequest } = useBackendRequest();

  // Function to handle the "Run Test" button
  const handleRunTest = async () => {
    try {
      console.log("Run Test button pressed");
      console.log(`Offset: ${offset}, Gain: ${gain}`);

      // Call the endpoint
      const response = await makeRequest("/single_test", {
        method: "POST",
        data: {
          file_path: projectFolder,
          chain_id: selectedChainId,
          offset: parseFloat(offset), // Convert offset to a number
          gain: parseFloat(gain), // Convert gain to a number
        },
      });
      /*const response = await axios.post("http://localhost:5000/single_test", {
        file_path: projectFolder,
        chain_id: selectedChainId,
        offset: parseFloat(offset), // Convert offset to a number
        gain: parseFloat(gain), // Convert gain to a number
      });*/

      if (response.data.status === "success") {
        const logData = response.data.log_data;

        // Extract direct and net radiation values from the log
        const directRadiationEntry = logData.find(
          (entry: any) => entry[3] === "direct_radiation"
        );
        const netRadiationEntry = logData.find(
          (entry: any) => entry[3] === "net_radiation"
        );

        const directRadiationValue = directRadiationEntry
          ? directRadiationEntry[5]
          : null;
        const netRadiationValue = netRadiationEntry
          ? netRadiationEntry[5]
          : null;

        // Update state with the received values
        setDirectRadiation(directRadiationValue.toFixed(2));
        setNetRadiation(netRadiationValue.toFixed(2));

        console.log("Test completed successfully:", logData);
      } else {
        console.error("Test failed:", response.data.error);
      }
    } catch (error) {
      console.error("Error running test:", error);
    }
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
          <div className="wind-or-radiation-field">
            <label>Offset:</label>
            <input
              type="number"
              value={offset}
              onChange={(e) => setOffset(e.target.value)}
            />
          </div>
          <div className="wind-or-radiation-field">
            <label>Gain:</label>
            <input
              type="number"
              value={gain}
              onChange={(e) => setGain(e.target.value)}
            />
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
