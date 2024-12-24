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
            sense_command = f"L#00{slave}S\r\n\r\n"
            response = send_command(ser, sense_command)
            
            # Send command to obtain data
            data_command = f"L#00{slave}D\r\n\r\n"
            response = send_command(ser, data_command)

            # Extract the number after "L>"
            match = re.search(r'L>(\d+)', response)
            if match:
                return match.group(1)  # Return the number found
            else:
                print(f"Slave: {slave}: No se encontró un número válido en la respuesta: {response}.")
                return None

    except serial.SerialException as e:
        print(f"Slave: {slave} Error de conexión: {e}")
        return None