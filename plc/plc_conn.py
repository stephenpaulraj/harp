import time

from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import encode_ieee, decode_ieee, long_list_to_word, word_list_to_long

f = open('/home/pi/hardwareid.txt', 'r')
data = f.read()
f.close()
print(data)
defaultid=int(data)

c = ModbusClient(host='192.168.3.1', port=502, auto_open=True, auto_close=False , debug=False)

write=0
boolean2=[]
int2=[]
float2=[]
float_l=0
bool_l=0
integer_l=0
ID=""
R=[]
R1=[]
name=[]
alarmID=[]
global Dict
def1="up"
ID=defaultid
Dict = {"HardWareID": ID }
start = time.time()

