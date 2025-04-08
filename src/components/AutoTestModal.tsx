import React, { useState, useEffect } from "react";
import axios from "axios";
import { useChainsContext } from "./ChainsContext";
import { useProjectContext } from "./ProjectContext";
import AirTest from "./AirTest";
import EnergyTest from "./EnergyTest";
import ProbeTest from "./ProbeTest";
import RadiationTest from "./RadiationTest";
import TemperatureTest from "./TemperatureTest";
import WindTest from "./WindTest";
import { getChainType, openModalByChainType } from "../utils/sensorUtils";
interface AutoTestModalProps {
  isOpen: boolean;
  onClose: () => void;
}
interface Chain {
  id: string;
  chain_port: string;
  baudrate: number;
  bytesize: number;
  parity: string;
  stopbits: number;
  timeout: number;
  chain_protocol: string;
  chain_available_slaves: Slave[];
  result_columns: string;
  fetchChainsData: (projectFolder: string) => Promise<void>; // Exposed fetch function
  chain_types: string[];
}
interface Slave {
  slave_id: number;
  sensor_id: string;
  sensor_type: string;
}

const AutoTestModal: React.FC<AutoTestModalProps> = ({ isOpen, onClose }) => {
  const { selectedProject } = useProjectContext();
  const project_folder = selectedProject?.folder + "/config.json";
  const { chains, numberOfChains } = useChainsContext();
  let [selectedChainId, setSelectedChainId] = useState("1"); // State for selected chain ID

  useEffect(() => {
    // Wait until chains[0] is defined and set the default chain type
    if (chains.length > 0 && chains[0].chain_types.length > 0) {
      console.log("Default chain type set to:", chains[0].chain_types[0]);
      setSelectedChainType(chains[0].chain_types[0]);
    }
  }, [chains]);
  let [selectedChainType, setSelectedChainType] = useState("Temperature");

  const [activeTab, setActiveTab] = useState("Per Time Period");
  const [remainingTime, setRemainingTime] = useState(
    "Auto Test per Time Period"
  );

  const [cycles, setCycles] = useState("");

  const [days, setDays] = useState(0);
  const [hours, setHours] = useState(0);
  const [minutes, setMinutes] = useState(0);
  const [seconds, setSeconds] = useState(0);
  const [intervalDays, setIntervalDays] = useState(0);
  const [intervalHours, setIntervalHours] = useState(0);
  const [intervalMinutes, setIntervalMinutes] = useState(0);
  const [intervalSeconds, setIntervalSeconds] = useState(0);

  // Sensor Specific Modals

  const [isAirModalOpen, setIsAirModalOpen] = useState(false);
  const [isEnergyModalOpen, setIsEnergyModalOpen] = useState(false);
  const [isProbeModalOpen, setIsProbeModalOpen] = useState(false);
  const [isRadiationModalOpen, setIsRadiationModalOpen] = useState(false);
  const [isTemperatureModalOpen, setIsTemperatureModalOpen] = useState(false);
  const [isWindModalOpen, setIsWindModalOpen] = useState(false);

  let getChainIndexbyId = (myId: string): number => {
    for (let i = 0; i < numberOfChains; i++) {
      if (chains[i].id == myId) {
        return i;
      }
    }
    return -1; // Return null if no chain with the given ID is found
  };

  const sensorTypeToModalSetter: Record<
    string,
    React.Dispatch<React.SetStateAction<boolean>>
  > = {
    Energy: setIsEnergyModalOpen,
    "Energy (Panel)": setIsEnergyModalOpen,
    "Energy (Battery)": setIsEnergyModalOpen,
    "Energy (Consumption)": setIsEnergyModalOpen,
    Temperature: setIsTemperatureModalOpen,
    Probe: setIsProbeModalOpen,
    Air: setIsAirModalOpen,
    Radiation: setIsRadiationModalOpen,
    "Direct Radiation": setIsRadiationModalOpen,
    "Net Radiation": setIsRadiationModalOpen,
    Anemometer: setIsWindModalOpen,
    "Wind Direction": setIsWindModalOpen,
    "Wind Speed": setIsWindModalOpen,
    Wind: setIsWindModalOpen,
  };

  const handleTimeChange = (
    value: number,
    maxValue: number,
    setValue: React.Dispatch<React.SetStateAction<number>>,
    nextValue: number,
    setNextValue: React.Dispatch<React.SetStateAction<number>>,
    nextNextValue?: number,
    setNextNextValue?: React.Dispatch<React.SetStateAction<number>>,
    nextMaxValue?: number,
    nextNextNextValue?: number,
    setNextNextNextValue?: React.Dispatch<React.SetStateAction<number>>,
    nextNextMaxValue?: number
  ) => {
    if (value >= maxValue) {
      setValue(0);
      setNextValue(nextValue + 1);
      if (nextMaxValue != undefined && nextNextValue != undefined) {
        if (nextValue + 1 >= nextMaxValue && setNextNextValue) {
          setNextValue(0);
          setNextNextValue(nextNextValue + 1);
        }
      }
      if (
        nextNextValue != undefined &&
        nextNextMaxValue != undefined &&
        nextNextNextValue != undefined &&
        setNextNextValue != undefined
      ) {
        if (nextNextValue + 1 >= nextNextMaxValue && setNextNextNextValue) {
          setNextNextValue(0);
          setNextNextNextValue(nextNextNextValue + 1);
        }
      }
    } else {
      setValue(value);
    }
  };

  const handleReadSensor = async () => {
    if (selectedChainId !== null) {
      let chain_index = parseInt(selectedChainId);
      if (chain_index != -1) {
        openModalByChainType(selectedChainType, sensorTypeToModalSetter);
      }
    }
  };

  const handleRunTestByCycles = async () => {
    try {
      const response = await axios.post(
        "http://localhost:5000/auto_test_by_cycles",
        {
          file_path: project_folder,
          num_cycles: parseInt(cycles),
        }
      );

      if (response.data.status === "success") {
        console.log("Test completed successfully");
      } else {
        console.log("Test failed");
        alert("Test failed");
      }
    } catch (error) {
      console.error("Error running test:", error);
      alert("Error running test");
    }
  };

  const handleRunTest = async () => {
    setRemainingTime("Running...");
    const totalDuration = days * 86400 + hours * 3600 + minutes * 60 + seconds;
    const interval =
      intervalDays * 86400 +
      intervalHours * 3600 +
      intervalMinutes * 60 +
      intervalSeconds;

    try {
      const response = await axios.post(
        "http://localhost:5000/auto_test_with_interval",
        {
          file_path: project_folder,
          total_duration: totalDuration,
          interval: interval,
        }
      );

      if (response.data.status === "success") {
        setRemainingTime("Test completed successfully");
      } else {
        setRemainingTime("Test failed");
      }
    } catch (error) {
      console.error("Error running test:", error);
      setRemainingTime("Test failed");
    }
  };

  if (!isOpen) return null;

  return (
    <div className="autotest-modal-overlay">
      <div className="autotest-modal">
        <div className="autotest-modal-header">
          <h2>Auto Test Modal</h2>
          <button onClick={onClose} className="close-button">
            &times;
          </button>
        </div>
        <div className="autotest-modal-tabs">
          <button
            className={activeTab === "Per Time Period" ? "active" : ""}
            onClick={() => setActiveTab("Per Time Period")}
          >
            Per Time Period
          </button>
          <button
            className={activeTab === "Per Cycles" ? "active" : ""}
            onClick={() => setActiveTab("Per Cycles")}
          >
            Per Cycles
          </button>
          <button
            className={activeTab === "Slave Specific Test" ? "active" : ""}
            onClick={() => setActiveTab("Slave Specific Test")}
          >
            Slave Specific Test
          </button>
        </div>

        <div className="autotest-modal-content">
          {activeTab === "Per Time Period" && (
            <div className="tab-content">
              <label>
                Time Period (DD:HH:MM:SS):
                <div className="time-period-inputs">
                  <input
                    type="number"
                    min="0"
                    value={days}
                    onChange={(e) => setDays(parseInt(e.target.value))}
                    placeholder="Days"
                  />
                  <input
                    type="number"
                    min="0"
                    max="24"
                    value={hours}
                    onChange={(e) =>
                      handleTimeChange(
                        parseInt(e.target.value),
                        24,
                        setHours,
                        days,
                        setDays
                      )
                    }
                    placeholder="Hours"
                  />
                  <input
                    type="number"
                    min="0"
                    max="60"
                    value={minutes}
                    onChange={(e) =>
                      handleTimeChange(
                        parseInt(e.target.value),
                        60,
                        setMinutes,
                        hours,
                        setHours,
                        days,
                        setDays,
                        24
                      )
                    }
                    placeholder="Minutes"
                  />
                  <input
                    type="number"
                    min="0"
                    max="60"
                    value={seconds}
                    onChange={(e) =>
                      handleTimeChange(
                        parseInt(e.target.value),
                        60,
                        setSeconds,
                        minutes,
                        setMinutes,
                        hours,
                        setHours,
                        60,
                        days,
                        setDays,
                        24
                      )
                    }
                    placeholder="Seconds"
                  />
                </div>
              </label>
              <label>
                Interval Between Samples (DD:HH:MM:SS):
                <div className="time-period-inputs">
                  <input
                    type="number"
                    min="0"
                    value={intervalDays}
                    onChange={(e) => setIntervalDays(parseInt(e.target.value))}
                    placeholder="Days"
                  />
                  <input
                    type="number"
                    min="0"
                    max="24"
                    value={intervalHours}
                    onChange={(e) =>
                      handleTimeChange(
                        parseInt(e.target.value),
                        24,
                        setIntervalHours,
                        intervalDays,
                        setIntervalDays
                      )
                    }
                    placeholder="Hours"
                  />
                  <input
                    type="number"
                    min="0"
                    max="60"
                    value={intervalMinutes}
                    onChange={(e) =>
                      handleTimeChange(
                        parseInt(e.target.value),
                        60,
                        setIntervalMinutes,
                        intervalHours,
                        setIntervalHours,
                        intervalDays,
                        setIntervalDays,
                        24
                      )
                    }
                    placeholder="Minutes"
                  />
                  <input
                    type="number"
                    min="0"
                    max="60"
                    value={intervalSeconds}
                    onChange={(e) =>
                      handleTimeChange(
                        parseInt(e.target.value),
                        60,
                        setIntervalSeconds,
                        intervalMinutes,
                        setIntervalMinutes,
                        intervalHours,
                        setIntervalHours,
                        60,
                        intervalDays,
                        setIntervalDays,
                        24
                      )
                    }
                    placeholder="Seconds"
                  />
                </div>
              </label>
              <div className="remaining-time">
                <strong>Remaining Time:</strong> {remainingTime}
              </div>
              <button onClick={handleRunTest}>Run Test</button>
            </div>
          )}

          {activeTab === "Per Cycles" && (
            <div className="tab-content">
              <label>
                Number of Cycles:
                <input
                  type="number"
                  value={cycles}
                  min={0}
                  onChange={(e) => setCycles(e.target.value)}
                />
              </label>
              <button onClick={handleRunTestByCycles}>Run Test</button>
            </div>
          )}

          {activeTab === "Slave Specific Test" && (
            <div className="tab-content">
              {/* <TemperatureTest sensorSerial="ABC" /> */}
              <label>
                Select Chain:
                <select
                  value={selectedChainId || ""}
                  onChange={(e) => {
                    const newChainId = e.target.value;
                    setSelectedChainId(newChainId);
                    console.log("Selected chain ID:", selectedChainId);
                    setSelectedChainType(
                      chains[parseInt(newChainId) - 1].chain_types[0]
                    );
                  }}
                >
                  {chains.map((chain) => (
                    <option key={chain.id} value={chain.id}>
                      {chain.id} ({getChainType(chain.chain_available_slaves)})
                      ({chain.chain_port})
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Select from available chain types:
                <select
                  value={selectedChainType || ""}
                  onChange={(e) => {
                    const newChainType = e.target.value;
                    setSelectedChainType(newChainType);
                    console.log("Selected chain type:", selectedChainType);
                  }}
                >
                  {chains[getChainIndexbyId(selectedChainId)].chain_types.map(
                    (chainType, index) => (
                      <option key={index} value={chainType}>
                        {chainType}
                      </option>
                    )
                  )}
                </select>
              </label>
              <button onClick={handleReadSensor}>
                Perform Sensor Specific Single Test
              </button>
            </div>
          )}
        </div>
        <button className="auto-test-button" onClick={onClose}>
          Cancel
        </button>
      </div>
      <AirTest
        isOpen={isAirModalOpen}
        onClose={() => setIsAirModalOpen(false)}
      />
      <EnergyTest
        isOpen={isEnergyModalOpen}
        onClose={() => setIsEnergyModalOpen(false)}
        projectFolder={project_folder} // Passing project folder
        selectedChainId={selectedChainId} // Passing selected chain ID
      />
      <ProbeTest
        isOpen={isProbeModalOpen}
        onClose={() => setIsProbeModalOpen(false)}
      />
      <RadiationTest
        isOpen={isRadiationModalOpen}
        onClose={() => setIsRadiationModalOpen(false)}
      />
      <TemperatureTest
        isOpen={isTemperatureModalOpen}
        onClose={() => setIsTemperatureModalOpen(false)}
        projectFolder={project_folder} // Passing project folder
        selectedChainId={selectedChainId} // Passing selected chain ID
      />
      <WindTest
        isOpen={isWindModalOpen}
        onClose={() => setIsWindModalOpen(false)}
      />
    </div>
  );
};

export default AutoTestModal;
