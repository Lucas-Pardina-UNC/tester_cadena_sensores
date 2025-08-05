import React, { useState } from "react";
import { useBackendRequest } from "../utils/backendRequest";

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
    baudrate: number;
    bytesize: number;
    parity: string;
    stopbits: number;
    timeout: number;
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
  const [slaveListInput, setSlaveListInput] = useState<string>(""); // New state for list input
  const [consoleMessages, setConsoleMessages] = useState<string[]>([]);
  const [responsiveSlaves, setResponsiveSlaves] = useState<Slave[]>([]);
  const [isReadyEnabled, setIsReadyEnabled] = useState<boolean>(false);
  const [isPhSensor, setIsPhSensor] = useState<boolean>(false); // New state for the checkbox

  const { makeRequest } = useBackendRequest();

  const handleModeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setDetectionMode(e.target.value);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number(e.target.value);
    if (e.target.name === "firstSlave") setFirstSlave(value);
    if (e.target.name === "lastSlave") setLastSlave(value);
    if (e.target.name === "numberOfSlaves") setNumberOfSlaves(value);
    if (e.target.name === "specificSlave") setSpecificSlave(value);
    if (e.target.name === "slaveListInput") setSlaveListInput(e.target.value);
  };

  const handleGoClick = async () => {
    let slaves: number[] = [];

    console.log("Intento detectar slaves con los siguientes parámetros:");
    console.log("Detection Mode:", detectionMode);
    console.log("First Slave ID:", firstSlave);
    console.log("Last Slave ID:", lastSlave);
    console.log("Number of Slaves:", numberOfSlaves);
    console.log("Specific Slave ID:", specificSlave);
    console.log("Slave List Input:", slaveListInput);
    console.log("Is PH Sensor:", isPhSensor);
    console.log("Chain Data:", chain);
    console.log("Chain Port:", chain.chain_port);
    console.log("Baudrate:", chain.baudrate);
    console.log("Bytesize:", chain.bytesize);
    console.log("Parity:", chain.parity);
    console.log("Stopbits:", chain.stopbits);
    console.log("Timeout:", chain.timeout);
    console.log("Chain Protocol:", chain.chain_protocol);

    if (detectionMode === "range") {
      // Generate a list from firstSlave to lastSlave (inclusive)
      slaves = Array.from(
        { length: lastSlave - firstSlave + 1 },
        (_, i) => firstSlave + i
      );
    } else if (detectionMode === "number") {
      // Generate a list from 1 to numberOfSlaves (inclusive)
      slaves = Array.from({ length: numberOfSlaves }, (_, i) => i + 1);
    } else if (detectionMode === "specific") {
      // List with only the specific slave
      slaves = [specificSlave];
    } else if (detectionMode === "list") {
      // Parse the comma-separated list into an array of integers
      slaves = slaveListInput
        .split(",")
        .map((s) => parseInt(s.trim(), 10))
        .filter((n) => !isNaN(n) && n >= 1 && n <= 255);
    }

    const payload: any = {
      chain_port: chain.chain_port,
      baudrate: chain.baudrate,
      bytesize: chain.bytesize,
      parity: chain.parity,
      stopbits: chain.stopbits,
      timeout: chain.timeout,
      chain_protocol: chain.chain_protocol,
      isPH: isPhSensor,
      slaves,
    };

    try {
      setConsoleMessages((prev) => [...prev, "Starting slave detection..."]);
      const response = await makeRequest("/list_sensors", {
        method: "POST",
        data: payload,
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
          <div
            className={`slave-detection-mode ${
              detectionMode === "list" ? "selected-mode" : ""
            }`}
          >
            <label>
              <input
                type="radio"
                name="detectionMode"
                value="list"
                checked={detectionMode === "list"}
                onChange={handleModeChange}
              />
              Detect from list
            </label>
            <label>Slave IDs (comma separated):</label>
            <input
              type="text"
              name="slaveListInput"
              disabled={detectionMode !== "list"}
              value={slaveListInput}
              onChange={handleInputChange}
              placeholder="e.g. 1,3,5,7"
            />
          </div>
        </div>
        <div>
          <label>
            <input
              type="checkbox"
              checked={isPhSensor}
              onChange={(e) => setIsPhSensor(e.target.checked)}
            />
            isPh sensor?
          </label>
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
