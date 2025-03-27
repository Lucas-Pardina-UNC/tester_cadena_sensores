import re
import serial
import time

def send_command(serial_conn, command):
    """Send a command and wait for a response with a terminator."""
    serial_conn.write(command.encode())
    serial_conn.flush()
    response = read_until(serial_conn, terminator="\r\n", timeout=2)
    return response

def read_until(serial_conn, terminator="\r\n", timeout=1):
    """Read from serial until a terminator or timeout is reached."""
    start_time = time.time()
    response = ""
    while (time.time() - start_time) < timeout:
        if serial_conn.in_waiting > 0:
            response += serial_conn.read(serial_conn.in_waiting).decode('utf-8', errors='ignore')
            if response.endswith(terminator):
                break
        time.sleep(0.01)  # Avoid busy-waiting
    return response

def legacy_measurement(com_port, slave: int) -> str:
    """Perform a measurement using the legacy protocol."""
    try:
        with serial.Serial(port=com_port, baudrate=9600, timeout=1) as ser:
            # Send command to sense
            sense_command = f"L#{slave:03}S\r\n\r\n"  # 1:03 = 001 (three digits format) 
            print(f"Sense Command: {sense_command}", flush=True)
            response = send_command(ser, sense_command)

            time.sleep(2.5) # Sleep for 1 second
            
            # Send command to obtain data
            data_command = f"L#{slave:03}D\r\n\r\n"  # 1:03 = 001 (three digits format) 
            print(f"Data Command: {data_command}", flush=True)
            response = send_command(ser, data_command)
            print(f"Legacy Response: {response}", flush=True)

            # Extract the number after "L>"
            match = re.search(r'L>(\d+)', response)
            if match:
                post_regex = match.group(1) 
                #print(f"legacy_measurement: {post_regex}",flush=True)
                return post_regex  # Return the number found
            else:
                print(f"Slave: {slave}: No se encontró un número válido en la respuesta: {response}.", flush=True)
                return None

    except serial.SerialException as e:
        print(f"Slave: {slave} Error de conexión: {e}", flush=True)
        return None

def legacy_wind_measurement(com_port, slave: int) -> str:
    """Perform a measurement using the legacy protocol."""
    try:
        with serial.Serial(port=com_port, baudrate=9600, timeout=1) as ser:
            # Send command to sense
            sense_command = f"L#{slave:03}S\r\n\r\n"  # 1:03 = 001 (three digits format) 
            response = send_command(ser, sense_command)

            time.sleep(2.5) # Sleep for 1 second
            
            # Send command to obtain data
            data_command = f"L#{slave:03}D\r\n\r\n"
            response = send_command(ser, data_command)

            print(f"response legacy measurement: {response}", flush=True) # Para sensor de dirección y velocidad del viento

            # Extract the number after "L>"
            match = re.search(r'L>(\d+)', response)
            if match:
                post_regex = match.group(1) 
                #print(f"legacy_measurement: {post_regex}",flush=True)
                return post_regex  # Return the number found
            else:
                print(f"Slave: {slave}: No se encontró un número válido en la respuesta: {response}.", flush=True)
                return None

    except serial.SerialException as e:
        print(f"Slave: {slave} Error de conexión: {e}", flush=True)
        return None
    
def legacy_get_sensor_id(com_port, slave: int) -> str:
    """Retrieve the sensor ID using the legacy protocol."""
    sensor_types = {
        "HU": "Humidity",
        "TE": "Temperature",
        "WD": "Wind Direction",
        "WS": "Wind Speed",
        "RD": "Direct Radiation",
        "RN": "Net Radiation",
        "PE": "Pressure",
        "PA": "Pressure",
        'EP' : "Energy (Panel)",  # Panel          
        'EB' : "Energy (Battery)",  # Battery
        'EC' : "Energy (Consumption)"  # Consumption
    }
    try:
        with serial.Serial(port=com_port, baudrate=9600, timeout=1) as ser:
            # Send command to get sensor type code
            #get_id_command = f"L#00{slave}I\r\n\r\n"
            get_id_command = f"L#{three_digit_format(slave)}I\r\n\r\n"
            print(f"Get ID Command: {get_id_command}", flush=True)
            response = send_command(ser, get_id_command)
            
            print(f"response to get ID: ", response, flush=True)
            
            # Extract the sensor type and slave ID
            #match = re.search(r'L>([A-Z]{2})00(\d+)', response)
            match = re.search(r'L>([A-Z]{2})(\d{3})', response)
            if match:
                sensor_code = match.group(1)
                sensor_name = sensor_types.get(sensor_code, "Unknown Sensor")
                print(f"Slave {slave}: Sensor Type: {sensor_name} ({sensor_code})", flush=True)
                #return sensor_code, sensor_name
                return sensor_code, sensor_name
            else:
                print(f"Slave {slave}: No valid sensor type found in response: {response}.")
                return None
    except serial.SerialException as e:
        print(f"Slave {slave} Connection error: {e}")
        return None

