#import asyncio
from flask import jsonify
from pymodbus import ModbusException
from pymodbus.exceptions import ModbusException
from datetime import datetime, timedelta
from datetime import datetime
from .legacy_commands import *
from .conversion import *
from .project_data import *

# -------------------------------- Energy Sensors (100) --------------------------------

async def read_modbus_energy_sensor(chain_id : int, slave_id, client):
    log_data = []

    charge = "NOT CHARGING"

    try:
        read_all = await client.write_coil(0, True, slave=slave_id)
        if not read_all.isError():
            # ------------------------------------ Read Charge ------------------------------------
            read_charge = await client.read_input_registers(2, count=1, slave=slave_id)
            if not read_charge.isError():
                charge_ADC = read_charge.registers[0]
                if(charge_ADC == 1):
                    charge = "CHARGING"
                else:
                    charge = "NOT CHARGING"
                #print(f"Charge Last: {charge}", flush=True)
            current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            log_data.append((current_timestamp, chain_id, slave_id, "Status_Charging", charge_ADC, charge))
            log_data.append((current_timestamp, chain_id, slave_id, "Status_Beacon", 1, "BEACONS ON"))
            log_data.append((current_timestamp, chain_id, slave_id, "Status_Tail_Current", 1000, "250"))
            log_data.append((current_timestamp, chain_id, slave_id, "Status_Voltage_Charge_On", 3125, "12.5"))
            # -------------------------------------------------------------------------------------

            # ---------------------------- Read Panel Voltage History -----------------------------
            await get_history_measurement_modbus(chain_id, client, slave_id, "panel", "voltage", log_data)
            await get_max_measurement_modbus(chain_id, client, slave_id, "panel", "voltage", log_data)
            await get_min_measurement_modbus(chain_id, client, slave_id, "panel", "voltage", log_data)
            await get_mean_measurement_modbus(chain_id, client, slave_id, "panel", "voltage", log_data)
            # -------------------------------------------------------------------------------------

            # ---------------------------- Read Panel Current History -----------------------------
            await get_history_measurement_modbus(chain_id, client, slave_id, "panel", "current", log_data)
            await get_max_measurement_modbus(chain_id, client, slave_id, "panel", "current", log_data)
            await get_min_measurement_modbus(chain_id, client, slave_id, "panel", "current", log_data)
            await get_mean_measurement_modbus(chain_id, client, slave_id, "panel", "current", log_data)
            # -------------------------------------------------------------------------------------

            # ---------------------------- Read Battery Voltage History ---------------------------
            await get_history_measurement_modbus(chain_id, client, slave_id, "battery", "voltage", log_data)
            await get_max_measurement_modbus(chain_id, client, slave_id, "battery", "voltage", log_data)
            await get_min_measurement_modbus(chain_id, client, slave_id, "battery", "voltage", log_data)
            await get_mean_measurement_modbus(chain_id, client, slave_id, "battery", "voltage", log_data)
            # -------------------------------------------------------------------------------------

            # ---------------------------- Read Battery Current History ---------------------------
            await get_history_measurement_modbus(chain_id, client, slave_id, "battery", "current", log_data)
            await get_max_measurement_modbus(chain_id, client, slave_id, "battery", "current", log_data)
            await get_min_measurement_modbus(chain_id, client, slave_id, "battery", "current", log_data)
            await get_mean_measurement_modbus(chain_id, client, slave_id, "battery", "current", log_data)
            # -------------------------------------------------------------------------------------

            # ---------------------------- Read Consumption Voltage History -----------------------
            await get_history_measurement_modbus(chain_id, client, slave_id, "consumption", "voltage", log_data)
            await get_max_measurement_modbus(chain_id, client, slave_id, "consumption", "voltage", log_data)
            await get_min_measurement_modbus(chain_id, client, slave_id, "consumption", "voltage", log_data)
            await get_mean_measurement_modbus(chain_id, client, slave_id, "consumption", "voltage", log_data)
            # -------------------------------------------------------------------------------------

            # ---------------------------- Read Consumption Current History -----------------------
            await get_history_measurement_modbus(chain_id, client, slave_id, "consumption", "current", log_data)
            await get_max_measurement_modbus(chain_id, client, slave_id, "consumption", "current", log_data)
            await get_min_measurement_modbus(chain_id, client, slave_id, "consumption", "current", log_data)
            await get_mean_measurement_modbus(chain_id, client, slave_id, "consumption", "current", log_data)
            # -------------------------------------------------------------------------------------
        
    except ModbusException:
        pass

    return log_data

