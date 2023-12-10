import serial
import time

byte_encoding = "ISO-8859-1"
modem = serial.Serial(port='/dev/ttyACM0', baudrate=460800, timeout=5)
print(modem)


def send_command(ser, cmd):
    modem.write(cmd.encode(byte_encoding) + b"\r")
    time.sleep(0.1)
    return ser.read_all().decode()


def read_lines():
    read = modem.readlines()
    for i, line in enumerate(read):
        read[i] = line.decode(byte_encoding).strip()
    return read


def close():
    modem.close()


# Read the current APN configuration
response = send_command(modem, 'AT+CGDCONT?')
print(response)

# if 'OK' not in response and 'ERROR' in response:
#     with open('/home/pi/harp/apn.txt', 'r') as apn_file:
#         apn = apn_file.readline().strip()
#
#     # Add the APN using AT command
#     command = 'AT+CGDCONT=1,"IP","{}"'.format(apn)
#     response = send_command(modem, command)
#
#     if 'OK' in response:
#         print('APN added successfully:', apn)
#     else:
#         print('Failed to add APN:', apn)
# else:
#     lines = response.split('\r\n')
#     print(lines)
#     for line in lines:
#         if '+CGDCONT: 1' in line:
#             parts = line.split(',')
#             if len(parts) > 2:
#                 current_apn = parts[2].strip('\"')
#                 print('Current APN:', current_apn)
#                 break
#     else:
#         print('APN is already present')

modem.close()
