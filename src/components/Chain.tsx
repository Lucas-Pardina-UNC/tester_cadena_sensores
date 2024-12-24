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
        fetchChainsData("");
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
        fetchChainsData("");
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

  useEffect(() => {
    setExpanded(false); // Collapse when chain changes
    setEditableChain(chain); // Update the editableChain state to reflect the new chain
  }, [chain]);

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
              <input
                type="text"
                name="chain_port"
                value={editableChain.chain_port}
                onChange={handleInputChange}
              />
            </label>
          </div>
          <div>
            <label>
              Baudrate:{" "}
              <input
                type="number"
                name="baudrate"
                value={editableChain.baudrate}
                onChange={handleInputChange}
              />
            </label>
          </div>
          <div>
            <label>
              Bytesize:{" "}
              <input
                type="number"
                name="bytesize"
                value={editableChain.bytesize}
                onChange={handleInputChange}
              />
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
              </select>
            </label>
          </div>
          <div>
            <label>
              Stopbits:{" "}
              <input
                type="number"
                name="stopbits"
                value={editableChain.stopbits}
                onChange={handleInputChange}
              />
            </label>
          </div>
          <div>
            <label>
              Timeout:{" "}
              <input
                type="number"
                name="timeout"
                value={editableChain.timeout}
                onChange={handleInputChange}
              />
            </label>
          </div>
          <div>
            <label>
              Chain Protocol:{" "}
              <input
                type="text"
                name="chain_protocol"
                value={editableChain.chain_protocol}
                onChange={handleInputChange}
              />
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
