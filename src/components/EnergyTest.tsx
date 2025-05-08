import React, { useState } from "react";
import axios from "axios";

interface EnergyTestProps {
  isOpen: boolean;
  onClose: () => void;
  projectFolder: string; // Receiving project folder
  selectedChainId: string; // Receiving selected chain ID
}

const EnergyTest: React.FC<EnergyTestProps> = ({
  isOpen,
  onClose,
  projectFolder,
  selectedChainId,
}) => {
  if (!isOpen) return null; // Don't render the modal if it's not open

  // State for Panel, Battery, and Consumption data
  const [panelData, setPanelData] = useState({
    voltageHistory: Array(8).fill(" - "),
    maxVoltage: " - ",
    minVoltage: " - ",
    meanVoltage: " - ",
    currentHistory: Array(8).fill(" - "),
    maxCurrent: " - ",
    minCurrent: " - ",
    meanCurrent: " - ",
  });

  const [batteryData, setBatteryData] = useState({
    voltageHistory: Array(8).fill(" - "),
    maxVoltage: " - ",
    minVoltage: " - ",
    meanVoltage: " - ",
    currentHistory: Array(8).fill(" - "),
    maxCurrent: " - ",
    minCurrent: " - ",
    meanCurrent: " - ",
  });

  const [consumptionData, setConsumptionData] = useState({
    voltageHistory: Array(8).fill(" - "),
    maxVoltage: " - ",
    minVoltage: " - ",
    meanVoltage: " - ",
    currentHistory: Array(8).fill(" - "),
    maxCurrent: " - ",
    minCurrent: " - ",
    meanCurrent: " - ",
  });

  // State for other fields
  const [chargingStatus, setChargingStatus] = useState(" - ");
  const [beaconStatus, setBeaconStatus] = useState(" - ");
  const [voltageChargeOn, setVoltageChargeOn] = useState(" - ");
  const [tailCurrent, setTailCurrent] = useState(" - ");

  // Fetch data from the endpoint
  const runEnergyTest = async () => {
    setPanelData({
      voltageHistory: Array(8).fill(" "),
      maxVoltage: " ",
      minVoltage: " ",
      meanVoltage: " ",
      currentHistory: Array(8).fill(" "),
      maxCurrent: " ",
      minCurrent: " ",
      meanCurrent: " ",
    });

    setBatteryData({
      voltageHistory: Array(8).fill(" "),
      maxVoltage: " ",
      minVoltage: " ",
      meanVoltage: " ",
      currentHistory: Array(8).fill(" "),
      maxCurrent: " ",
      minCurrent: " ",
      meanCurrent: " ",
    });

    setConsumptionData({
      voltageHistory: Array(8).fill(" "),
      maxVoltage: " ",
      minVoltage: " ",
      meanVoltage: " ",
      currentHistory: Array(8).fill(" "),
      maxCurrent: " ",
      minCurrent: " ",
      meanCurrent: " ",
    });

    setChargingStatus(" ");
    setBeaconStatus(" ");
    setVoltageChargeOn(" ");
    setTailCurrent(" ");

    try {
      const response = await axios.post("http://localhost:5000/single_test", {
        file_path: projectFolder,
        chain_id: selectedChainId,
      });

      if (response.data.status === "success") {
        const logData = response.data.log_data;

        const extractValue = (key: string) => {
          const entry = logData.find((item: any) => item[3] === key);
          return entry ? entry[5].toString() : " ";
        };

        const chargingStatusEntry = extractValue("Status_Charging");
        const beaconStatusEntry = extractValue("Status_Beacon");
        const voltageChargeOnEntry = extractValue("Status_Voltage_Charge_On");
        const tailCurrentEntry = extractValue("Status_Tail_Current");

        setChargingStatus(chargingStatusEntry);
        setBeaconStatus(beaconStatusEntry);
        setVoltageChargeOn(voltageChargeOnEntry);
        setTailCurrent(tailCurrentEntry);

        const panel = {
          voltageHistory: Array.from({ length: 8 }, (_, i) =>
            extractValue(`panel_voltage_history_${i}`)
          ),
          maxVoltage: extractValue("panel_voltage_max"),
          minVoltage: extractValue("panel_voltage_min"),
          meanVoltage: extractValue("panel_voltage_mean"),
          currentHistory: Array.from({ length: 8 }, (_, i) =>
            extractValue(`panel_current_history_${i}`)
          ),
          maxCurrent: extractValue("panel_current_max"),
          minCurrent: extractValue("panel_current_min"),
          meanCurrent: extractValue("panel_current_mean"),
        };

        const battery = {
          voltageHistory: Array.from({ length: 8 }, (_, i) =>
            extractValue(`battery_voltage_history_${i}`)
          ),
          maxVoltage: extractValue("battery_voltage_max"),
          minVoltage: extractValue("battery_voltage_min"),
          meanVoltage: extractValue("battery_voltage_mean"),
          currentHistory: Array.from({ length: 8 }, (_, i) =>
            extractValue(`battery_current_history_${i}`)
          ),
          maxCurrent: extractValue("battery_current_max"),
          minCurrent: extractValue("battery_current_min"),
          meanCurrent: extractValue("battery_current_mean"),
        };

        const consumption = {
          voltageHistory: Array.from({ length: 8 }, (_, i) =>
            extractValue(`consumption_voltage_history_${i}`)
          ),
          maxVoltage: extractValue("consumption_voltage_max"),
          minVoltage: extractValue("consumption_voltage_min"),
          meanVoltage: extractValue("consumption_voltage_mean"),
          currentHistory: Array.from({ length: 8 }, (_, i) =>
            extractValue(`consumption_current_history_${i}`)
          ),
          maxCurrent: extractValue("consumption_current_max"),
          minCurrent: extractValue("consumption_current_min"),
          meanCurrent: extractValue("consumption_current_mean"),
        };

        setPanelData(panel);
        setBatteryData(battery);
        setConsumptionData(consumption);
      }
    } catch (error) {
      console.error("Error running energy test:", error);
    }
  };

  return (
    <div className="energy-modal-overlay">
      <div className="energy-modal">
        <h2>Energy Test</h2>
        <div className="energy-test-data">
          <div className="test-type">
            {/* Panel Data */}
            <h3>Panel</h3>
            <div className="data-section">
              <div className="voltage-data">
                <label>Voltage History:</label>
                {panelData.voltageHistory.map((value, index) => (
                  <input key={index} type="text" value={value} readOnly />
                ))}
                <label>Max Voltage:</label>
                <input type="text" value={panelData.maxVoltage} readOnly />
                <label>Min Voltage:</label>
                <input type="text" value={panelData.minVoltage} readOnly />
                <label>Mean Voltage:</label>
                <input type="text" value={panelData.meanVoltage} readOnly />
              </div>
              <div className="current-data">
                <label>Current History:</label>
                {panelData.currentHistory.map((value, index) => (
                  <input key={index} type="text" value={value} readOnly />
                ))}
                <label>Max Current:</label>
                <input type="text" value={panelData.maxCurrent} readOnly />
                <label>Min Current:</label>
                <input type="text" value={panelData.minCurrent} readOnly />
                <label>Mean Current:</label>
                <input type="text" value={panelData.meanCurrent} readOnly />
              </div>
            </div>
          </div>

          <div className="test-type">
            {/* Battery Data */}
            <h3>Battery</h3>
            <div className="data-section">
              <div className="voltage-data">
                <label>Voltage History:</label>
                {batteryData.voltageHistory.map((value, index) => (
                  <input key={index} type="text" value={value} readOnly />
                ))}
                <label>Max Voltage:</label>
                <input type="text" value={batteryData.maxVoltage} readOnly />
                <label>Min Voltage:</label>
                <input type="text" value={batteryData.minVoltage} readOnly />
                <label>Mean Voltage:</label>
                <input type="text" value={batteryData.meanVoltage} readOnly />
              </div>
              <div className="current-data">
                <label>Current History:</label>
                {batteryData.currentHistory.map((value, index) => (
                  <input key={index} type="text" value={value} readOnly />
                ))}
                <label>Max Current:</label>
                <input type="text" value={batteryData.maxCurrent} readOnly />
                <label>Min Current:</label>
                <input type="text" value={batteryData.minCurrent} readOnly />
                <label>Mean Current:</label>
                <input type="text" value={batteryData.meanCurrent} readOnly />
              </div>
            </div>
          </div>

          {/* Consumption Data */}
          <div className="test-type">
            <h3>Consumption</h3>
            <div className="data-section">
              <div className="voltage-data">
                <label>Voltage History:</label>
                {consumptionData.voltageHistory.map((value, index) => (
                  <input key={index} type="text" value={value} readOnly />
                ))}
                <label>Max Voltage:</label>
                <input
                  type="text"
                  value={consumptionData.maxVoltage}
                  readOnly
                />
                <label>Min Voltage:</label>
                <input
                  type="text"
                  value={consumptionData.minVoltage}
                  readOnly
                />
                <label>Mean Voltage:</label>
                <input
                  type="text"
                  value={consumptionData.meanVoltage}
                  readOnly
                />
              </div>
              <div className="current-data">
                <label>Current History:</label>
                {consumptionData.currentHistory.map((value, index) => (
                  <input key={index} type="text" value={value} readOnly />
                ))}
                <label>Max Current:</label>
                <input
                  type="text"
                  value={consumptionData.maxCurrent}
                  readOnly
                />
                <label>Min Current:</label>
                <input
                  type="text"
                  value={consumptionData.minCurrent}
                  readOnly
                />
                <label>Mean Current:</label>
                <input
                  type="text"
                  value={consumptionData.meanCurrent}
                  readOnly
                />
              </div>
            </div>
          </div>
        </div>

        {/* Other Fields */}
        <div className="energy-status-data">
          <h3>Status Data</h3>
          <div className="data-section">
            <div className="energy-status-labels">
              <label>Charging Status:</label>
              <label>Beacon Status:</label>
              <label>Voltage Charge On:</label>
              <label>Tail Current:</label>
            </div>
            <div className="energy-status-values">
              <input type="text" value={chargingStatus} readOnly />
              <input type="text" value={beaconStatus} readOnly />
              <input type="text" value={voltageChargeOn} readOnly />
              <input type="text" value={tailCurrent} readOnly />
            </div>
          </div>
        </div>
        <div className="energy-test-buttons">
          <button onClick={onClose}>Close</button>
          <button onClick={runEnergyTest}>Run Test</button>
        </div>
      </div>
    </div>
  );
};

export default EnergyTest;
