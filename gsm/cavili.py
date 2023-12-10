import serial
import time


def send_command(ser, cmd):
    ser.write((cmd + '\r\n').encode())
    time.sleep(1)  # Allow some time for the modem to respond
    return ser.read_all().decode()


modem = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=1)

# Read the current APN configuration
response = send_command(modem, 'AT+CGDCONT?')
print(response)

if 'OK' not in response and 'ERROR' in response:
    with open('/home/pi/harp/apn.txt', 'r') as apn_file:
        apn = apn_file.readline().strip()

    # Add the APN using AT command
    command = 'AT+CGDCONT=1,"IP","{}"'.format(apn)
    response = send_command(modem, command)

    if 'OK' in response:
        print('APN added successfully:', apn)
    else:
        print('Failed to add APN:', apn)
else:
    lines = response.split('\r\n')
    print(lines)
    for line in lines:
        if '+CGDCONT: 1' in line:
            parts = line.split(',')
            if len(parts) > 2:
                current_apn = parts[2].strip('\"')
                print('Current APN:', current_apn)
                break
    else:
        print('APN is already present')

modem.close()
