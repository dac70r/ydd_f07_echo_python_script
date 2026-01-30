
import serial
import time
MESSAGE_BYTES = bytes([0xEE])

def open_serial_port(port_name, baud_rate):
    try:
    # Configure and open the serial port with a timeout
    # Using a 'with' statement ensures the port is closed automatically
        with serial.Serial(port=port_name, baudrate=baud_rate, timeout=1) as ser:
            time.sleep(2) # Wait for the connection to establish (especially for Arduino/microcontrollers)
            print(f"Connected to port {ser.name}")


    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def send_uart_message(port_name, baud_rate, message):
    try:
        # Configure and open the serial port with a timeout
        # Using a 'with' statement ensures the port is closed automatically
        with serial.Serial(port=port_name, baudrate=baud_rate, timeout=1) as ser:

            # Send the data
            print(f"Sending: {message}")
            ser.write(message)

    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Example Usage ---
# On Windows, port is typically 'COMX' (e.g., 'COM3')
# On Linux/macOS, port is typically '/dev/ttyUSBX' or '/dev/ttyACMX'
SERIAL_PORT = 'COM12' # !! REPLACE WITH YOUR ACTUAL PORT NAME !!
BAUD_RATE = 115200  # !! REPLACE WITH YOUR DEVICE'S BAUD RATE !!

if __name__ == "__main__":

    open_serial_port(SERIAL_PORT, BAUD_RATE)
    while True:
        send_uart_message(SERIAL_PORT, BAUD_RATE, MESSAGE_BYTES)
        time.sleep(1)