async def get_history_measurement_modbus(chain_id : int, client, slave_id, measurement, measure_type, log_data):
    history_start_registers = {
        "panel_voltage": 3, "panel_current": 14,
        "battery_voltage": 25, "battery_current": 36,
        "consumption_voltage": 47, "consumption_current": 58
    }
    
    first_register = history_start_registers[f"{measurement}_{measure_type}"]
    history_values = []
    
    for i in range(8):
        read_value = await client.read_input_registers((first_register + i), count=1, slave=slave_id)
        if not read_value.isError():
            adc_value = read_value.registers[0]
            converted_value = adc_to_energy_voltage_value(read_value.registers[0]) if measure_type == "voltage" else adc_to_energy_current_value(read_value.registers[0])
            history_values.append(converted_value)
            #print(f"{measurement.capitalize()} {measure_type.capitalize()} History [{i}]: {converted_value} | ADC value: {read_value.registers[0]}", flush=True)
            # Obtain current date/time
            current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            measurement_type = f"{measurement}_{measure_type}_history_{i}"
            log_data.append((current_timestamp, chain_id, slave_id, measurement_type, adc_value, converted_value))
    
    return history_values

async def get_max_measurement_modbus(chain_id : int, client, slave_id, measurement, measure_type, log_data):
    max_registers = {
        "panel_voltage": 11, "panel_current": 22,
        "battery_voltage": 33, "battery_current": 44,
        "consumption_voltage": 55, "consumption_current": 66
    }
    
    register = max_registers[f"{measurement}_{measure_type}"]
    read_value = await client.read_input_registers(register, count=1, slave=slave_id)
    if not read_value.isError():
        adc_value = read_value.registers[0]
        converted_value = adc_to_energy_voltage_value(read_value.registers[0]) if measure_type == "voltage" else adc_to_energy_current_value(read_value.registers[0])
        #print(f"{measurement.capitalize()} {measure_type.capitalize()} Max: {converted_value}", flush=True)
        # Obtain current date/time
        current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        measurement_type = f"{measurement}_{measure_type}_max"
        log_data.append((current_timestamp, chain_id, slave_id, measurement_type, adc_value, converted_value))
        return converted_value
    return None

async def get_min_measurement_modbus(chain_id : int, client, slave_id, measurement, measure_type, log_data):
    min_registers = {
        "panel_voltage": 12, "panel_current": 23,
        "battery_voltage": 34, "battery_current": 45,
        "consumption_voltage": 56, "consumption_current": 67
    }
    
    register = min_registers[f"{measurement}_{measure_type}"]
    read_value = await client.read_input_registers(register, count=1, slave=slave_id)
    if not read_value.isError():
        adc_value = read_value.registers[0]
        converted_value = adc_to_energy_voltage_value(read_value.registers[0]) if measure_type == "voltage" else adc_to_energy_current_value(read_value.registers[0])
        #print(f"{measurement.capitalize()} {measure_type.capitalize()} Min: {converted_value}", flush=True)
        # Obtain current date/time
        current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        measurement_type = f"{measurement}_{measure_type}_min"
        log_data.append((current_timestamp, chain_id, slave_id, measurement_type, adc_value, converted_value))
        return converted_value
    return None

async def get_mean_measurement_modbus(chain_id : int, client, slave_id, measurement, measure_type, log_data):
    mean_registers = {
        "panel_voltage": 13, "panel_current": 24,
        "battery_voltage": 35, "battery_current": 46,
        "consumption_voltage": 57, "consumption_current": 68
    }
    
    register = mean_registers[f"{measurement}_{measure_type}"]
    read_value = await client.read_input_registers(register, count=1, slave=slave_id)
    if not read_value.isError():
        adc_value = read_value.registers[0]
        converted_value = adc_to_energy_voltage_value(read_value.registers[0]) if measure_type == "voltage" else adc_to_energy_current_value(read_value.registers[0])
        #print(f"{measurement.capitalize()} {measure_type.capitalize()} Mean: {converted_value}", flush=True)
        # Obtain current date/time
        current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        measurement_type = f"{measurement}_{measure_type}_mean"
        log_data.append((current_timestamp, chain_id, slave_id, measurement_type, adc_value, converted_value))
        return converted_value
    return None

async def legacy_read_history(chain_port, slave_id):
    """
    Reads history measurements from the legacy system and prints raw & converted values.

    Parameters:
    - chain_port: The communication port.
    - slave_id: The sensor ID.
    - voltage_conversion_function: Function to convert raw ADC values for voltage.
    - current_conversion_function: Function to convert raw ADC values for current.

    Returns:
    - Two lists: one with 8 historical voltage measurements, one with 8 historical current measurements.
    """
    read_history = legacy_history_measurement(chain_port, slave_id)
    
    if read_history and len(read_history) == 16:
        raw_voltage_values = [int(val) for val in read_history[:8]]
        raw_current_values = [int(val) for val in read_history[8:]]

        converted_voltage_values = [adc_to_energy_voltage_value(raw) for raw in raw_voltage_values]
        converted_current_values = [adc_to_energy_current_value(raw) for raw in raw_current_values]

        return converted_voltage_values, converted_current_values
    else:
        return [4444] * 8, [4444] * 8

