import React, { useState } from "react";
import { useProjectContext } from "./ProjectContext";
import { useChainsContext } from "./ChainsContext";
import { useBackendRequest } from "../utils/backendRequest";
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

const AddChain: React.FC = () => {
  const { selectedProject } = useProjectContext();
  const { setChainsData } = useChainsContext();
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
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [successMessage, setSuccessMessage] = useState<string>("");

  const { makeRequest } = useBackendRequest();

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
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
      await makeRequest(`/add-chain/${selectedProject.id}`, {
        method: "POST",
        data: chain,
      });
      /* await axios.post(
        `${backendUrl}/add-chain/${selectedProject.id}`, //`http://localhost:5000/add-chain/${selectedProject.id}`,
        chain
      ); */
      setSuccessMessage("Chain added successfully!");
      setErrorMessage("");
      fetchChainsData(selectedProject.folder);
    } catch (error: any) {
      console.log("Error adding chain:", error);
      setErrorMessage(error.response?.data?.message || "Error adding chain");
      setSuccessMessage("");
    }
  };

  // @ts-ignore
  const fetchChainsData = async (projectFolder: string) => {
    try {
      const response = await makeRequest("/get-chains", {
        method: "GET",
      });
      //const response = await axios.get(`${backendUrl}/get-chains`); // ("http://localhost:5000/get-chains"

      if (response.data.status === "success") {
        const chains = response.data.chains;
        setChainsData(chains); // Update the ChainsContext with the chains data
      } else {
        console.error("Error fetching chains:", response.data.message);
      }
    } catch (error) {
      console.error("Error fetching chains:", error);
    }
  };

  return (
    <div>
      <h2>Add Sensor Chain</h2>
      <div>
        <label>Chain Port:</label>
        <input
          type="text"
          name="chain_port"
          value={chain.chain_port}
          onChange={handleInputChange}
        />
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
      </div>
      <button onClick={handleSubmit}>Add Chain</button>

      {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}
      {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}
    </div>
  );
};

export default AddChain;
