import React, { useState } from "react";
import { useBackendRequest } from "../utils/backendRequest";

interface WindTestProps {
  isOpen: boolean;
  onClose: () => void;
  projectFolder: string; // Receiving project folder
  selectedChainId: string; // Receiving selected chain ID
}

const WindTest: React.FC<WindTestProps> = ({
  isOpen,
  onClose,
  projectFolder,
  selectedChainId,
}) => {
  if (!isOpen) return null; // Don't render the modal if it's not open

  // State variables for Wind Speed and Wind Direction
  // @ts-ignore
  const [windSpeed, setWindSpeed] = useState(" - ");
  // @ts-ignore
  const [windDirection, setWindDirection] = useState(" - ");

  const { makeRequest } = useBackendRequest();

  const handleRunTest = async () => {
    try {
      const response = await makeRequest("/single_test", {
        method: "POST",
        data: {
          file_path: projectFolder,
          chain_id: selectedChainId,
        },
      });
      console.log("Response:", response.data);

      if (response.data.status === "success") {
        const logData = response.data.log_data;

        // Extract direct and net radiation values from the log
        const windSpeedEntry = logData.find(
          (entry: any) => entry[3] === "wind_speed"
        );
        const windDirectionEntry = logData.find(
          (entry: any) => entry[3] === "wind_direction"
        );

        const windSpeedValue = windSpeedEntry ? windSpeedEntry[5] : null;
        const windDirectionValue = windDirectionEntry
          ? windDirectionEntry[5]
          : null;

        // Update state with the received values
        setWindSpeed(windSpeedValue.toFixed(2));
        setWindDirection(windDirectionValue.toFixed(2));

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