async def legacy_read_metric(chain_port, slave_id, metric_type):
    """
    Reads a metric (max, min, or mean) from the legacy system and prints raw & converted values.
    
    Parameters:
    - chain_port: The communication port.
    - slave_id: The sensor ID.
    - metric_type: 'M' for max, 'm' for min, 'P' for mean.
    - voltage_conversion_function: Function to convert voltage raw ADC values.
    - current_conversion_function: Function to convert current raw ADC values.

    Returns:
    - A tuple (converted_voltage, converted_current), or (4444, 4444) if reading fails.
    """
    read_metric = legacy_metrics_measurement(chain_port, slave_id, metric_type)

    if read_metric and len(read_metric) == 2:
        raw_voltage, raw_current = int(read_metric[0]), int(read_metric[1])
        converted_voltage = adc_to_energy_voltage_value(raw_voltage)
        converted_current = adc_to_energy_current_value(raw_current)

        return converted_voltage, converted_current
    else:
        return 4444, 4444  # Return error values if something goes wrong

async def legacy_read_status(chain_port, slave_id):
    """
    Reads the status data from the legacy system and returns the converted values.

    Parameters:
    - chain_port: The communication port.
    - slave_id: The sensor ID.

    Returns:
    - A list [converted_voltage, converted_current, beacon_status, charging_status].
    """
    read_status = legacy_status_measurement(chain_port, slave_id)

    if read_status and len(read_status) == 4:
        raw_voltage, raw_current, beacon_raw, charging_raw = read_status

        converted_voltage = adc_to_energy_voltage_value(raw_voltage)
        converted_current = adc_to_energy_current_value(raw_current)

        beacon_status = "BEACONS ON" if beacon_raw == 1 else "BEACONS OFF"
        charging_status = "CHARGING" if charging_raw == 1 else "NOT CHARGING"

        return [converted_voltage, converted_current, beacon_status, charging_status]
    else:
        return [4444, 4444, "UNKNOWN", "UNKNOWN"]  # Return error values if something goes wrong

async def read_legacy_energy_sensor_panel(chain_id : int, chain_port, slave_id):
    log_data = []

    # Read status
    voltage_chrg_on, current_tail, beacon_status, charging_status = await legacy_read_status(chain_port, slave_id)
    
    # Print status
    print(f"Tail Current: {current_tail}", flush=True)
    print(f"Voltage Charge On: {voltage_chrg_on}", flush=True)
    print(f"Beacon Status: {beacon_status}", flush=True)
    print(f"Charging Status: {charging_status}", flush=True)

    # Obtain current date/time
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    log_data.append((current_timestamp, chain_id, slave_id, "Status_Charging", charging_status, charging_status))
    log_data.append((current_timestamp, chain_id, slave_id, "Status_Beacon", beacon_status, beacon_status))
    log_data.append((current_timestamp, chain_id, slave_id, "Status_Tail_Current", current_tail, current_tail))
    log_data.append((current_timestamp, chain_id, slave_id, "Status_Voltage_Charge_On", voltage_chrg_on, voltage_chrg_on))
    
    # Read history
    panel_voltage_history, panel_current_history  = await legacy_read_history(chain_port, slave_id)

    # Read metrics
    panel_max_voltage, panel_max_current = await legacy_read_metric(chain_port, slave_id, 'M')
    panel_min_voltage, panel_min_current = await legacy_read_metric(chain_port, slave_id, 'm')
    panel_mean_voltage, panel_mean_current = await legacy_read_metric(chain_port, slave_id, 'P')

    print("Panel Voltage History:")
    for i, value in enumerate(panel_voltage_history):
        print(f"Voltage[{i}]: {value}", flush=True)

    print("Panel Current History:")
    for i, value in enumerate(panel_current_history):
        print(f"Current[{i}]: {value}", flush=True)

    # Print metrics
    print(f"Panel Max Current: {panel_max_current}", flush=True)
    print(f"Panel Min Current: {panel_min_current}", flush=True)
    print(f"Panel Mean Current: {panel_mean_current}", flush=True)

    print(f"Panel Max Voltage: {panel_max_voltage}", flush=True)
    print(f"Panel Min Voltage: {panel_min_voltage}", flush=True)
    print(f"Panel Mean Voltage: {panel_mean_voltage}", flush=True)

    # Obtain current date/time
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    # Voltage history
    for i, value in enumerate(panel_voltage_history):
        log_data.append({
            "timestamp": current_timestamp,
            "chain_id": f"chain_{chain_id}",
            "slave_id": slave_id,
            "value_type": f"panel_voltage_history_{i}",
            "value": value
        })

    # Current history
    for i, value in enumerate(panel_current_history):
        log_data.append({
            "timestamp": current_timestamp,
            "chain_id": f"chain_{chain_id}",
            "slave_id": slave_id,
            "value_type": f"panel_current_history_{i}",
            "value": value
        })

    # Metrics
    metrics = [
        ("panel_voltage_max", panel_max_voltage),
        ("panel_voltage_min", panel_min_voltage),
        ("panel_voltage_mean", panel_mean_voltage),
        ("panel_current_max", panel_max_current),
        ("panel_current_min", panel_min_current),
        ("panel_current_mean", panel_mean_current),
    ]

    for value_type, value in metrics:
        log_data.append({
            "timestamp": current_timestamp,
            "chain_id": f"chain_{chain_id}",
            "slave_id": slave_id,
            "value_type": value_type,
            "value": value
        })

    return log_data

