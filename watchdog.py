import serial
import time

serial_port = '/dev/ttyUSB2'
baud_rate = 115200

ser = serial.Serial(serial_port, baud_rate, timeout=1)

try:
    ser.write(b'AT+CPOF\r\n')
    time.sleep(1)
    response = ser.read_all().decode('utf-8')

    print("Response from modem:")
    print(response)

finally:
    ser.close()

