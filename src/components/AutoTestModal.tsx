import React, { useState } from "react";
import axios from "axios";
import { useChainsContext } from "./ChainsContext";
import { useProjectContext } from "./ProjectContext";

interface AutoTestModalProps {
  isOpen: boolean;
  onClose: () => void;
}
interface Slave {
  slave_id: number;
  sensor_id: string;
  sensor_type: string;
}

const AutoTestModal: React.FC<AutoTestModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState("Per Time Period");
  //const [timePeriod, setTimePeriod] = useState("");
  //const [interval, setInterval] = useState("");
  const [remainingTime, setRemainingTime] = useState(
    "Auto Test per Time Period"
  );

  const [cycles, setCycles] = useState("");

  /* const [selectedChain, setSelectedChain] = useState(""); */
  const [selectedChain, setSelectedChain] = useState("");
  const [responsiveSlaves, setResponsiveSlaves] = useState<Slave[]>([]);
  const [selectedSlave, setSelectedSlave] = useState("");
  const [sensorValue, setSensorValue] = useState("");
  const [days, setDays] = useState(0);
  const [hours, setHours] = useState(0);
  const [minutes, setMinutes] = useState(0);
  const [seconds, setSeconds] = useState(0);
  const [intervalDays, setIntervalDays] = useState(0);
  const [intervalHours, setIntervalHours] = useState(0);
  const [intervalMinutes, setIntervalMinutes] = useState(0);
  const [intervalSeconds, setIntervalSeconds] = useState(0);
  const { chains, fetchChainsData } = useChainsContext();
  const { selectedProject } = useProjectContext();
  const project_folder = selectedProject?.folder + "/config.json";

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
    try {
      const response = await axios.post("http://localhost:5000/read_sensor", {
        file_path: project_folder,
        chain_id: parseInt(selectedChain),
        slave_id: parseInt(selectedSlave),
      });
      //console.log(response.data);
      setSensorValue(response.data.temperature);
    } catch (error) {
      console.error("Error reading sensor:", error);
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
        //console.log(response.data);
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
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h2>Auto Test Modal</h2>
          <button onClick={onClose} className="close-button">
            &times;
          </button>
        </div>
        <div className="modal-tabs">
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

        <div className="modal-content">
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
              <label>
                Select Chain:
                <select
                  value={selectedChain}
                  onChange={(e) => {
                    const selectedChainId = e.target.value;
                    setSelectedChain(selectedChainId);
                    // Find the selected chain's slaves and set them in responsiveSlaves
                    const selectedChainData = chains.find(
                      (chain) => Number(chain.id) == Number(selectedChainId) // Convert selectedChainId to a number
                    );
                    if (selectedChainData) {
                      setResponsiveSlaves(
                        selectedChainData.chain_available_slaves
                      );
                    } else {
                      setResponsiveSlaves([]); // Clear the list if no chain is selected
                    }
                  }}
                  onClick={fetchChainsData}
                >
                  <option value="">-- Select Chain --</option>
                  {chains.map((chain) => (
                    <option key={chain.id} value={chain.id}>
                      {chain.id}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Select Slave:
                <select
                  value={selectedSlave}
                  onChange={(e) => setSelectedSlave(e.target.value)}
                  disabled={!selectedChain}
                >
                  <option value="">-- Select Slave --</option>
                  {responsiveSlaves.map((slave) => (
                    <option key={slave.slave_id} value={slave.slave_id}>
                      {slave.slave_id}
                    </option>
                  ))}
                </select>
              </label>
              <button onClick={handleReadSensor}>Read Sensor</button>
            </div>
          )}
        </div>
        <button className="auto-test-button" onClick={onClose}>
          Cancel
        </button>
      </div>
    </div>
  );
};

export default AutoTestModal;
