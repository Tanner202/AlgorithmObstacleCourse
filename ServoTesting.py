import serial
import time

arduino = serial.Serial('/dev/tty.usbserial-10', 9600)  # Mac example port
time.sleep(2)

arduino.write(b"ON\n")
print("Sent ON")

time.sleep(2)

arduino.write(b"OFF\n")
print("Sent OFF")