async def read_legacy_energy_sensor_battery(chain_id : int, chain_port, slave_id):
    log_data = []

    # Read history
    battery_voltage_history, battery_current_history  = await legacy_read_history(chain_port, slave_id)

    # Read metrics
    battery_max_voltage, battery_max_current = await legacy_read_metric(chain_port, slave_id, 'M')
    battery_min_voltage, battery_min_current = await legacy_read_metric(chain_port, slave_id, 'm')
    battery_mean_voltage, battery_mean_current = await legacy_read_metric(chain_port, slave_id, 'P')

    print("Battery Voltage History:")
    for i, value in enumerate(battery_voltage_history):
        print(f"Voltage[{i}]: {value}", flush=True)

    print("Battery Current History:")
    for i, value in enumerate(battery_current_history):
        print(f"Current[{i}]: {value}", flush=True)

    # Print metrics
    print(f"Battery Max Current: {battery_max_current}", flush=True)
    print(f"Battery Min Current: {battery_min_current}", flush=True)
    print(f"Battery Mean Current: {battery_mean_current}", flush=True)

    print(f"Battery Max Voltage: {battery_max_voltage}", flush=True)
    print(f"Battery Min Voltage: {battery_min_voltage}", flush=True)
    print(f"Battery Mean Voltage: {battery_mean_voltage}", flush=True)

     # Obtain current date/time
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    # Voltage history
    for i, value in enumerate(battery_voltage_history):
        log_data.append({
            "timestamp": current_timestamp,
            "chain_id": f"chain_{chain_id}",
            "slave_id": slave_id,
            "value_type": f"battery_voltage_history_{i}",
            "value": value
        })

    # Current history
    for i, value in enumerate(battery_current_history):
        log_data.append({
            "timestamp": current_timestamp,
            "chain_id": f"chain_{chain_id}",
            "slave_id": slave_id,
            "value_type": f"battery_current_history_{i}",
            "value": value
        })

    # Metrics
    metrics = [
        ("battery_voltage_max", battery_max_voltage),
        ("battery_voltage_min", battery_min_voltage),
        ("battery_voltage_mean", battery_mean_voltage),
        ("battery_current_max", battery_max_current),
        ("battery_current_min", battery_min_current),
        ("battery_current_mean", battery_mean_current),
    ]

    for value_type, value in metrics:
        log_data.append({
            "timestamp": current_timestamp,
            "chain_id": f"chain_{chain_id}",
            "slave_id": slave_id,
            "value_type": value_type,
            "value": value
        })

    return log_data

async def read_legacy_energy_sensor_consumption(chain_id : int, chain_port, slave_id):
    log_data = []

    # Read history
    consumption_voltage_history, consumption_current_history  = await legacy_read_history(chain_port, slave_id)

    # Read metrics
    consumption_max_voltage, consumption_max_current = await legacy_read_metric(chain_port, slave_id, 'M')
    consumption_min_voltage, consumption_min_current = await legacy_read_metric(chain_port, slave_id, 'm')
    consumption_mean_voltage, consumption_mean_current = await legacy_read_metric(chain_port, slave_id, 'P')

    print("Consumption Voltage History:")
    for i, value in enumerate(consumption_voltage_history):
        print(f"Voltage[{i}]: {value}", flush=True)

    print("Consumption Current History:")
    for i, value in enumerate(consumption_current_history):
        print(f"Current[{i}]: {value}", flush=True)
    
    # Print metrics
    print(f"Consumption Max Current: {consumption_max_current}", flush=True)
    print(f"Consumption Min Current: {consumption_min_current}", flush=True)
    print(f"Consumption Mean Current: {consumption_mean_current}", flush=True)

    print(f"Consumption Max Voltage: {consumption_max_voltage}", flush=True)
    print(f"Consumption Min Voltage: {consumption_min_voltage}", flush=True)
    print(f"Consumption Mean Voltage: {consumption_mean_voltage}", flush=True)

    # Obtain current date/time
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    # Voltage history
    for i, value in enumerate(consumption_voltage_history):
        log_data.append({
            "timestamp": current_timestamp,
            "chain_id": f"chain_{chain_id}",
            "slave_id": slave_id,
            "value_type": f"consumption_voltage_history_{i}",
            "value": value
        })

    # Current history
    for i, value in enumerate(consumption_current_history):
        log_data.append({
            "timestamp": current_timestamp,
            "chain_id": f"chain_{chain_id}",
            "slave_id": slave_id,
            "value_type": f"consumption_current_history_{i}",
            "value": value
        })

    # Metrics
    metrics = [
        ("consumption_voltage_max", consumption_max_voltage),
        ("consumption_voltage_min", consumption_min_voltage),
        ("consumption_voltage_mean", consumption_mean_voltage),
        ("consumption_current_max", consumption_max_current),
        ("consumption_current_min", consumption_min_current),
        ("consumption_current_mean", consumption_mean_current),
    ]

    for value_type, value in metrics:
        log_data.append({
            "timestamp": current_timestamp,
            "chain_id": f"chain_{chain_id}",
            "slave_id": slave_id,
            "value_type": value_type,
            "value": value
        })

    return log_data


