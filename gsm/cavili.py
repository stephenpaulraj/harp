from sim_modem import Modem, SerialComm

comm = SerialComm(address='/dev/ttyACM0', baudrate=460800, timeout=5, at_cmd_delay=0.1,)
comm.send("ATZ")
comm.send("ATE1")
read = comm.read_lines()
print(read)
if read[-1] != "OK":
    raise Exception("Modem do not respond", read)




