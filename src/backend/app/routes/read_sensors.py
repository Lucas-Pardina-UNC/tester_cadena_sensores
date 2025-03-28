#import asyncio
from flask import jsonify
from pymodbus import ModbusException
from pymodbus.exceptions import ModbusException
from .legacy_commands import *
from .conversion import *

# -------------------------------- Energy Sensors (100) --------------------------------

async def read_modbus_energy_sensor(slave_id, client):
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
                print(f"Charge Last: {charge}", flush=True)
            # -------------------------------------------------------------------------------------

            # ---------------------------- Read Panel Voltage History -----------------------------
            await get_history_measurement_modbus(client, slave_id, "panel", "voltage", log_data)
            await get_max_measurement_modbus(client, slave_id, "panel", "voltage", log_data)
            await get_min_measurement_modbus(client, slave_id, "panel", "voltage", log_data)
            await get_mean_measurement_modbus(client, slave_id, "panel", "voltage", log_data)
            # -------------------------------------------------------------------------------------

            # ---------------------------- Read Panel Current History -----------------------------
            await get_history_measurement_modbus(client, slave_id, "panel", "current", log_data)
            await get_max_measurement_modbus(client, slave_id, "panel", "current", log_data)
            await get_min_measurement_modbus(client, slave_id, "panel", "current", log_data)
            await get_mean_measurement_modbus(client, slave_id, "panel", "current", log_data)
            # -------------------------------------------------------------------------------------

            # ---------------------------- Read Battery Voltage History ---------------------------
            await get_history_measurement_modbus(client, slave_id, "battery", "voltage", log_data)
            await get_max_measurement_modbus(client, slave_id, "battery", "voltage", log_data)
            await get_min_measurement_modbus(client, slave_id, "battery", "voltage", log_data)
            await get_mean_measurement_modbus(client, slave_id, "battery", "voltage", log_data)
            # -------------------------------------------------------------------------------------

            # ---------------------------- Read Battery Current History ---------------------------
            await get_history_measurement_modbus(client, slave_id, "battery", "current", log_data)
            await get_max_measurement_modbus(client, slave_id, "battery", "current", log_data)
            await get_min_measurement_modbus(client, slave_id, "battery", "current", log_data)
            await get_mean_measurement_modbus(client, slave_id, "battery", "current", log_data)
            # -------------------------------------------------------------------------------------

            # ---------------------------- Read Consumption Voltage History -----------------------
            await get_history_measurement_modbus(client, slave_id, "consumption", "voltage", log_data)
            await get_max_measurement_modbus(client, slave_id, "consumption", "voltage", log_data)
            await get_min_measurement_modbus(client, slave_id, "consumption", "voltage", log_data)
            await get_mean_measurement_modbus(client, slave_id, "consumption", "voltage", log_data)
            # -------------------------------------------------------------------------------------

            # ---------------------------- Read Consumption Current History -----------------------
            await get_history_measurement_modbus(client, slave_id, "consumption", "current", log_data)
            await get_max_measurement_modbus(client, slave_id, "consumption", "current", log_data)
            await get_min_measurement_modbus(client, slave_id, "consumption", "current", log_data)
            await get_mean_measurement_modbus(client, slave_id, "consumption", "current", log_data)
            # -------------------------------------------------------------------------------------
        
    except ModbusException:
        pass

    return log_data

async def get_history_measurement_modbus(client, slave_id, measurement, measure_type, log_data):
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
            converted_value = adc_to_energy_voltage_value(read_value.registers[0]) if measure_type == "voltage" else adc_to_energy_current_value(read_value.registers[0])
            history_values.append(converted_value)
            print(f"{measurement.capitalize()} {measure_type.capitalize()} History [{i}]: {converted_value} | ADC value: {read_value.registers[0]}", flush=True)
            log_data.append((slave_id, converted_value))
    
    return history_values

