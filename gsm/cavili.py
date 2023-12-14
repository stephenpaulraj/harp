#!/usr/bin/env python3

from sim_modem import Modem
import time
import os
import sys


def update_apn(modem, APN, timeout=10):
    try:
        modem.comm.send('AT+CGDCONT=1,\"IP\",\"' + APN + '\"')
        read = modem.comm.read_lines(timeout=timeout)
        print(read)
        time.sleep(0.5)
        if modem.debug:
            print("Device responded: ", read)
        return read[1]
    except TimeoutError:
        print("Timeout: Modem response not received within {} seconds.".format(timeout))
        return None


def is_valid_apn_configured(modem, timeout=10):
    try :
        modem.comm.send('AT+CGDCONT?')
        response = modem.comm.read_lines()
        time.sleep(0.5)
        return response
    except TimeoutError:
        print("Timeout: Modem response not received within {} seconds.".format(timeout))
        return None


if __name__ == '__main__':
    # c = Modem('/dev/ttyACM0')  # Replace 'Modem' with the actual class from 'sim_modem'

    start = time.time()

    # while True:
    #     is_valid_apn_configured(c)
    # if time.time() - start > 10:
    #     start = time.time()
    #
    #     with open('/home/pi/apn1.txt', 'r') as f:
    #         ser1 = f.read().strip()
    #     print(ser1)
    #
    #     if ser1 != "0":
    #         update_apn(c, ser1)
    #         time.sleep(0.5)
    #
    #         with open('/home/pi/apn1.txt', 'w') as f:
    #             f.write('0')
    #
    #         print("Restart Modem")
    #
    #     else:
    #         print("No APN found")
