import React, { useState } from "react";
import axios from "axios";

interface SlaveDetectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSlavesDetected: (slaves: number[]) => void;
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
  const [numSlavesToTest, setNumSlavesToTest] = useState<number>(1);
  const [consoleMessages, setConsoleMessages] = useState<string[]>([]);
  const [responsiveSlaves, setResponsiveSlaves] = useState<number[]>([]);
  const [isReadyEnabled, setIsReadyEnabled] = useState<boolean>(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNumSlavesToTest(Number(e.target.value));
  };

  const handleGoClick = async () => {
    try {
      setConsoleMessages((prev) => [...prev, "Starting slave detection..."]);
      const response = await axios.post("http://localhost:5000/list_sensors", {
        num_slaves_to_test: numSlavesToTest,
        chain_port: chain.chain_port,
        chain_protocol: chain.chain_protocol,
      });

      if (response.data.responsive_slaves) {
        setResponsiveSlaves(response.data.responsive_slaves);
        setIsReadyEnabled(true); // Enable the Ready button
        setConsoleMessages((prev) => [
          ...prev,
          `Responsive slaves detected: ${response.data.responsive_slaves.join(
            ", "
          )}`,
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
    onSlavesDetected(responsiveSlaves); // Pass the responsive slaves to the parent
    onClose(); // Close the modal
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>Detect Slaves</h2>
        <div>
          <label>Number of Slaves to Test (1-255):</label>
          <input
            type="number"
            value={numSlavesToTest}
            onChange={handleInputChange}
            min={1}
            max={255}
          />
        </div>
        <div className="modal-buttons">
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
