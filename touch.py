import serial
import time

# Set up the serial connection
ser = serial.Serial('COM6', 1200)  # Open COM6 at 1200 baud rate
time.sleep(1)  # Wait a moment for the connection to establish

# Send a newline character (or any other character) to trigger the reset
ser.write(b'\r')  # \r = Carriage return, or \n = newline
ser.close()