# -------------------------------- /Energy Sensors (100) --------------------------------

# -------------------------------- Air Sensors (200) ------------------------------------
async def read_modbus_air_sensors(chain_id : int, slave_id, client):
    log_data = []
    
    # Get Pressure calibration values (coef)
    coefficients = []
    coefficients_ok = []
    coef_names = ["dig_t1", "dig_t2", "dig_t3", "dig_p1", "dig_p2", "dig_p3", "dig_p4", "dig_p5", "dig_p6", "dig_p7", "dig_p8", "dig_p9"]

    try:
            write_response = await client.write_coil(0, True, slave=slave_id)  # Sense All
            
            if not write_response.isError():
                # Medir Coeficientes
                #log_data.append(slave_id)
                for i in range (12):
                    read_coefficient = await client.read_input_registers((8 + i), count=1, slave=slave_id)
                    if not read_coefficient.isError():
                        coef = read_coefficient.registers[0]
                        if coef_names[i] not in ["dig_t1", "dig_p1"]:
                            coef = convert_short(coef)
                        coefficients.append(coef)
                        coefficients_ok.append(True)

                    else:
                        coefficients.append(0)
                        coefficients_ok.append(False)
                
                if False not in coefficients_ok:
                    print(f"Coeficientes: {coefficients}", flush=True)
                    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                    log_data.append((current_timestamp, chain_id, slave_id, "dig_t1" ,0, coefficients[0]))
                    log_data.append((current_timestamp, chain_id, slave_id, "dig_t2" ,0, coefficients[1]))
                    log_data.append((current_timestamp, chain_id, slave_id, "dig_t3" ,0, coefficients[2]))
                    log_data.append((current_timestamp, chain_id, slave_id, "dig_p1" ,0, coefficients[3]))
                    log_data.append((current_timestamp, chain_id, slave_id, "dig_p2" ,0, coefficients[4]))
                    log_data.append((current_timestamp, chain_id, slave_id, "dig_p3" ,0, coefficients[5]))
                    log_data.append((current_timestamp, chain_id, slave_id, "dig_p4" ,0, coefficients[6]))
                    log_data.append((current_timestamp, chain_id, slave_id, "dig_p5" ,0, coefficients[7]))
                    log_data.append((current_timestamp, chain_id, slave_id, "dig_p6" ,0, coefficients[8]))
                    log_data.append((current_timestamp, chain_id, slave_id, "dig_p7" ,0, coefficients[9]))
                    log_data.append((current_timestamp, chain_id, slave_id, "dig_p8" ,0, coefficients[10]))
                    log_data.append((current_timestamp, chain_id, slave_id, "dig_p9" ,0, coefficients[11]))
           
                read_temperature = await client.read_input_registers(2, count=1, slave=slave_id)
                if not read_temperature.isError():
                    ADC_value_temp = read_temperature.registers[0]
                    temperature = adc_to_temperature(ADC_value_temp)
                    # Obtain current date/time
                    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                    log_data.append((current_timestamp, chain_id, slave_id, "air-temp" ,ADC_value_temp, temperature))
                else:
                    print(f"Error al leer el registro de entrada 2 (aereos - temperatura) para el esclavo {slave_id}", flush=True)  
                
                read_humidity = await client.read_input_registers(3, count=1, slave=slave_id)
                if not read_humidity.isError():
                    ADC_value_humidity = read_humidity.registers[0]
                    humidity = adc_to_humidity(ADC_value_humidity)
                    #log_data.append((slave_id, humidity))
                    # Obtain current date/time
                    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                    log_data.append((current_timestamp, chain_id, slave_id, "humidity", ADC_value_humidity, humidity))
                else:
                    print(f"Error al leer el registro de entrada 3 (aereos - humedad) para el esclavo {slave_id}", flush=True) 

                read_pressure_high =  await client.read_input_registers(4, count=1, slave=slave_id)
                read_pressure_low = await client.read_input_registers(5, count=1, slave=slave_id)
                if ((not read_pressure_high.isError()) and (not read_pressure_low.isError())):
                    read_pressure_high = read_pressure_high.registers[0]
                    read_pressure_low = read_pressure_low.registers[0]
                    ADC_value_pressure = (read_pressure_high << 16) | read_pressure_low
                else:
                    print(f"Error al leer registros de entrada 4 y 5 (aereos - presión) para el esclavo {slave_id}", flush=True) 

                temp_compensation_high =  await client.read_input_registers(6, count=1, slave=slave_id)
                temp_compensation_low = await client.read_input_registers(7, count=1, slave=slave_id)
                if ((not temp_compensation_high.isError()) and (not temp_compensation_low.isError())):
                    temp_compensation_high = temp_compensation_high.registers[0]
                    temp_compensation_low = temp_compensation_low.registers[0]
                    ADC_value_temp_comp = (temp_compensation_high << 16) | temp_compensation_low
                    print(f"Temperature ellos Low High: {temp_compensation_high} {temp_compensation_low}", flush=True)
                    print(f"Temperature ellos ADC completo: {ADC_value_temp_comp}", flush=True)
                else:
                    print(f"Error al leer registros de entrada 6 y 7 (aereos - compensación de temperatura) para el esclavo {slave_id}", flush=True) 
    
                air_pressure = adc_to_air_pressure(ADC_value_temp_comp, ADC_value_pressure, coefficients)
                # Obtain current date/time
                current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                log_data.append((current_timestamp, chain_id, slave_id, "pressure", ADC_value_temp_comp, air_pressure))

            else:
                print(f"Error al escribir en la bobina 0 para el esclavo {slave_id}")    
    except ModbusException:
        #print(f"Error de Modbus para el esclavo {slave_id}", flush=True)
        log_data.append((current_timestamp, chain_id, slave_id,"Error", "Error"))

    #print(f"Legacy Air Log Data: {log_data}", flush=True)
    return log_data

