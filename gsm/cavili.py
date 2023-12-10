from sim_modem import Modem, SerialComm

# modem = Modem('/dev/ttyACM0')
comm = SerialComm(address='/dev/ttyACM0')
comm.send("ATZ")
comm.send("ATE1")
read = comm.read_lines()
print(read)
if read[-1] != "OK":
    raise Exception("Modem do not respond", read)




