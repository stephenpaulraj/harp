from sim_modem import Modem, SerialComm

modem = Modem('/dev/ttyACM0', debug=True)
status = modem.get_sim_status()

print(status)
