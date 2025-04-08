import React, { useState } from "react";
import axios from "axios";

interface TemperatureTestProps {
  isOpen: boolean;
  onClose: () => void;
  projectFolder: string; // Receiving project folder
  selectedChainId: string; // Receiving selected chain ID
}

const TemperatureTest: React.FC<TemperatureTestProps> = ({
  isOpen,
  onClose,
  projectFolder,
  selectedChainId,
}) => {
  if (!isOpen) return null; // Don't render the modal if it's not open

  const [timestamps, setTimestamps] = useState<string[]>(Array(17).fill(" - "));
  const [temperatures, setTemperatures] = useState<string[]>(
    Array(17).fill(" - ")
  );
  const [adcValues, setAdcValues] = useState<string[]>(Array(17).fill(" - "));
  const [showAdcValues, setShowAdcValues] = useState<boolean>(false); // State to toggle ADC visibility

  const handleRunTest = async () => {
    try {
      const response = await axios.post("http://localhost:5000/single_test", {
        file_path: projectFolder,
        chain_id: selectedChainId,
      });

      console.log("Response:", response.data);

      if (response.data.status === "success") {
        const logData = response.data.log_data;

        // Extract timestamps, temperatures, and ADC values from logData
        const newTimestamps = logData.map(
          (entry: any) => entry[0][1] // Extract the timestamp
        );
        const newTemperatures = logData.map(
          (entry: any) => entry[0][3].toString() // Extract the temperature and convert to string
        );
        const newAdcValues = logData.map(
          (entry: any) => entry[0][2].toString() // Extract the ADC value and convert to string
        );

        setTimestamps(newTimestamps);
        setTemperatures(newTemperatures);
        setAdcValues(newAdcValues);
      }
    } catch (error) {
      console.error("Error running test:", error);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>Temperature Test</h2>
        <p>Sensor Chain Serial Number: 0000</p>
        <div className="adc-checkbox">
          <label>
            <input
              type="checkbox"
              onChange={(e) => setShowAdcValues(e.target.checked)} // Toggle ADC visibility
            />
            Show ADC values
          </label>
        </div>
        <div
          className={
            showAdcValues ? "fields-description-adc" : "fields-description"
          }
        >
          <div className="slave-id-description">
            <label>Slave ID</label>
          </div>
          <label>Timestamp</label>
          <div className="temperature-description">
            <label>Temperature</label>
          </div>
          {showAdcValues && ( // Conditionally render the ADC Value label
            <div className="adc-description">
              <label>ADC Value</label>
            </div>
          )}
        </div>
        <div
          className={
            showAdcValues
              ? "temperature-test-results-adc"
              : "temperature-test-results"
          }
        >
          <div className="slave-id-fields">
            {Array.from({ length: 17 }, (_, index) => (
              <div key={index} className="slave-id-field">
                <label>Slave {index + 1} :</label>
              </div>
            ))}
          </div>
          <div className="timestamp-fields">
            {timestamps.map((timestamp, index) => (
              <div key={index} className="timestamp-field">
                <input
                  type="text"
                  value={timestamp}
                  readOnly
                  className="current-time-input"
                />
              </div>
            ))}
          </div>
          <div className="temperature-fields">
            {temperatures.map((temperature, index) => (
              <div key={index} className="temperature-field">
                <input
                  type="text"
                  value={temperature}
                  readOnly
                  className="temperature-input"
                />
              </div>
            ))}
          </div>
          {showAdcValues && ( // Conditionally render ADC fields
            <div className="adc-fields">
              {adcValues.map((adcValue, index) => (
                <div key={index} className="adc-field">
                  <input
                    type="text"
                    value={adcValue}
                    readOnly
                    className="adc-input"
                  />
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="modal-buttons">
          <button onClick={handleRunTest}>Run Test</button>
          <button onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
};

export default TemperatureTest;