# ---------------------------- Legacy Energy Measurements ----------------------------    
def legacy_history_measurement(com_port, slave: int) -> str:
    """Perform a historical measurement using the legacy protocol."""
    legacy_history_measurement = []
    
    try:
        with serial.Serial(port=com_port, baudrate=9600, timeout=1) as ser:
            # Send command to sense
            sense_command = f"L#{slave:03}S\r\n\r\n"
            response = send_command(ser, sense_command)
            
            # Send command to obtain history data
            history_command = f"L#{slave:03}H\r\n\r\n"
            response = send_command(ser, history_command)

            # Extract all numbers after "L>"
            #legacy_history_measurement = re.findall(r'L>(\d+)', response)
            legacy_history_measurement = re.findall(r'L>(-?\d+)', response)
            
            if legacy_history_measurement and len(legacy_history_measurement) == 16:
                return legacy_history_measurement  # Return list of 16 values
            else:
                print(f"Slave: {slave}: Could not extract 8 values from response: {response}. Found {len(legacy_history_measurement)} values.", flush=True)
                return None

    except serial.SerialException as e:
        print(f"Slave: {slave} Error de conexión: {e}", flush=True)
        return None
    
def legacy_metrics_measurement(com_port, slave: int, metric: str):
    """Perform a measurement using the legacy protocol."""
    try:
        with serial.Serial(port=com_port, baudrate=9600, timeout=1) as ser:
            # Send command to sense
            sense_command = f"L#{slave:03}S\r\n\r\n"
            response = send_command(ser, sense_command)
            
            # Send command to obtain data
            data_command = f"L#{slave:03}{metric}\r\n\r\n"
            response = send_command(ser, data_command)

            # Extract two numbers after "L>"
            matches = re.findall(r'L>(-?\d+)', response)

            if len(matches) == 2:
                voltage, current = int(matches[0]), int(matches[1])
                return [voltage, current]  # Return both values as a list
            else:
                print(f"Slave: {slave}: Expected 2 values but found {len(matches)} in response: {response}.", flush=True)
                return None

    except serial.SerialException as e:
        print(f"Slave: {slave} Error de conexión: {e}", flush=True)
        return None
    
def legacy_status_measurement(com_port, slave: int):
    """Perform a status measurement using the legacy protocol."""
    try:
        with serial.Serial(port=com_port, baudrate=9600, timeout=1) as ser:            
            # Send command to obtain status data
            data_command = f"L#{slave:03}E\r\n\r\n"
            response = send_command(ser, data_command)

            # Extract all numbers after "L>"
            matches = re.findall(r'L>(-?\d+)', response)

            if len(matches) == 4:
                return [int(value) for value in matches]  # Convert all matches to integers
            else:
                print(f"Slave: {slave}: Expected 4 values but found {len(matches)} in response: {response}.", flush=True)
                return None

    except serial.SerialException as e:
        print(f"Slave: {slave} Error de conexión: {e}", flush=True)
        return None


def legacy_get_coef(com_port) -> list[int]:
    try:
        with serial.Serial(port=com_port, baudrate=9600, timeout=1) as ser:
            # Send command to update sensor´s calbration coefficients
            get_coeff_command = f"L#008S\r\n\r\n"
            response = send_command(ser, get_coeff_command)
            
            # Send command to get sensor´s calbration coefficients
            get_coeff_command = f"L#008C\r\n\r\n"
            response = send_command(ser, get_coeff_command)

            # Check if response is valid
            if not response or response.strip() in ["", ".", "ERROR", "N/A"]:
                print("Invalid response received",flush=True)
                return None
            
            # Use regex to extract all numbers (including negative ones)
            numbers = re.findall(r'L>(-?\d+)', response)

            if not numbers:
                print("No valid coefficients found in response")
                return None

            # Convert to integers
            numbers = list(map(int, numbers))
            
            return numbers
        
    except serial.SerialException as e:
        print(f"Slave 8 Connection error: {e}")
        return None
    
def three_digit_format(n):
    return f"{n:03}"