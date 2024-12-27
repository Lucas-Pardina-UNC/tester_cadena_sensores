import React, { useState, useEffect } from "react";
import axios from "axios";
import { useProjectContext } from "./ProjectContext";
import { useChainsContext } from "./ChainsContext";
import SlaveDetectionModal from "./SlaveDetectionModal";
import { useAlert } from "./CustomAlertContext";

interface Chain {
  chain_port: string;
  baudrate: number;
  bytesize: number;
  parity: string;
  stopbits: number;
  timeout: number;
  chain_protocol: string;
  chain_available_slaves: number[];
}

interface AddChainModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const AddChainModal: React.FC<AddChainModalProps> = ({ isOpen, onClose }) => {
  const { selectedProject } = useProjectContext();
  const { fetchChainsData } = useChainsContext();
  const [chain, setChain] = useState<Chain>({
    chain_port: "",
    baudrate: 9600,
    bytesize: 8,
    parity: "N",
    stopbits: 1,
    timeout: 1,
    chain_protocol: "legacy",
    chain_available_slaves: [],
  });
  const defaultChain: Chain = {
    chain_port: "",
    baudrate: 9600,
    bytesize: 8,
    parity: "N",
    stopbits: 1,
    timeout: 1,
    chain_protocol: "legacy",
    chain_available_slaves: [],
  };
  const [comPorts, setComPorts] = useState<
    { device: string; description: string }[]
  >([]);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [successMessage, setSuccessMessage] = useState<string>("");
  const [isDetectModalOpen, setDetectModalOpen] = useState<boolean>(false); // State to control the new modal
  const { showAlert } = useAlert();

  const resetForm = () => {
    setChain({
      ...defaultChain,
      chain_port: "", // Reset to the placeholder option
    });
    setErrorMessage("");
    setSuccessMessage("");
  };

  useEffect(() => {
    if (isOpen) {
      fetchComPorts();
    }
  }, [isOpen]);

  const fetchComPorts = async () => {
    try {
      const response = await axios.get("http://localhost:5000/list-com-ports");
      if (response.data.status === "success") {
        setComPorts(response.data.ports);
      } else {
        console.error("Error fetching COM ports:", response.data.message);
      }
    } catch (error) {
      console.error("Error fetching COM ports:", error);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setChain((prevChain) => ({
      ...prevChain,
      [name]:
        name === "chain_available_slaves"
          ? value.split(",").map(Number)
          : value,
    }));
  };

  const handleSubmit = async () => {
    if (!selectedProject) {
      setErrorMessage("Please select a project first.");
      return;
    }

    try {
      await axios.post(
        `http://localhost:5000/add-chain/${selectedProject.id}`,
        chain
      );
      setSuccessMessage("Chain added successfully!");
      await showAlert("Chain added successfully!");
      setErrorMessage("");
      //await fetchChainsData(selectedProject.folder);
      await fetchChainsData();
      resetForm();
      onClose();
    } catch (error: any) {
      setErrorMessage(error.response?.data?.message || "Error adding chain");
      setSuccessMessage("");
    }
  };

  const openSlaveDetectionModal = () => {
    setDetectModalOpen(true); // Open the detection modal
  };

  const closeSlaveDetectionModal = () => {
    setDetectModalOpen(false); // Close the detection modal
  };

  const handleSlavesDetected = (slaves: number[]) => {
    setChain((prevChain) => ({
      ...prevChain,
      chain_available_slaves: slaves,
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>Add Sensor Chain</h2>
        <div>
          <label>Chain Port:</label>
          <select
            name="chain_port"
            value={chain.chain_port}
            onChange={handleInputChange}
          >
            <option value="">Select a COM Port</option>
            {comPorts.map((port) => (
              <option key={port.device} value={port.device}>
                {port.device} - {port.description}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label>Baudrate:</label>
          <input
            type="number"
            name="baudrate"
            value={chain.baudrate}
            onChange={handleInputChange}
          />
        </div>
        <div>
          <label>Bytesize:</label>
          <input
            type="number"
            name="bytesize"
            value={chain.bytesize}
            onChange={handleInputChange}
          />
        </div>
        <div>
          <label>Parity:</label>
          <input
            type="text"
            name="parity"
            value={chain.parity}
            onChange={handleInputChange}
          />
        </div>
        <div>
          <label>Stopbits:</label>
          <input
            type="number"
            name="stopbits"
            value={chain.stopbits}
            onChange={handleInputChange}
          />
        </div>
        <div>
          <label>Timeout:</label>
          <input
            type="number"
            name="timeout"
            value={chain.timeout}
            onChange={handleInputChange}
          />
        </div>
        <div>
          <label>Chain Protocol:</label>
          <input
            type="text"
            name="chain_protocol"
            value={chain.chain_protocol}
            onChange={handleInputChange}
          />
        </div>
        <div>
          <label>Available Slaves (comma separated):</label>
          <input
            type="text"
            name="chain_available_slaves"
            value={chain.chain_available_slaves.join(",")}
            onChange={handleInputChange}
          />
          <button onClick={openSlaveDetectionModal}>Detect</button>{" "}
          {/* Detect button */}
        </div>
        <div className="modal-buttons">
          <button
            onClick={() => {
              setErrorMessage("");
              setSuccessMessage("");
              resetForm();
              onClose();
            }}
          >
            Cancel
          </button>
          <button onClick={handleSubmit}>Add Chain</button>
        </div>
        {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}
        {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}
      </div>
      <SlaveDetectionModal
        isOpen={isDetectModalOpen}
        onClose={closeSlaveDetectionModal}
        onSlavesDetected={handleSlavesDetected}
        chain={chain}
      />
    </div>
  );
};

export default AddChainModal;
