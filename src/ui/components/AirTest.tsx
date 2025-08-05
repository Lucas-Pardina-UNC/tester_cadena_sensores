import React, { useState } from "react";
import { useBackendRequest } from "../utils/backendRequest";

interface AirTestProps {
  isOpen: boolean;
  onClose: () => void;
  projectFolder: string; // Path to the project folder
  selectedChainId: string; // Selected chain ID
}

const AirTest: React.FC<AirTestProps> = ({
  isOpen,
  onClose,
  projectFolder,
  selectedChainId,
}) => {
  if (!isOpen) return null; // Don't render the modal if it's not open

  // State variables for Humidity, Pressure, Temperature, and ADC values
  const [humidity, setHumidity] = useState(" - ");
  const [pressure, setPressure] = useState(" - ");
  const [temperature, setTemperature] = useState(" - ");
  const [humidityADC, setHumidityADC] = useState(" - ");
  const [pressureADC, setPressureADC] = useState(" - ");
  const [temperatureADC, setTemperatureADC] = useState(" - ");
  const [calibrationCoefficients, setCalibrationCoefficients] = useState<
    number[] | null
  >(null); // Store calibration coefficients
  const [showADCValues, setShowADCValues] = useState(false); // Toggle ADC values visibility

  const { makeRequest } = useBackendRequest();

  // Function to handle the "Run Test" button
  const handleRunTest = async () => {
    try {
      // Call the endpoint
      const response = await makeRequest("/single_test", {
        method: "POST",
        data: {
          file_path: projectFolder,
          chain_id: selectedChainId,
        },
      });
      /*const response = await axios.post("http://localhost:5000/single_test", {
        // "http://localhost:5000/single_test"
        file_path: projectFolder,
        chain_id: selectedChainId,
      });*/

      if (response.data.status === "success") {
        const logData = response.data.log_data;

        // Parse the new log format
        let coefficients: number[] = [];
        const coefficientKeys = [
          "dig_t1",
          "dig_t2",
          "dig_t3",
          "dig_p1",
          "dig_p2",
          "dig_p3",
          "dig_p4",
          "dig_p5",
          "dig_p6",
          "dig_p7",
          "dig_p8",
          "dig_p9",
        ];

        // Extract calibration coefficients
        coefficientKeys.forEach((key) => {
          const entry = logData.find((item: any) => item[3] === key);
          if (entry) {
            coefficients.push(entry[5]); // Push the value of the coefficient
          }
        });

        // Extract temperature, humidity, and pressure values
        const tempEntry = logData.find((item: any) => item[3] === "air-temp");
        const humidityEntry = logData.find(
          (item: any) => item[3] === "humidity"
        );
        const pressureEntry = logData.find(
          (item: any) => item[3] === "pressure"
        );

        const temp = tempEntry ? tempEntry[5] : null;
        const tempADC = tempEntry ? tempEntry[4] : null;
        const humidityValue = humidityEntry ? humidityEntry[5] : null;
        const humidityADCValue = humidityEntry ? humidityEntry[4] : null;
        const pressureValue = pressureEntry ? pressureEntry[5] : null;
        const pressureADCValue = pressureEntry ? pressureEntry[4] : null;

        // Update state with parsed values
        setCalibrationCoefficients(coefficients);
        setTemperature(temp ? temp.toFixed(2) : " - "); // Format to 2 decimal places
        setTemperatureADC(tempADC ? tempADC.toString() : " - ");
        setHumidity(humidityValue ? humidityValue.toFixed(2) : " - "); // Format to 2 decimal places
        setHumidityADC(humidityADCValue ? humidityADCValue.toString() : " - ");
        setPressure(pressureValue ? pressureValue.toFixed(2) : " - "); // Format to 2 decimal places
        setPressureADC(pressureADCValue ? pressureADCValue.toString() : " - ");
      }
    } catch (error) {
      console.error("Error running air test:", error);
    }
  };

  // Function to handle the "Export Calibration Coefficients" button
  const handleExportCoefficients = async () => {
    if (calibrationCoefficients) {
      const coefNames = [
        "dig_t1",
        "dig_t2",
        "dig_t3",
        "dig_p1",
        "dig_p2",
        "dig_p3",
        "dig_p4",
        "dig_p5",
        "dig_p6",
        "dig_p7",
        "dig_p8",
        "dig_p9",
      ];

      // Create a JSON object with coefficient names and values
      const coefficientsJson = coefNames.reduce((acc, name, index) => {
        acc[name] = calibrationCoefficients[index];
        return acc;
      }, {} as Record<string, number>);

      try {
        // Save the JSON object to a file in the project folder
        const filePath = `${projectFolder}/calibration_coefficients.json`;
        const fileData = JSON.stringify(coefficientsJson, null, 2);

        // Use the File System API to save the file
        const blob = new Blob([fileData], { type: "application/json" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "calibration_coefficients.json";
        link.click();

        console.log(
          "Calibration coefficients exported successfully:",
          filePath
        );
      } catch (error) {
        console.error("Error exporting calibration coefficients:", error);
      }
    } else {
      console.log("No calibration coefficients available to export.");
    }
  };

  return (
    <div className="air-modal-overlay">
      <div className="air-modal">
        <h2>Air Test</h2>
        <button onClick={handleExportCoefficients}>
          Export Calibration Coefficients
        </button>
        <label>
          <input
            type="checkbox"
            checked={showADCValues}
            onChange={() => setShowADCValues(!showADCValues)}
          />
          Show ADC Values
        </label>
        <div className="air-test-fields">
          <div className="air-field">
            <label>Humidity:</label>
            <input type="text" value={humidity} readOnly />
          </div>
          <div className="air-field">
            <label>Pressure:</label>
            <input type="text" value={pressure} readOnly />
          </div>
          <div className="air-field">
            <label>Temperature:</label>
            <input type="text" value={temperature} readOnly />
          </div>
          {showADCValues && (
            <>
              <div className="air-field">
                <label>Humidity ADC:</label>
                <input type="text" value={humidityADC} readOnly />
              </div>
              <div className="air-field">
                <label>Pressure ADC:</label>
                <input type="text" value={pressureADC} readOnly />
              </div>
              <div className="air-field">
                <label>Temperature ADC:</label>
                <input type="text" value={temperatureADC} readOnly />
              </div>
            </>
          )}
        </div>
        <div className="air-test-buttons">
          <button onClick={onClose}>Close</button>
          <button onClick={handleRunTest}>Run Test</button>
        </div>
      </div>
    </div>
  );
};

export default AirTest;
