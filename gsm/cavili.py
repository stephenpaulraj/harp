from sim_modem import Modem

device = Modem('/dev/ttyACM0')
status = device.get_sim_status()

print(status)