async def read_legacy_humidity_sensor(chain_id : int, chain_port, slave_id):
    log_data = []
    
    legacy_value = legacy_measurement(chain_port, slave_id)
    if legacy_value:
        humidity = adc_to_humidity(int(legacy_value))
    else:
        humidity = 4444

    # Obtain current date/time
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    log_data.append((current_timestamp, chain_id, slave_id, "humidity" ,legacy_value, humidity))

    print(log_data, flush=True)
    return log_data

async def read_legacy_pressure_sensor(chain_id : int, chain_port, slave_id):
    log_data = []
    
    # ------------------------ Get Pressure calibration values (coef) ------------------------
    coefficients = []

    coefficients = legacy_get_coef(chain_port)

    if coefficients == None:
        print(f"Error al leer los coeficientes para el esclavo {slave_id}", flush =True)
        return None
    else:
        current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        log_data.append((current_timestamp, chain_id, slave_id, "dig_t1" ,0, coefficients[0]))
        log_data.append((current_timestamp, chain_id, slave_id, "dig_t2" ,0, coefficients[1]))
        log_data.append((current_timestamp, chain_id, slave_id, "dig_t3" ,0, coefficients[2]))
        log_data.append((current_timestamp, chain_id, slave_id, "dig_p1" ,0, coefficients[3]))
        log_data.append((current_timestamp, chain_id, slave_id, "dig_p2" ,0, coefficients[4]))
        log_data.append((current_timestamp, chain_id, slave_id, "dig_p3" ,0, coefficients[5]))
        log_data.append((current_timestamp, chain_id, slave_id, "dig_p4" ,0, coefficients[6]))
        log_data.append((current_timestamp, chain_id, slave_id, "dig_p5" ,0, coefficients[7]))
        log_data.append((current_timestamp, chain_id, slave_id, "dig_p6" ,0, coefficients[8]))
        log_data.append((current_timestamp, chain_id, slave_id, "dig_p7" ,0, coefficients[9]))
        log_data.append((current_timestamp, chain_id, slave_id, "dig_p8" ,0, coefficients[10]))
        log_data.append((current_timestamp, chain_id, slave_id, "dig_p9" ,0, coefficients[11]))
    # -------------------------------------------------------------------------------------------

    # ------------------------ Get Temperature for pressure calculation -------------------------
    read_temperature = legacy_measurement(chain_port, 8)
    if  read_temperature != None:
        ADC_value_temp = int(read_temperature)
    else:
        print(f"Error al leer el registro de entrada 2 (aereos - temperatura) para el esclavo {slave_id}", flush=True)
        return None  
    #--------------------------------------------------------------------------------------------
    
    # -------------------------- Get Pressure ADC measurement & convert--------------------------
    legacy_value = legacy_measurement(chain_port, slave_id)
    if legacy_value != None:
        ADC_value_press = int (legacy_value)
        pressure = adc_to_air_pressure(ADC_value_temp, ADC_value_press, coefficients)
    else:
        print("failed to read pressure", flush=True)
        pressure = 4444
    #--------------------------------------------------------------------------------------------
    
    
    # Obtain current date/time
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    log_data.append((current_timestamp, chain_id, slave_id, "pressure", ADC_value_press, pressure))
    #log_data.append(coefficients)

    #print(f"Legacy Pressure Log Data: {log_data}", flush=True)
    return log_data

async def read_legacy_temperature_sensor(chain_id : int, chain_port, slave_id):
    log_data = []

    legacy_value = legacy_measurement(chain_port, slave_id)
    if legacy_value:
        temperature = adc_to_temperature(int(legacy_value))
    else:
        temperature = 4444
    
    project = get_project_instance()
    #print(f"Chain {chain_id} type:: {project.chains[chain_id].chain_types}", flush=True)
    # Obtain current date/time
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    if("Air" in project.chains[chain_id].chain_types):
        log_data.append((current_timestamp, chain_id, slave_id, "air-temp" ,legacy_value, temperature))
    else:
        log_data.append((current_timestamp, chain_id, slave_id, "temperature",legacy_value, temperature))

    print(log_data, flush=True)
    return log_data
