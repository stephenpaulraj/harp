from sim_modem import Modem
import time
import os

modem = Modem('/dev/ttyUSB2')


def get_ping(self) -> str:
    if self.debug:
        self.comm.send("AT+CPING=\"8.8.8.8\",1,5,64,1000,20000,255")
        read = self.comm.read_lines()
        if read[-1] != "OK":
            print("Ping not Ok")
            # raise Exception("Unsupported command")

        # print("Sending: AT+CGMI")

    self.comm.send("AT+CPING=\"8.8.8.8\",1,5,64,1000,20000,255")
    read = self.comm.read_lines()

    if self.debug:
        print("Device responded: ", read)
        print(read)
        if (read == "ERROR"):
            self.comm.send("AT+CFUN=0")
            time.sleep(0.5)
            self.comm.send("AT+CFUN=1")
            time.sleep(1)
    # ['AT+CGMI', 'SIMCOM INCORPORATED', '', 'OK']

    # if read[-1] != "OK":
    #   raise Exception("Command failed")
    return read[1]


def update_apn(self, APN: str) -> str:
    if self.debug:
        self.comm.send('AT+CGDCONT=1,\"IP\",\"' + APN + '\"')
        read = self.comm.read_lines()
        if read[-1] == "OK":
            print("APN UPDATE is OK")
            # raise Exception("Unsupported command")

        # print("Sending: AT+CGMI")
    self.comm.send('AT+CGDCONT=1,\"IP\",\"' + APN + '\"')
    read = self.comm.read_lines()
    print(read)
    time.sleep(1)

    self.comm.send("AT+CFUN=0")
    # time.sleep(0.5)
    read = self.comm.read_lines()
    self.comm.send("AT+CFUN=1")
    # time.sleep(0.5)
    read = self.comm.read_lines()
    # time.sleep(1)
    if self.debug:
        print("Device responded: ", read)
    # ['AT+CGMI', 'SIMCOM INCORPORATED', '', 'OK']

    # if read[-1] != "OK":
    #   raise Exception("Command failed")


def restart_modem(self) -> str:
    self.comm.send("AT+CFUN=0")
    # time.sleep(0.5)
    read = self.comm.read_lines()
    self.comm.send("AT+CFUN=1")
    # time.sleep(0.5)
    read = self.comm.read_lines()
    # time.sleep(1)
    if self.debug:
        print("Device responded: ", read)
    # ['AT+CGMI', 'SIMCOM INCORPORATED', '', 'OK']

    # if read[-1] != "OK":
    #   raise Exception("Command failed")
    return read[1]


def connect_sim_com():
    pass


def main():
    while True:

        sim = modem.get_sim_status()

        print(sim)

        sms = modem.get_sms_list()

        print(sms)

        res = len([ele for ele in sms if isinstance(ele, dict)])

        print(res)

        for i in range(res):

            sms1 = sms[i]
            message = sms1.get('message')

            print(message)
            # mess_pre=
            if (message[0:3] == "APN"):
                # if (message == "APN airtelgprs.com"):

                print("APN found")
                apn = message[4:]
                print(apn)

                modem.update_apn(apn)

                # modem.send_sms(number, 'APN received') # send response back to the user

                # save the apn in text file and update in modem
                # update apnfunction
                # delete remaining messages
            else:
                print("No APN in saved messages")


if __name__ == '__main__':
    main()