async def get_max_measurement_modbus(client, slave_id, measurement, measure_type, log_data):
    max_registers = {
        "panel_voltage": 11, "panel_current": 22,
        "battery_voltage": 33, "battery_current": 44,
        "consumption_voltage": 55, "consumption_current": 66
    }
    
    register = max_registers[f"{measurement}_{measure_type}"]
    read_value = await client.read_input_registers(register, count=1, slave=slave_id)
    if not read_value.isError():
        converted_value = adc_to_energy_voltage_value(read_value.registers[0]) if measure_type == "voltage" else adc_to_energy_current_value(read_value.registers[0])
        print(f"{measurement.capitalize()} {measure_type.capitalize()} Max: {converted_value}", flush=True)
        log_data.append((slave_id, converted_value))
        return converted_value
    return None

async def get_min_measurement_modbus(client, slave_id, measurement, measure_type, log_data):
    min_registers = {
        "panel_voltage": 12, "panel_current": 23,
        "battery_voltage": 34, "battery_current": 45,
        "consumption_voltage": 56, "consumption_current": 67
    }
    
    register = min_registers[f"{measurement}_{measure_type}"]
    read_value = await client.read_input_registers(register, count=1, slave=slave_id)
    if not read_value.isError():
        converted_value = adc_to_energy_voltage_value(read_value.registers[0]) if measure_type == "voltage" else adc_to_energy_current_value(read_value.registers[0])
        print(f"{measurement.capitalize()} {measure_type.capitalize()} Min: {converted_value}", flush=True)
        log_data.append((slave_id, converted_value))
        return converted_value
    return None

async def get_mean_measurement_modbus(client, slave_id, measurement, measure_type, log_data):
    mean_registers = {
        "panel_voltage": 13, "panel_current": 24,
        "battery_voltage": 35, "battery_current": 46,
        "consumption_voltage": 57, "consumption_current": 68
    }
    
    register = mean_registers[f"{measurement}_{measure_type}"]
    read_value = await client.read_input_registers(register, count=1, slave=slave_id)
    if not read_value.isError():
        converted_value = adc_to_energy_voltage_value(read_value.registers[0]) if measure_type == "voltage" else adc_to_energy_current_value(read_value.registers[0])
        print(f"{measurement.capitalize()} {measure_type.capitalize()} Mean: {converted_value}", flush=True)
        log_data.append((slave_id, converted_value))
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

async def read_legacy_energy_sensor_panel(chain_port, slave_id):
    log_data = []

    # Read status
    voltage_chrg_on, current_tail, beacon_status, charging_status = await legacy_read_status(chain_port, slave_id)
    
    # Print status
    print(f"Tail Current: {current_tail}", flush=True)
    print(f"Voltage Charge On: {voltage_chrg_on}", flush=True)
    print(f"Beacon Status: {beacon_status}", flush=True)
    print(f"Charging Status: {charging_status}", flush=True)
    
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

    # Log data
    log_data.extend([
        (slave_id, panel_current_history),
        (slave_id, panel_voltage_history),
        (slave_id, panel_max_current),
        (slave_id, panel_min_current),
        (slave_id, panel_mean_current),
        (slave_id, panel_max_voltage),
        (slave_id, panel_min_voltage),
        (slave_id, panel_mean_voltage),
    ])

    return log_data

async def read_legacy_energy_sensor_battery(chain_port, slave_id):
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

    # Log data
    log_data.extend([
        (slave_id, battery_current_history),
        (slave_id, battery_voltage_history),
        (slave_id, battery_max_current),
        (slave_id, battery_min_current),
        (slave_id, battery_mean_current),
        (slave_id, battery_max_voltage),
        (slave_id, battery_min_voltage),
        (slave_id, battery_mean_voltage),
    ])

    return log_data

async def read_legacy_energy_sensor_consumption(chain_port, slave_id):
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

    # Log data
    log_data.extend([
        (slave_id, consumption_current_history),
        (slave_id, consumption_voltage_history),
        (slave_id, consumption_max_current),
        (slave_id, consumption_min_current),
        (slave_id, consumption_mean_current),
        (slave_id, consumption_max_voltage),
        (slave_id, consumption_min_voltage),
        (slave_id, consumption_mean_voltage),
    ])

    return log_data


