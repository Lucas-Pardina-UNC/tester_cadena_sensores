import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import axios from "axios";
import { useProjectContext } from "./ProjectContext";

interface Chain {
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
  //[key: string]: any; // Allows flexibility for additional chain parameters
  fetchChainsData: (projectFolder: string) => Promise<void>; // Exposed fetch function
}

interface ChainsContextType {
  chains: Chain[];
  numberOfChains: number;
  setChainsData: (chains: Chain[]) => void;
}

const ChainsContext = createContext<ChainsContextType | undefined>(undefined);

export const ChainsProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [chains, setChains] = useState<Chain[]>([]);
  const numberOfChains = chains.length;
  const { selectedProject } = useProjectContext(); // Access current project data

  const setChainsData = (newChains: Chain[]) => {
    setChains(newChains);
  };

  const fetchChainsData = async (projectFolder: string) => {
    try {
      const response = await axios.get("http://localhost:5000/get-chains");

      if (response.data.status === "success") {
        const chains = response.data.chains;
        setChainsData(chains); // Update the chains in the context
      } else {
        console.error("Error fetching chains:", response.data.message);
      }
    } catch (error) {
      console.error("Error fetching chains:", error);
    }
  };

  useEffect(() => {
    if (selectedProject?.folder) {
      fetchChainsData(selectedProject.folder); // Initial fetch on component mount
    }
  }, [selectedProject]); // Re-fetch when selectedProject changes

  return (
    <ChainsContext.Provider value={{ chains, numberOfChains, setChainsData }}>
      {children}
    </ChainsContext.Provider>
  );
};

export const useChainsContext = (): ChainsContextType => {
  const context = useContext(ChainsContext);
  if (!context) {
    throw new Error("useChainsContext must be used within a ChainsProvider");
  }
  return context;
};
