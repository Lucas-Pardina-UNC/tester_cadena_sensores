// src/utils/sensorUtils.ts
export const sensorTypeMap: Record<string | number, string> = {
    100: "Energy",
    200: "Air",
    400: "Radiation",
    500: "Anemometer",
    900: "Temperature",
    999: "Temperature",
    1000: "Probe",
    "EP": "Energy (Panel)",
    "EB": "Energy (Battery)",
    "EC": "Energy (Consumption)",
    "HU": "Humidity",
    "PE": "Pressure",
    "PA": "Pressure",
    "TE": "Temperature",
    "RD": "Direct Radiation",
    "RN": "Net Radiation",
    "WD": "Wind Direction",
    "WS": "Wind Speed",
  };
  
  export const getSensorType = (sensor_id: string | number): string | undefined => {
    return sensorTypeMap[sensor_id];
  };
  
  export const openCorrespondingModal = (
    responsiveSlaves: { sensor_id: string | number; sensor_type: string }[],
    setModalState: Record<string, React.Dispatch<React.SetStateAction<boolean>>>
  ) => {
    const openedModals = new Set<string>();
  
    responsiveSlaves.forEach((slave) => {
      const sensorType = getSensorType(slave.sensor_id) || slave.sensor_type;
  
      if (sensorType && setModalState[sensorType] && !openedModals.has(sensorType)) {
        setModalState[sensorType](true);
        openedModals.add(sensorType);
      }
    });
  
    if (openedModals.size === 0) {
      console.log("No recognized sensor type found in the selected chain.");
    }
  };
  
  export const getChainType = (
    responsiveSlaves: { sensor_id: string | number; sensor_type: string }[]
  ): string | "Mixed" | "Unknown" => {
    const chainTypes = new Set<string>();
  
    responsiveSlaves.forEach((slave) => {
      const sensorType = getSensorType(slave.sensor_id) || slave.sensor_type;
  
      if (sensorType) {
        // Map the sensor type to its chain type (e.g., "Energy", "Air", etc.)
        if (sensorType.startsWith("Energy")) {
          chainTypes.add("Energy");
        } else if (sensorType === "Temperature") {
          chainTypes.add("Temperature");
        } else if (sensorType === "Probe") {
          chainTypes.add("Probe");
        } else if (sensorType === "Air" || sensorType === "Humidity" || sensorType === "Pressure") {
          chainTypes.add("Air");
        } else if (sensorType === "Radiation" || sensorType === "Direct Radiation" || sensorType === "Net Radiation") {
          chainTypes.add("Radiation");
        } else if (sensorType === "Anemometer" || sensorType === "Wind Direction" || sensorType === "Wind Speed") {
          chainTypes.add("Anemometer");
        }
      }
    });
  
    // Determine the result based on the number of unique chain types
    if (chainTypes.size === 1) {
      return Array.from(chainTypes)[0]; // Return the single chain type
    } else if (chainTypes.size > 1) {
      return "Mixed"; // Multiple chain types detected
    } else {
      return "Unknown"; // No recognized chain type
    }
  };

  export const openModalByChainType = (
    chainType: string,
    setModalState: Record<string, React.Dispatch<React.SetStateAction<boolean>>>
  ) => {
    if (setModalState[chainType]) {
      setModalState[chainType](true); // Open the modal corresponding to the chain type
    } else {
      console.log(`No modal found for the chain type: ${chainType}`);
    }
  };