import React, { useState } from "react";
import axios from "axios";

interface Slave {
  slave_id: number;
  sensor_id: string;
  sensor_type: string;
}

interface SlaveDetectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSlavesDetected: (slaves: Slave[]) => void;
  chain: {
    chain_port: string;
    chain_protocol: string;
  };
}

const SlaveDetectionModal: React.FC<SlaveDetectionModalProps> = ({
  isOpen,
  onClose,
  onSlavesDetected,
  chain,
}) => {
  const [detectionMode, setDetectionMode] = useState("range");
  const [firstSlave, setFirstSlave] = useState<number>(1);
  const [lastSlave, setLastSlave] = useState<number>(1);
  const [numberOfSlaves, setNumberOfSlaves] = useState<number>(1);
  const [specificSlave, setSpecificSlave] = useState<number>(1);
  const [consoleMessages, setConsoleMessages] = useState<string[]>([]);
  const [responsiveSlaves, setResponsiveSlaves] = useState<Slave[]>([]);
  const [isReadyEnabled, setIsReadyEnabled] = useState<boolean>(false);

  const handleModeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setDetectionMode(e.target.value);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number(e.target.value);
    if (e.target.name === "firstSlave") setFirstSlave(value);
    if (e.target.name === "lastSlave") setLastSlave(value);
    if (e.target.name === "numberOfSlaves") setNumberOfSlaves(value);
    if (e.target.name === "specificSlave") setSpecificSlave(value);
  };

  const handleGoClick = async () => {
    let first = firstSlave;
    let last = lastSlave;

    if (detectionMode === "number") {
      first = 1;
      last = numberOfSlaves;
    } else if (detectionMode === "specific") {
      first = last = specificSlave;
    }

    try {
      setConsoleMessages((prev) => [...prev, "Starting slave detection..."]);
      const response = await axios.post("http://localhost:5000/list_sensors", {
        first_slave: first,
        last_slave: last,
        chain_port: chain.chain_port,
        chain_protocol: chain.chain_protocol,
      });

      if (response.data.responsive_slaves) {
        setResponsiveSlaves(response.data.responsive_slaves);
        setIsReadyEnabled(true);
        const formattedSlaves = response.data.responsive_slaves
          .map(
            (slave: Slave) =>
              `Slave ID: ${slave.slave_id}, Sensor ID: ${slave.sensor_id}, Sensor Type: ${slave.sensor_type}`
          )
          .join("\n");
        setConsoleMessages((prev) => [
          ...prev,
          `Responsive slaves detected:\n${formattedSlaves}`,
        ]);
      } else {
        setConsoleMessages((prev) => [
          ...prev,
          "No responsive slaves detected",
        ]);
      }
    } catch (error) {
      setConsoleMessages((prev) => [...prev, "Error detecting slaves"]);
    }
  };

  const handleReady = () => {
    onSlavesDetected(responsiveSlaves);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="salve-detection-modal-overlay">
      <div className="salve-detection-modal">
        <h2>Detect Slaves</h2>
        <div className="salve-detection-options">
          <div
            className={`slave-detection-mode ${
              detectionMode === "range" ? "selected-mode" : ""
            }`}
          >
            <label>
              <input
                type="radio"
                name="detectionMode"
                value="range"
                checked={detectionMode === "range"}
                onChange={handleModeChange}
              />
              Detect by range
            </label>
            <div className="salve-detection-range">
              <label>First Slave ID:</label>
              <input
                type="number"
                name="firstSlave"
                disabled={detectionMode !== "range"}
                value={firstSlave}
                onChange={handleInputChange}
                min={1}
                max={255}
              />
              <label>Last Slave ID:</label>
              <input
                type="number"
                name="lastSlave"
                disabled={detectionMode !== "range"}
                value={lastSlave}
                onChange={handleInputChange}
                min={1}
                max={255}
              />
            </div>
          </div>
          <div
            className={`slave-detection-mode ${
              detectionMode === "number" ? "selected-mode" : ""
            }`}
          >
            <label>
              <input
                type="radio"
                name="detectionMode"
                value="number"
                checked={detectionMode === "number"}
                onChange={handleModeChange}
              />
              Detect a number of slaves
            </label>
            <label>Number of Slaves to Detect:</label>
            <input
              type="number"
              name="numberOfSlaves"
              disabled={detectionMode !== "number"}
              value={numberOfSlaves}
              onChange={handleInputChange}
              min={1}
              max={255}
            />
          </div>
          <div
            className={`slave-detection-mode ${
              detectionMode === "specific" ? "selected-mode" : ""
            }`}
          >
            <label>
              <input
                type="radio"
                name="detectionMode"
                value="specific"
                checked={detectionMode === "specific"}
                onChange={handleModeChange}
              />
              Detect a specific slave
            </label>
            <label>Slave ID to Detect:</label>
            <input
              type="number"
              name="specificSlave"
              disabled={detectionMode !== "specific"}
              value={specificSlave}
              onChange={handleInputChange}
              min={1}
              max={255}
            />
          </div>
        </div>
        <div className="slave-detection-modal-buttons">
          <button onClick={onClose}>Cancel</button>
          <button onClick={handleGoClick}>Go</button>
        </div>
        <div>
          <h3>Console Output:</h3>
          <textarea rows={10} readOnly value={consoleMessages.join("\n")} />
        </div>
        <button onClick={handleReady} disabled={!isReadyEnabled}>
          Ready
        </button>
      </div>
    </div>
  );
};

export default SlaveDetectionModal;
