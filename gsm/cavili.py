import serial
import time


def send_command(ser, cmd):
    ser.write((cmd + '\r\n').encode())
    time.sleep(1)  # Allow some time for the modem to respond
    return ser.read_all().decode()


modem = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=1)

response = send_command(modem, 'AT+CGDCONT?')

if 'OK' not in response and 'ERROR' in response:
    with open('/home/pi/harp/apn.txt', 'r') as apn_file:
        apn = apn_file.readline().strip()

    command = 'AT+CGDCONT=1,"IP","{}"'.format(apn)
    response = send_command(modem, command)

    if 'OK' in response:
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
        print('Failed to add APN:', apn)
else:
    print('APN is already present')

modem.close()
