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