# -------------------------------- /Energy Sensors (100) --------------------------------

# -------------------------------- Air Sensors (200) ------------------------------------
async def read_modbus_air_sensors(slave_id, client):
    log_data = []
    
    # Get Pressure calibration values (coef)
    coefficients = []
    coefficients_ok = []
    coef_names = ["dig_t1", "dig_t2", "dig_t3", "dig_p1", "dig_p2", "dig_p3", "dig_p4", "dig_p5", "dig_p6", "dig_p7", "dig_p8", "dig_p9"]

    try:
            write_response = await client.write_coil(0, True, slave=slave_id)  # Sense All
            
            if not write_response.isError():
                # Medir Coeficientes
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
                
                read_temperature = await client.read_input_registers(2, count=1, slave=slave_id)
                if not read_temperature.isError():
                    ADC_value_temp = read_temperature.registers[0]
                    temperature = adc_to_temperature(ADC_value_temp)
                    log_data.append((slave_id, temperature))
                else:
                    print(f"Error al leer el registro de entrada 2 (aereos - temperatura) para el esclavo {slave_id}", flush=True)  
                
                read_humidity = await client.read_input_registers(3, count=1, slave=slave_id)
                if not read_humidity.isError():
                    ADC_value_humidity = read_humidity.registers[0]
                    humidity = adc_to_humidity(ADC_value_humidity)
                    log_data.append((slave_id, humidity))
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
                else:
                    print(f"Error al leer registros de entrada 6 y 7 (aereos - compensación de temperatura) para el esclavo {slave_id}", flush=True) 
    
                air_pressure = adc_to_air_pressure(ADC_value_temp_comp, ADC_value_pressure, coefficients)
                log_data.append((slave_id, air_pressure))

            else:
                print(f"Error al escribir en la bobina 0 para el esclavo {slave_id}")    
    except ModbusException:
        log_data.append(("Error, modbus exception"))

    return log_data

async def read_legacy_humidity_sensor(chain_port, slave_id):
    log_data = []
    
    legacy_value = legacy_measurement(chain_port, slave_id)
    if legacy_value:
        humidity = adc_to_humidity(int(legacy_value))
    else:
        humidity = 4444

    log_data.append((slave_id, legacy_value, humidity))

    print(log_data, flush=True)
    return log_data

async def read_legacy_pressure_sensor(chain_port, slave_id):
    log_data = []
    
    # ------------------------ Get Pressure calibration values (coef) ------------------------
    coefficients = []

    coefficients = legacy_get_coef(chain_port)

    if coefficients == None:
        print(f"Error al leer los coeficientes para el esclavo {slave_id}", flush =True)
        return None
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
    
    
    log_data.append((slave_id, ADC_value_press, pressure))

    print(f"Legacy Pressure Log Data: {log_data}", flush=True)
    return log_data

async def read_legacy_temperature_sensor(chain_port, slave_id):
    log_data = []

    legacy_value = legacy_measurement(chain_port, slave_id)
    if legacy_value:
        temperature = adc_to_temperature(int(legacy_value))
    else:
        temperature = 4444
    
    log_data.append((slave_id, legacy_value, temperature))

    print(log_data, flush=True)
    return log_data
# ------------------------------------ /Air Sensors ------------------------------------

# ----------------------------- Radiation Sensors (400) --------------------------------
async def read_modbus_radiation_sensor(slave_id, client):
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
                direct_radiation = adc_to_direct_radiation(ADC_value_1)
                net_radiation = adc_to_net_radiation(ADC_value_2)
                log_data.append((slave_id, ADC_value_1, direct_radiation, ADC_value_2, net_radiation))
            else:
                print(f"Error al leer el registro de entrada 2 para el esclavo {slave_id}")  
        else:
            print(f"Error al escribir en la bobina 0 para el esclavo {slave_id}")    
    except ModbusException:
        pass

    return log_data

async def read_legacy_direct_radiation(chain_port, slave_id):
    log_data = []
    
    legacy_value = legacy_measurement(chain_port, slave_id)
    if legacy_value:
        direct_radiation = adc_to_direct_radiation(int(legacy_value))
    else:
        direct_radiation = 4444

    log_data.append((slave_id, legacy_value, direct_radiation))

    return log_data

