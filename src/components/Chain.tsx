import React, { useState, useEffect } from "react";
import axios from "axios";
import { useChainsContext } from "./ChainsContext";
import { useAlert } from "./CustomAlertContext";

interface ChainProps {
  chain: {
    id: string;
    chain_port: string;
    baudrate: number;
    bytesize: number;
    parity: string;
    stopbits: number;
    timeout: number;
    chain_protocol: string;
    chain_available_slaves: number[];
    result_columns: string;
  };
  isExpanded: boolean;
}

const Chain: React.FC<ChainProps> = ({ chain }) => {
  const [expanded, setExpanded] = useState(false);
  const [editableChain, setEditableChain] = useState(chain);
  const { fetchChainsData } = useChainsContext();
  const { showAlert } = useAlert();
  const [comPorts, setComPorts] = useState<
    { device: string; description: string }[]
  >([]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setEditableChain((prev) => ({
      ...prev,
      [name]:
        name === "chain_available_slaves"
          ? value.split(",").map(Number)
          : value,
    }));
  };

  const handleSave = async () => {
    try {
      const response = await axios.put(
        `http://localhost:5000/update-chain/${chain.id}`,
        editableChain
      );
      if (response.data.status === "success") {
        await showAlert("Chain changes saved successfully!");
        fetchChainsData();
      } else {
        alert(`Error updating chain: ${response.data.message}`);
      }
    } catch (error) {
      console.error("Error updating chain:", error);
      alert("An error occurred while trying to update the chain.");
    }
  };

  const handleDelete = async () => {
    try {
      const response = await fetch(
        `http://localhost:5000/delete-chain/${chain.id}`,
        {
          method: "DELETE",
        }
      );

      if (response.ok) {
        const result = await response.json();
        console.log(result);
        fetchChainsData();
        const message = `Chain with ID ${chain.id} deleted successfully.`;
        await showAlert(message);
        //alert(`Chain with ID ${chain.id} deleted successfully.`);
      } else {
        const error = await response.json();
        alert(`Error deleting chain: ${error.message}`);
      }
    } catch (error) {
      console.error("Error deleting chain:", error);
      alert("An error occurred while trying to delete the chain.");
    }
  };

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

  useEffect(() => {
    setExpanded(false); // Collapse when chain changes
    setEditableChain(chain); // Update the editableChain state to reflect the new chain
  }, [chain]);

  useEffect(() => {
    if (expanded) {
      fetchComPorts();
    }
  }, [expanded]);

  return (
    <div
      style={{
        border: "1px solid #ccc",
        borderRadius: "8px",
        padding: "8px",
        margin: "8px 0",
        cursor: "pointer",
      }}
    >
      <div onClick={() => setExpanded(!expanded)}>
        <strong>ID:</strong> {chain.id} | <strong>Port:</strong>{" "}
        {chain.chain_port}
      </div>
      {expanded && (
        <div style={{ marginTop: "8px" }}>
          <div>
            <label>
              Chain Port:{" "}
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
              {/* <input
                type="text"
                name="chain_port"
                value={editableChain.chain_port}
                onChange={handleInputChange}
              /> */}
            </label>
          </div>
          <div>
            <label>
              Baudrate:{" "}
              <select
                /* type="number" */
                name="baudrate"
                value={editableChain.baudrate}
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
            </label>
          </div>
          <div>
            <label>
              Bytesize:{" "}
              <select
                /* type="number" */
                name="bytesize"
                value={editableChain.bytesize}
                onChange={handleInputChange}
              >
                <option value="5">5 bits</option>
                <option value="6">6 bits</option>
                <option value="7">7 bits</option>
                <option value="8">8 bits</option>
              </select>
            </label>
          </div>
          <div>
            <label>
              Parity:{" "}
              <select
                name="parity"
                value={editableChain.parity}
                onChange={handleInputChange}
              >
                <option value="N">None</option>
                <option value="E">Even</option>
                <option value="O">Odd</option>
                <option value="M">Mark</option>
                <option value="S">Space</option>
              </select>
            </label>
          </div>
          <div>
            <label>
              Stopbits:{" "}
              <select
                /* type="number" */
                name="stopbits"
                value={editableChain.stopbits}
                onChange={handleInputChange}
              >
                <option value="1">1</option>
                <option value="2">2</option>
              </select>
            </label>
          </div>
          <div>
            <label>
              Timeout:{" "}
              <input
                type="number"
                name="timeout"
                min={0}
                value={editableChain.timeout}
                onChange={handleInputChange}
              />
            </label>
          </div>
          <div>
            <label>
              Chain Protocol:{" "}
              <select
                /* type="text" */
                name="chain_protocol"
                value={editableChain.chain_protocol}
                onChange={handleInputChange}
              >
                <option value="legacy">Legacy</option>
                <option value="modbus">Modbus</option>
              </select>
            </label>
          </div>
          <div>
            <label>
              Available Slaves:{" "}
              <input
                type="text"
                name="chain_available_slaves"
                value={editableChain.chain_available_slaves.join(",")}
                onChange={handleInputChange}
              />
            </label>
          </div>
          <div>
            <label>
              Result Columns:{" "}
              <input
                type="text"
                name="result_columns"
                value={editableChain.result_columns}
                onChange={handleInputChange}
              />
            </label>
          </div>
          <div style={{ marginTop: "8px" }}>
            <button onClick={handleSave}>Save</button>
            <button style={{ marginLeft: "8px" }} onClick={handleDelete}>
              Delete
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chain;