# ------------------------------------ /Air Sensors ------------------------------------

# ----------------------------- Radiation Sensors (400) --------------------------------
async def read_modbus_radiation_sensor(chain_id : int, slave_id, client, offset : int = 0, gain : float = 0.0):
    log_data = []
    read_response = []

    try:
        write_response = await client.write_coil(0, True, slave=slave_id)
        if not write_response.isError():
            read_response[0] = await client.read_input_registers(2, count=1, slave=slave_id)
            read_response[1] = await client.read_input_registers(3, count=1, slave=slave_id)
            if not read_response[0].isError() and not read_response[1].isError():
                ADC_value_1 = read_response[0].registers[0]
                ADC_value_2 = read_response[1].registers[0]
                if (offset != None or gain != None) and (offset != 0 or gain != 0.0):
                    direct_radiation = adc_to_accurate_direct_radiation(int(ADC_value_1), offset, gain)
                else:
                    direct_radiation = adc_to_direct_radiation(ADC_value_1)
                
                net_radiation = adc_to_net_radiation(ADC_value_2)
                # Obtain current date/time
                current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                log_data.append((current_timestamp, chain_id, slave_id, "direct_radiation", ADC_value_1, direct_radiation))
                log_data.append((current_timestamp, chain_id, slave_id, "net_radiation", ADC_value_2, net_radiation))
            else:
                print(f"Error al leer el registro de entrada 2 para el esclavo {slave_id}")  
        else:
            print(f"Error al escribir en la bobina 0 para el esclavo {slave_id}")    
    except ModbusException:
        pass

    return log_data

async def read_legacy_direct_radiation(chain_id : int, chain_port, slave_id, offset : int = 0, gain : float = 0.0):
    log_data = []
    
    legacy_value = legacy_measurement(chain_port, slave_id)
    if legacy_value:
        if (offset != None or gain != None) and (offset != 0 or gain != 0.0):
            direct_radiation = adc_to_accurate_direct_radiation(int(legacy_value), offset, gain)
        direct_radiation = adc_to_direct_radiation(int(legacy_value))
        print(f"Direct radiation: {direct_radiation}", flush=True)
    else:
        direct_radiation = 4444

    # Obtain current date/time
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    log_data.append((current_timestamp, chain_id, slave_id, "direct_radiation", legacy_value, direct_radiation))

    return log_data

async def read_legacy_net_radiation(chain_id : int, chain_port, slave_id):
    log_data = []
    
    legacy_value = legacy_measurement(chain_port, slave_id)
    if legacy_value:
        net_radiation = adc_to_net_radiation(int(legacy_value))
    else:
        net_radiation = 4444

    # Obtain current date/time
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    log_data.append((current_timestamp, chain_id, slave_id, "net_radiation", legacy_value, net_radiation))

    return log_data

# --------------------------- /Radiation Sensors (400) ------------------------------

# --------------------------- Anemometer Sensor (500) ------------------------------
async def read_modbus_anemometer_sensor(chain_id : int, slave_id, client):
    log_data = []

    try:
            write_response = await client.write_coil(0, True, slave=slave_id)
            if not write_response.isError():
                read_response = await client.read_input_registers(2, count=1, slave=slave_id)
                if not read_response.isError():
                    ADC_value = read_response.registers[0]
                    wind_direction = adc_to_wind_direction(ADC_value)
                    # Obtain current date/time
                    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                    log_data.append((current_timestamp, chain_id, slave_id, "wind_direction", ADC_value, wind_direction))
                else:
                    print(f"Error al leer el registro de entrada 2 para el esclavo {slave_id}")  
                read_response = await client.read_input_registers(3, count=1, slave=slave_id)
                if not read_response.isError():
                    ADC_value = read_response.registers[0]
                    wind_speed = adc_to_wind_direction(ADC_value)
                    # Obtain curren7t date/time
                    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                    log_data.append((current_timestamp, chain_id, slave_id, "wind_speed",ADC_value, wind_speed))
                else:
                    print(f"Error al leer el registro de entrada 2 para el esclavo {slave_id}") 
            else:
                print(f"Error al escribir en el coil 0 para el esclavo {slave_id}")    
    except ModbusException:
        log_data.append(("Error, modbus exception"))
    
    return log_data

async def read_legacy_wind_direction(chain_id : int, chain_port, slave_id):
    log_data = []
    
    legacy_value = legacy_wind_measurement(chain_port, slave_id)
    if legacy_value:
        wind_direction = adc_to_wind_direction(int(legacy_value))
        #print(f"Wind direction: {wind_direction}", flush=True)
    else:
        wind_direction = 4444

    # Obtain current date/time
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    log_data.append((current_timestamp, chain_id, slave_id, "wind_direction", legacy_value, wind_direction))

    return log_data