async def read_legacy_net_radiation(chain_port, slave_id):
    log_data = []
    
    legacy_value = legacy_measurement(chain_port, slave_id)
    if legacy_value:
        net_radiation = adc_to_net_radiation(int(legacy_value))
    else:
        net_radiation = 4444

    log_data.append((slave_id, legacy_value, net_radiation))

    return log_data

# --------------------------- /Radiation Sensors (400) ------------------------------

# --------------------------- Anemometer Sensor (500) ------------------------------
async def read_modbus_anemometer_sensor(slave_id, client):
    log_data = []

    try:
            write_response = await client.write_coil(0, True, slave=slave_id)
            if not write_response.isError():
                read_response = await client.read_input_registers(2, count=1, slave=slave_id)
                if not read_response.isError():
                    ADC_value = read_response.registers[0]
                    wind_direction = adc_to_wind_direction(ADC_value)
                    log_data.append((slave_id, ADC_value, wind_direction))
                else:
                    print(f"Error al leer el registro de entrada 2 para el esclavo {slave_id}")  
                read_response = await client.read_input_registers(3, count=1, slave=slave_id)
                if not read_response.isError():
                    ADC_value = read_response.registers[0]
                    wind_speed = adc_to_wind_direction(ADC_value)
                    log_data.append((slave_id, ADC_value, wind_speed))
                else:
                    print(f"Error al leer el registro de entrada 2 para el esclavo {slave_id}") 
            else:
                print(f"Error al escribir en el coil 0 para el esclavo {slave_id}")    
    except ModbusException:
        log_data.append(("Error, modbus exception"))
    
    return log_data

async def read_legacy_wind_direction(chain_port, slave_id):
    log_data = []
    
    legacy_value = legacy_wind_measurement(chain_port, slave_id)
    if legacy_value:
        wind_direction = adc_to_wind_direction(int(legacy_value))
        #print(f"Wind direction: {wind_direction}", flush=True)
    else:
        wind_direction = 4444

    log_data.append((slave_id, legacy_value, wind_direction))

    return log_data

async def read_legacy_wind_speed(chain_port, slave_id):
    log_data = []
    
    legacy_value = legacy_wind_measurement(chain_port, slave_id)
    if legacy_value:
        wind_speed = adc_to_wind_speed(int(legacy_value))
        #print(f"Wind speed: {wind_speed}", flush=True)
    else:
        wind_speed = 4444

    log_data.append((slave_id, legacy_value, wind_speed))

    return log_data

# --------------------------- /Anemometer Sensor (500) -----------------------------

# --------------------------- Temperature Chain (900, 999) --------------------------
async def read_modbus_temperature_chain_sensor(slave_id, client):
    log_data = []

    try:
            write_response = await client.write_coil(0, True, slave=slave_id)
            if not write_response.isError():
                read_response = await client.read_input_registers(2, count=1, slave=slave_id)
                if not read_response.isError():
                    ADC_value = read_response.registers[0]
                    temperature = adc_to_temperature(ADC_value)
                    log_data.append((slave_id, ADC_value, temperature))
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
async def read_modbus_probe_sensors(slave_id, client):
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

async def handle_sensor_reading_modbus(sensor_id : Union[str, int], slave_id : int, client):
    # Establish connection if not already connected
    if not client.connected:
        await client.connect()

    if not client.connected:
        return jsonify({"error": f"Failed to connect to chain for slave {slave_id}"}), 500
    
    return await sensor_type_functions_map[sensor_id](slave_id, client)

async def handle_sensor_reading_legacy(sensor_id : Union[str, int], chain_port, slave_id : int):
    return await sensor_type_functions_map[sensor_id](chain_port, slave_id)

def convert_short(value):
    if value & 0x8000:  # Check if the most significant bit (MSB) is 1 (negative)
        signed_value = value - 0x10000  # Convert to negative using two's complement
    else:
        signed_value = value  # Already positive
    
    return signed_value