import React, { useState, useEffect } from "react";
import { useProjectContext } from "./ProjectContext";
import { useChainsContext } from "./ChainsContext";
import SlaveDetectionModal from "./SlaveDetectionModal";
import { useAlert } from "./CustomAlertContext";
import { useBackendRequest } from "../utils/backendRequest";

interface Slave {
  slave_id: number;
  sensor_id: string;
  sensor_type: string;
}
interface Chain {
  chain_port: string;
  baudrate: number;
  bytesize: number;
  parity: string;
  stopbits: number;
  timeout: number;
  chain_protocol: string;
  chain_available_slaves: Slave[];
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
  const [slaveIDsList, setSlaveIDsList] = useState<number[]>([]);
  const [slaveTypesList, setSlaveTypesList] = useState<string[]>([]);
  const [isDetectModalOpen, setDetectModalOpen] = useState<boolean>(false); // State to control the new modal
  const { showAlert } = useAlert();
  const { makeRequest } = useBackendRequest();

  //const { backendUrl, loading, error } = useBackendUrl();

  const resetForm = () => {
    setChain({
      ...defaultChain,
      chain_port: "", // Reset to the placeholder option
    });
  };

  useEffect(() => {
    if (isOpen) {
      fetchComPorts();
    }
  }, [isOpen]);

  const fetchComPorts = async () => {
    try {
      const response = await makeRequest("/list-com-ports", {
        method: "GET",
      });
      //const response = await axios.get("http://localhost:5000/list-com-ports"); // "http://localhost:5000/list-com-ports"
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

  const validateChainData = (chain: Chain): string[] => {
    const errors: string[] = [];

    if (!chain.chain_port) {
      errors.push("Chain Port is required");
    }

    const validBaudrates = [
      1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200,
    ];
    if (!validBaudrates.includes(chain.baudrate)) {
      errors.push("Invalid Baudrate");
    }

    const validBytesizes = [5, 6, 7, 8];
    if (!validBytesizes.includes(chain.bytesize)) {
      errors.push("Invalid Bytesize");
    }

    const validParities = ["N", "E", "O", "M", "S"];
    if (!validParities.includes(chain.parity)) {
      errors.push("Invalid Parity");
    }

    const validStopbits = [1, 2];
    if (!validStopbits.includes(chain.stopbits)) {
      errors.push("Invalid Stopbits");
    }

    if (chain.timeout <= 0) {
      errors.push("Timeout must be greater than 0");
    }

    const validProtocols = ["legacy", "modbus"];
    if (!validProtocols.includes(chain.chain_protocol)) {
      errors.push("Invalid Protocol");
    }

    if (!Array.isArray(chain.chain_available_slaves)) {
      errors.push("Available Slaves must be a list");
    }

    return errors;
  };

  const handleSubmit = async () => {
    console.log("Submitting chain:");

    if (!selectedProject) {
      return;
    }

    const errors = validateChainData(chain);
    if (errors.length > 0) {
      await showAlert(`Error adding chain: \n- ${errors.join("\n- ")}`);
      return;
    }

    try {
      //await axios.post("http://localhost:5000/list-com-ports", chain);
      await makeRequest(`/add-chain/${selectedProject.id}`, {
        method: "POST",
        data: chain,
      });
      await showAlert("Chain added successfully!");
      await fetchChainsData();
      resetForm();
      onClose();
    } catch (error: any) {
      await showAlert("Error adding chain");
    }
  };

  const openSlaveDetectionModal = async () => {
    const errors = validateChainData(chain);
    if (errors.length > 0) {
      await showAlert(`Cannot detect slaves: \n- ${errors.join("\n- ")}`);
      return;
    }
    setDetectModalOpen(true); // Open the detection modal
  };

  const closeSlaveDetectionModal = () => {
    setDetectModalOpen(false); // Close the detection modal
  };

  const handleSlavesDetected = (slaves: Slave[]) => {
    setChain((prevChain) => {
      const updatedChain = { ...prevChain, chain_available_slaves: slaves };
      const slaveIds = updatedChain.chain_available_slaves.map(
        (slave) => slave.slave_id
      );
      const sensorTypes = updatedChain.chain_available_slaves.map(
        (slave) => slave.sensor_type
      );
      // Update state for chain and individual lists
      setSlaveIDsList(slaveIds);
      setSlaveTypesList(sensorTypes);

      return updatedChain;
    });
  };

  if (!isOpen) return null;

  return (
    <div className="add-chain-modal-overlay">
      <div className="add-chain-modal">
        <h2>Add Sensor Chain</h2>
        <div className="chain-field">
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
          <label>Baudrate:</label>
          <select
            name="baudrate"
            value={chain.baudrate}
            onChange={handleInputChange}
          >
            <option value="1200">1200</option>
            <option value="2400">2400</option>
            <option value="4800">4800</option>
            <option value="9600">9600</option>
            <option value="14400">14400</option>
            <option value="19200">19200</option>
            <option value="38400">38400</option>
            <option value="57600">57600</option>
            <option value="115200">115200</option>
          </select>
          <label>Bytesize:</label>
          <select
            name="bytesize"
            value={chain.bytesize}
            onChange={handleInputChange}
          >
            <option value="5">5 bits</option>
            <option value="6">6 bits</option>
            <option value="7">7 bits</option>
            <option value="8">8 bits</option>
          </select>
          <label>Parity:</label>
          <select
            name="parity"
            value={chain.parity}
            onChange={handleInputChange}
          >
            <option value="N">None</option>
            <option value="E">Even</option>
            <option value="O">Odd</option>
            <option value="M">Mark</option>
            <option value="S">Space</option>
          </select>
          <label>Stopbits:</label>
          <select
            name="stopbits"
            value={chain.stopbits}
            onChange={handleInputChange}
          >
            <option value="1">1</option>
            <option value="2">2</option>
          </select>
          <label>Timeout:</label>
          <input
            type="number"
            name="timeout"
            value={chain.timeout}
            onChange={handleInputChange}
          />
          <label>Chain Protocol:</label>
          <select
            name="chain_protocol"
            value={chain.chain_protocol}
            onChange={handleInputChange}
          >
            <option value="legacy">Legacy</option>
            <option value="modbus">Modbus</option>
          </select>
          <label>Available Slaves:</label>
          <input
            type="text"
            name="chain_available_slaves"
            value={slaveIDsList.join(",")}
            onChange={handleInputChange}
          />
          <label>Available Slaves Sensor Types:</label>
          <input
            type="text"
            name="chain_available_slaves"
            value={slaveTypesList.join(",")}
            onChange={handleInputChange}
          />
        </div>
        <button onClick={openSlaveDetectionModal}>Detect Slaves</button>{" "}
        <div className="chain-field">{/* Detect button */}</div>
        <div className="modal-buttons">
          <button
            onClick={() => {
              resetForm();
              onClose();
            }}
          >
            Cancel
          </button>
          <button onClick={handleSubmit}>Add Chain</button>
        </div>
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