async def read_legacy_wind_speed(chain_id : int, chain_port, slave_id):
    log_data = []
    
    legacy_value = legacy_wind_measurement(chain_port, slave_id)
    if legacy_value:
        wind_speed = adc_to_wind_speed(int(legacy_value))
        #print(f"Wind speed: {wind_speed}", flush=True)
    else:
        wind_speed = 4444

    # Obtain current date/time
    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    log_data.append((current_timestamp, chain_id, slave_id, "wind_speed", legacy_value, wind_speed))

    return log_data

# --------------------------- /Anemometer Sensor (500) -----------------------------

# --------------------------- Temperature Chain (900, 999) --------------------------
async def read_modbus_temperature_chain_sensor(chain_id : int, slave_id, client):
    log_data = []

    try:
            write_response = await client.write_coil(0, True, slave=slave_id)
            if not write_response.isError():
                read_response = await client.read_input_registers(2, count=1, slave=slave_id)
                if not read_response.isError():
                    ADC_value = read_response.registers[0]
                    temperature = adc_to_temperature(ADC_value)
                    # Obtain current date/time
                    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                    log_data.append((current_timestamp, chain_id, slave_id, "temperature", ADC_value, temperature))
                    print(f"Cadena de Temperatura, {log_data}", flush=True)
                else:
                    print(f"Error al leer el registro de entrada 2 para el esclavo {slave_id}")  
            else:
                print(f"Error al escribir en la bobina 0 para el esclavo {slave_id}")    
    except ModbusException:
        log_data.append(("Error, modbus exception"))
    
    return log_data
# --------------------------- /Temperature Chain (900, 999) -------------------------

# --------------------------- Probe Sensors (1000) ---------------------------------
async def read_modbus_probe_sensors(chain_id : int, slave_id, client, offset : int = 0, gain : float = 0.0):
    pass
# --------------------------- /Probe Sensors (1000) --------------------------------

sensor_type_functions_map = {
    100 : read_modbus_energy_sensor,                # Programado ok / Testeado no
    200 : read_modbus_air_sensors,                  # Programado ok / Testeado no
    400 : read_modbus_radiation_sensor,             # Programado ok / Testeado no
    500 : read_modbus_anemometer_sensor,            # Programado ok / Testeado no
    900 : read_modbus_temperature_chain_sensor,     # Programado ok / Testeado no
    999 : read_modbus_temperature_chain_sensor,     # Idem
    1000 : read_modbus_probe_sensors,               # Programado no / Testeado no
    # ----------------------- Energy Board (100 equivalent) -----------------------
    'EP' : read_legacy_energy_sensor_panel,  # Panel            # Programado ok / Testeado no
    'EB' : read_legacy_energy_sensor_battery,  # Battery
    'EC' : read_legacy_energy_sensor_consumption,  # Consumption
    # ----------------------- Air Sensors (200 equivalent)-------------------------
    'HU' : read_legacy_humidity_sensor,
    'PE' : read_legacy_pressure_sensor,
    'PA' : read_legacy_pressure_sensor,
    'TE' : read_legacy_temperature_sensor,  # Temperature chain (900, 999 equivalent)
    # -------------------- Radiation Sensor (400 equivalent)-----------------------
    'RD': read_legacy_direct_radiation,
    'RN': read_legacy_net_radiation,
    # ------------------------ Anemometer (500 equivalent)--------------------------
    'WD': read_legacy_wind_direction,
    'WS': read_legacy_wind_speed,
    
    # ---------------------------- Probe (1000 equivalent)--------------------------
    #'PH': read_legacy_probe_sensor,
    #'pHORP': read_legacy_probe_sensor,
    #'OD': read_legacy_probe_sensor,
    #'ODTemp': read_legacy_probe_sensor,
    #'ODmgL': read_legacy_probe_sensor,
    #'ODPPM': read_legacy_probe_sensor,
    #'phycocyanin': read_legacy_probe_sensor,
    #'chlorophyll': read_legacy_probe_sensor,
    #'turbidity': read_legacy_probe_sensor,
}

async def handle_sensor_reading_modbus(chain_id : int, sensor_id : Union[str, int], slave_id : int, client):
    # Establish connection if not already connected
    if not client.connected:
        await client.connect()

    if not client.connected:
        return jsonify({"error": f"Failed to connect to chain for slave {slave_id}"}), 500
    
    return await sensor_type_functions_map[sensor_id](chain_id, slave_id, client)

async def handle_sensor_reading_legacy(chain_id : int, sensor_id : Union[str, int], chain_port, slave_id : int, offset : int = 0, gain : float = 0.0):
    if sensor_id == 'RD' and (offset != 0 or gain != 0.0):
        return await read_legacy_direct_radiation(chain_id, chain_port, slave_id, offset, gain)
    return await sensor_type_functions_map[sensor_id](chain_id, chain_port, slave_id)

def convert_short(value):
    if value & 0x8000:  # Check if the most significant bit (MSB) is 1 (negative)
        signed_value = value - 0x10000  # Convert to negative using two's complement
    else:
        signed_value = value  # Already positive
    
    return signed_value