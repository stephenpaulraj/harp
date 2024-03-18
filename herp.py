
#!/usr/bin/env python3

import uuid
import numpy as np
import random
import json 
import time
from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import encode_ieee, decode_ieee, \
                              long_list_to_word, word_list_to_long
                              
import ssl
import paho.mqtt.client as mqtt
from datetime import datetime
import thread6

import subprocess
from pyroute2 import IPDB
import json
    
context = ssl.create_default_context()

broker_address= "b-4d9d7a54-2795-4ab2-b1e7-c40ddf1113f7-1.mq.us-east-1.amazonaws.com" # No ssl://
port = 8883
user = "ehashmq1"
password = "eHash@12mqtt34!"

#c = ModbusClient(host='192.168.0.1', port=502, auto_open=True, debug=False)
#c = ModbusClient(host='192.168.0.1', port=502)

global write

global R
R=[]
#global R

#global boolean2
#boolean2=[]

def getmac(command):
    return subprocess.check_output(command, shell=True)
    
def floatC(reg5):
    global f
    f=[]
    s=""
    for i in range(len(reg5)):
        s = [str(ft) for ft in reg5[i]]
        #s=round(s,2)
        a_string = "".join(s)
    
        res=str(a_string)
    
        f.append(res)           
    return(f)                    

def intC(reg91):
    global t
    t=[]
    ss=""
    for i in range(len(reg91)):
        ss = [str(ft) for ft in reg91[i]]
        #s=round(s,2)
        a_string = "".join(ss)
    
        ress=str(a_string)
    
        t.append(ress)           
    return(t)                 


def Cloning(li1):
    li_copy = li1[:]
    return li_copy



def unique(list1):
 
    # initialize a null list
    global unique_list 
    unique_list = []
    #global unique_list
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    # print list
    for x in unique_list:
        print(x)
        

def CountFrequency(my_list):
 
    # Creating an empty dictionary
    freq = {}
   # R=[]
    R.clear()
    for item in my_list:
        if (item in freq):
            freq[item] += 1
        else:
            freq[item] = 1
 
    for key, value in freq.items():
        print("% s : % s" % (key, value))
        R.append(int(value))
        
        #print(a)
        #print(R)

        
        #if(key=='2'):
           # v=v+1
        #if(key=='1'):
            #v1=v1+1
    #print(v1)

def CountIndex(my_list,element):
    global I
    I=[]
    index = my_list.index(element)
    return index
    print(index)
    


def convert_back(bin_num):
    """
    Converts binary string to a float.
    """
    value = 0
    print(type(bin_num))
    n = list(bin_num)

    if n[0] == '1':
        value = value + (2 ** 15)
    if n[1] == '1':
        value = value + (2 ** 14)
    if n[2] == '1':
        value = value + (2 ** 13)
    if n[3] == '1':
        value = value + (2 ** 12)
    if n[4] == '1':
        value = value + (2 ** 11)
    if n[5] == '1':
        value = value + (2 ** 10)
    if n[6] == '1':
        value = value + (2 ** 9)
    if n[7] == '1':
        value = value + (2 ** 8)
    if n[8] == '1':
        value = value + (2 ** 7)
    if n[9] == '1':
        value = value + (2 ** 6)
    if n[10] == '1':
        value = value + (2 ** 5)
    if n[11] == '1':
        value = value + (2 ** 4)
    if n[12] == '1':
        value = value + (2 ** 3)
    if n[13] == '1':
        value = value + (2 ** 2)
    if n[14] == '1':
        value = value + (2 ** 1)
    if n[15] == '1':
        value = value + (2 ** 0)

    print(value)

    return value

def arrange(res):
    global a
    a=[]
    a.append(res[-9])
    a.append(res[-10])
    a.append(res[-11])
    a.append(res[-12])

    a.append(res[-13])
    a.append(res[-14])
    a.append(res[-15])
    a.append(res[-16])
    
    a.append(res[-1])
    a.append(res[-2])
    a.append(res[-3])
    a.append(res[-4])
    
    a.append(res[-5])
    a.append(res[-6])
    a.append(res[-7])
    a.append(res[-8])

    return a
    
def pop(la,number):
    
    #global b
    #b=[]
    if (number==16):
        la=la
    if (number<16):
        del la[number:16]
    
    return la       

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {str(rc)}")

    # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    client.subscribe('web-Alarms')
    client.subscribe('web-hardwarestatus')


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    topic = msg.topic
    print(f"data received from topic: {topic}")
    
    if (topic=="web-hardwarestatus"):
        print("its for Write")
        write=1
        m_decode = str(msg.payload.decode("UTF-8", "ignore"))
        print(f"data type: {type(m_decode)}")
        print(f"data decoded: {m_decode}")

        print("Converting from Json to Object...")
        m_in = json.loads(m_decode)
        print(f"converted data type: {type(m_in)}")
       # SIMCardMobileNumber = str("%s" % m_in['object2'])
        #print("data")
        #print(SIMCardMobileNumber)
        
       # m_in1=json.loads(SIMCardMobileNumber)
        #SIMCardMobileNumber1 =SIMCardMobileNumber[0]
        #print("data1")
        #print(SIMCardMobileNumber1)    
        #data = json.loads()
          
        #order_1_id = m_decode[4]
        #order_2_id = m_decode[4]
        #order_1_id = m_['objects'][0]['StationID']
        #order_2_id = m_in['objects'][1]['parameter']
        #order_3_id = m_in['objects'][2]['value']
        #order_4_id = m_in['objects'][3]['startTimeStamp']
        #total = len(m_in['objects'])
        total=1   
        #print(f"Order #1: {order_1_id}, Order #2: {order_2_id},Total Orders: {total}")
        print(f"converted data: {m_in}")
       # print(order_1_id)
        print('\n')
        
        for key in m_in:
            print(key)

        #print(data['object1']['Description'])
        
        for item in m_in.items():
            print(item)
        
        global nameW    
        nameW=[]
        global addW
        addW=[]
        global datTW
        datTW=[]
        global maskW    
        maskW=[]    
        global tagW
        priceW=""
        price1W=0
        price2W=0
        #n=1
        ID=m_in['HardwareID']
        #name.append(m_in['object']['ParameterName'])
        #add.append(m_in['object']['Address'])
        #datT.append(m_in['object']['DataType'])
        print("HardWareID:")
        print(ID)
        print(type(ID))
        print("DefaultID:")
        print(defaultid)
        print(type(defaultid))
        if (defaultid==ID):
            
            print("Match for this unit for write")
            nameW.append(m_in['object']['ParameterName'])
            addW.append(m_in['object']['Address'])
            datTW.append(m_in['object']['DataType'])
            maskW.append(m_in['object']['Mask'])
            tagW=m_in['object']['Value']

            #for item in m_in.items():
                #data[item]=m_in['object']['ParameterName']
                
             #   price=m_in['object'+str(n)]['ParameterName']
              #  price1=m_in['object'+str(n)]['Address']
               # price2=m_in['object'+str(n)]['DataType']
                #name.append(price)
                #add.append(price1)
                #datT.append(price2)
                #n=n+1
               # if (n<1):
                #    n=n+1    
            #n=n+1
            #item=item+1
            print(nameW)
            print(addW)     
            print(datTW)
            print("mask")
            print(maskW[0])
            
            
            
            
            
            #tag="1"
            
            print(maskW[0])
            bin_datW=""
            
            
            tag_f=0.0
            ad_f=0
            tag_i=0
            #float=0
            
                    
            if (datTW[0]=='2'):
            
                tagB=m_in['object']['Value']
                ad_B=m_in['object']['Address']
                ad_b=int(ad_B)
                tagb=int(tagB)
                ad_b=ad_b-1
                print(tagW)
                
                
                floatW=0
                
                
            if (datTW[0]=='3'):    
            
                tag_f=m_in['object']['Value']
                ad_f=m_in['object']['Address']
                tag_1=float(tag_f)
                ad_1=int(ad_f)
                ad_1=ad_1-1
                #ad_f=
                #tag_f=float(tag_f)
                #ad_f=int(ad_f)
                print("real Value")
                print(tag_1)
                print(type(tag_1))
                print("real address")
                print(ad_1)
                print(type(ad_1))
                floatW=1
            
            if (datTW[0]=='1'):    
            
                tag_i=m_in['object']['Value']
                ad_i=m_in['object']['Address']
                tag_I=int(tag_i)
                ad_I=int(ad_i)
                ad_I=ad_I-1
                #ad_f=
                #tag_f=float(tag_f)
                #ad_f=int(ad_f)
                print("integer Value")
                print(tag_I)
                print(type(tag_I))
                print("Interger address")
                print(ad_I)
                print(type(ad_I))
                floatW=0
            
            #tag="1"
            
            print(maskW[0])
            bin_dat=""
            #float=0
            #global float
            #float=0
            
                    
            #print("binary")    
            #print(bin_dat)    
            #bin_D=convert_back(bin_dat)
            #print("Interger1")
            #print(bin_D)
                
            
            #print("tag")
            #print(tag)
            
            #reg_value=convert_back(bin_dat)
            
            if (datTW[0]=='1'):
            
                write=1        
                print('write single register Integer')
                print('----------\n')
                #r1=""
                for ad in range(1):
                    
                    regs_l1 = c.read_holding_registers(ad_I, 1)
                    integer5=int(regs_l1[0])
                    print("Register value")
                    print(integer5)
                    
                    print("new")
                    #print(new)
                    #for ad in range(1):
                    #is_ok = c.write_single_register(ad, bit)
                    is_ok = c.write_single_register(ad_I,  tag_I)                
                    write=0
                    time.sleep(1)

            if (datTW[0]=='2'):
            
                write=1 
                print('write single register Boolean')
                print('----------\n')
                r1=""
                for ad in range(1):
                    
                    regs_l = c.read_holding_registers(ad_b, 1)
                    integer=int(regs_l[0])
                    print("Register value")
                    print(integer)

                    binary = bin(integer)
                #print(binary)
                    regs_1_bin=str(format(integer,'016b'))
                    print(regs_1_bin)
                    
                    
                    
                    global res
                    res=[]
                    
                    for x in range(16):
                        res.append(regs_1_bin[x])
                #print(res)
                    print(f'Stationary List: {res}')
                    print(res)
                    
                    
                    r1=res[0]+res[1]+res[2]+res[3]+res[4]+res[5]+res[6]+res[7]+res[8]+res[9]+res[10]+res[11]+res[12]+res[13]+res[14]+res[15]
                    print("last")
                    print(r1)
                    
                    if (maskW[0]=='256'):
                    #bin_dat="0000000"+tag+"00000000"
                        res[7]=tagb
                    if (maskW[0]=='512'):
                    #bin_dat="000000"+ tag+ "000000000"
                        res[6]=tagb
                    if (maskW[0]=='1024'):
                    #bin_dat="00000"+tag+ "0000000000"
                        res[5]=tagb
                    if (maskW[0]=='2048'):
                    #bin_dat="0000"+tag+ "00000000000"
                        res[4]=tagb
                    
                    if (maskW[0]=='4096'):
                    #bin_dat="000"+ tag+  "000000000000"
                        res[3]=tagb
                    if (maskW[0]=='8192'):
                    #bin_dat="00"+tag+"0000000000000"
                        res[2]=tagb
                    if (maskW[0]=='16384'):
                    #bin_dat="0" + tag+ "00000000000000"
                        res[1]=tagb
                    if (maskW[0]=='32768'):
                    #bin_dat=tag+"000000000000000"
                        res[0]=tagb
                    
                    if (maskW[0]=='1'):
                    #bin_dat="000000000000000"+tag
                        res[15]=tagb
                    if (maskW[0]=='2'):
                    #bin_dat="00000000000000"+ tag+"0"
                        res[14]=tagb
                    if (maskW[0]=='4'):
                    #bin_dat="0000000000000" +tag+ "00"
                        res[13]=tagb
                    if (maskW[0]=='8'):
                    #bin_dat="000000000000" + tag + "000"
                        res[12]=tagb
                    
                    if (maskW[0]=='16'):
                    #bin_dat="00000000000" +tag+ "0000"
                        res[11]=tagb
                    if (maskW[0]=='32'):
                    #bin_dat="0000000000" + tag+ "00000"    
                        res[10]=tagb
                    if (maskW[0]=='64'):
                    #bin_dat="000000000"+ tag+ "000000"
                        res[9]=tagb
                    if (maskW[0]=='128'):
                    #bin_dat="00000000" +tag+ "0000000"
                        res[8]=tagb
                    r1_new=""    
                    
                    r1_new=str(res[0])+str(res[1])+str(res[2])+str(res[3])+str(res[4])+str(res[5])+str(res[6])+str(res[7])+str(res[8])+str(res[9])+str(res[10])+str(res[11])+str(res[12])+str(res[13])+str(res[14])+str(res[15])
                    
                    print("update")
                    print(r1_new)
                    convert_back(r1_new)
                    reg_value=convert_back(r1_new)
                
                    new=0
                    ad=0
                    
                    #new=(bin_D | integer)
                    
                    #if (tag==0):
                     #   new=(bin_D&integer)
                    #else:     
                    #    new=(bin_D & integer)
                    #is_ok = c.write_single_register(ad, bit)
                    #ad=int(add[0])
                    print("new")
                    print(new)
                    #for ad in range(1):
                    #is_ok = c.write_single_register(ad, bit)
                    is_ok = c.write_single_register(ad_b,  reg_value)
                        #write_single_register(reg_addr, reg_value)
                    write=0  
                    time.sleep(1)  
                        #if is_ok:
                        #    print('register #%s: write to %s' % (ad, reg_value))
                       # else:
                          #  print('register #%s: unable to write %s' % (ad, reg_value))
                         #   print('register #%s: unable to write %s' % (ad, reg_value))
                    #time.sleep(0.5)
                    #reg_value=reg_value+1
                    
            if (datTW[0]=='3'): 
                write=1
                print("Write single real value")
                c.write_float(ad_1,[tag_1])            
                write=0
                time.sleep(1)      
        #else:
            #write=0
            #time.sleep(3)
          
      
    if (topic=="web-Alarms"):
        print("its for Adress amapping ")
    
        m_decode = str(msg.payload.decode("UTF-8", "ignore"))
        print(f"data type: {type(m_decode)}")
        #print(f"data decoded: {m_decode}")
        
        print("Converting from Json to Object...")
        m_in1 = json.loads(m_decode)
        
        ID=m_in1['HardwareID']
        #name.append(m_in['object']['ParameterName'])
        #add.append(m_in['object']['Address'])
        #datT.append(m_in['object']['DataType'])
        print("HardWareID:")
        print(ID)
        print(type(ID))
        print("DefaultID:")
        print(defaultid)
        print(type(defaultid))
        
        if (defaultid==ID):
        
            print("Match for this unit:")
            
            with open("/home/pi/sample.json", "w") as outfile:
                json.dump(m_in1, outfile)
            print(m_in1)
            
        #print(f"converted data type: {type(m_in1)}")
        #total=1
        else: 
            print("Not matching for this unit")
            
        try:
            #f = open('student.csv')
            with open('/home/pi/sample.json', 'r') as openfile:
                m_in = json.load(openfile)
                
                print("After read from Memory")
            print(m_in)
            print(type(m_in))
            
            #print(f"Order #1: {order_1_id}, Order #2: {order_2_id},Total Orders: {total}")
            print(f"converted data: {m_in}")
           # print(order_1_id)
            print('\n')
            
            global m
            m=0
            for key in m_in:
                print(key)
                m=m+1
            
            print("key count or no of parameters saved")
            print(m)    
            print('\n')

            for item in m_in.items():
                print(item)
            global datT
            datT=[]
            global name
            name=[]
            global alarmID
            alarmID=[]
            name=[]
            add=[]
            #datT=[]  
            #alarmID=[]     
            price=""
            price1=""
            price2=""
            price3=""
            n=0
            
            for item in m_in.items():
                #data[item]=m_in['object']['ParameterName']
                print(item)
                
            for item in m_in.items():
                #data[item]=m_in['object']['ParameterName']
                
                price=m_in['object'+str(n)]['ParameterName']
                price1=m_in['object'+str(n)]['Address']
                price2=m_in['object'+str(n)]['DataType']
                price3=m_in['object'+str(n)]['AlarmID']
                name.append(price)
                add.append(price1)
                datT.append(price2)
                alarmID.append(price3)
                #n=n+1
                if (n<(m-2)):
                    n=n+1    
            #n=n+1
            #item=item+1
            name= name[:-1]
            add=add[:-1]
            datT=datT[:-1]
            alarmID=alarmID[:-1]
            
            print()
            #print("parameter")
            #print(name)
            print("Address to scan")
            print(add)
            print("Data types to scan")    
            print(datT)
            #print("Individual Alarm IDs")    
            #print(alarmID)
            #print(datT[0])
            #res = [datT[0]]
            #print(res)
            #test_dict = {'gfg': 1, 'is': 2, 'best': 3, 'for': 2, 'CS': 2}
            #print(R)
            print()
            
            #CountFrequency(datT)
            CountFrequency(add)
            #CountIndex(add,str(12))
            global index1
            index1=[]
            global index2
            index2=[]
            q=0
            unique(add)
            print("Different address  need to scan")
            print(unique_list)
            #unique(datT)
            #print("Different Data Types")
            global res5
            
            res5 = [eval(i) for i in unique_list]
            
            res5 = list(map(lambda x: x - 1, res5))
            print(res5)
            
            print(res5[1]) 
            print(res5[2]) 
            #unique(datT)
            #print("Different Data Types")
            #print(unique_list)

            #l=CountIndex(add,'12')
            l=CountIndex(add,unique_list[3])
            print("index")
            print(l)
            #i=0
            # use of range() to define a range of values
            values1 = range(len(unique_list))

        # iterate from i = 0 to i = 3
            for i in values1:
                print(i)
                l=CountIndex(add,unique_list[i])
                index1.append(l)
            for j in index1:
                res=""
                #print(datT[0])
                res =datT[j]
                index2.append(res)
                #print(k)
            print(index2)
            #global res2
            res2 = [eval(i) for i in index2]
            print(res2)
            #for key in add:
                #print(key)
                
                #index1.append(CountIndex(add,unique_list[x]))
                #i=CountIndex(add,unique_list[q])
                #index1.append(i)
                #index_1.extend(i)
                #CountIndex(add,'12')
                #print(i)
                #q=q+1
            #print("Total of new tags has to be defined")
            #print(m)
            print("Starting point of each new address")
            print(index1)    
            #print(v)
            print("Each address is present for how many times starting from first add") 
            print(R)
            print(R[0])
            print(R[1])
            global R1
            R1=[]
            for i in range(len(R)):
                if R[i]> 1:
                    R1.append(R[i])
            print("boolean adress freq")
            print(R1)
            print("Total no of new tags has to be defined")
            print(m)   
            #unique(datT)
            print("Which data type is present at the starting pos for each address")
            #len=0   
            length=len(unique_list)
            print("Need to scan no of adress")
            print(length) 
            
            # trying to parse the diff adress accoring to their data types
            #bool= 
            global float2
            float2=[]
            global boolean2
            #boolean1=[]
            global int2
            #int2=[]
            u16=0

            length2=len(res5)
            float2.clear()
            boolean2.clear()
            int2.clear()

            for i in range(length):
            #for k in len(res2):
                if(res2[i] == 3):
                    print("its Float data")
                    float2.append(res5[i])
                    
                if(res2[i] == 2):
                    print("its Boolena  data")
                    boolean2.append(res5[i])
                    
                if(res2[i] == 1):
                    print("its Integer  data")
                    int2.append(res5[i])
             
                #if(k == 1):
                #    print("Float data so it will take 4 address starting from") #+ str( add[i]))
                #if(k == 2):
                #    print("Boolean data so it will take 1 address starting from") # str( add[i])+" and do conversion")
                #if(k == 3):
                #    print("Float data so it will take 4 address starting from") #+ str(add[i]))
                #else:
             #    print("No valid data type")
            global float_l
            float_l=len(float2)
            global bool_l
            bool_l=len(boolean2)
            global integer_l
            integer_l=len(int2)
            
            print("no of float data")      
            print(float_l)
            
            print("no of boolean data")
            print(bool_l)
            
            print("no of integer data")
            print(integer_l)
        #ID=m_in['HardwareID']
        #name.append(m_in['object']['ParameterName'])
        #add.append(m_in['object']['Address'])
        #datT.append(m_in['object']['DataType'])
        #print("HardWareID:")
        #print(ID)
        #print(type(ID))
        #print("DefaultID:")
        #print(defaultid)
        #print(type(defaultid))
        #if (defaultid==ID):
        
            #print("Match for this unit:")
                
        except FileNotFoundError:
        
            print('File does not exist')
            #os.system("python3 /home/pi/herp.py")
            
    #else:
        #try:
        #with open('/home/pi/sample.json', 'r') as openfile:
        #except
    # Reading from json file
        #    m_in = json.load(openfile)
            
        
            

# The callback for when a PUBLISH message is sent to the server.
def on_publish(client, userdata, mid):
    print(f"data published with message id: {mid}")
    print('\n')

# init modbus client
#c = ModbusClient(debug=False, auto_open=True)


run = True
###########################################################################################################################################
if __name__ == '__main__':
    #client = mqtt.Client()
    #client.on_connect = on_connect
    #client.on_message = on_message
    f = open('/home/pi/hardwareid.txt', 'r')
    data = f.read()
    f.close()
    print(data)
    defaultid=int(data)
    
    client = mqtt.Client(str(uuid.uuid1())) #create new instance
    #client._connect_timeout = 30.0
    client.username_pw_set(user, password=password) #set username and password
     

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    client.tls_set_context(context=context)
    client.connect(broker_address, port=port, keepalive=1000)

    #client.connect(host=Config.MQTT_HOST, port=Config.MQTT_PORT, keepalive=60)
    client.loop_start()
    
    c = ModbusClient(host='192.168.3.1', port=502, auto_open=True, auto_close=False , debug=False)
    
    #print(boolean2)
   # print(bool_l)
    #new_var = on_message()  
    write=0
    boolean2=[]
    int2=[]
    #boolean2 = [0] * 2
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
    #Dict = {"HardWareID": 8}
    Dict = {"HardWareID": ID }
    start = time.time()
    
    while True:

        
    # read 10 registers at address 0, store result in regs list
        
        #client.on_message = on_message
        #client.on_connect = on_connect
        #client.on_message = on_message
        
        if time.time() - start > 10:
            start = time.time()
        
            ip = IPDB()
            state = ip.interfaces.eth1.operstate
            print(state)
            ip.release()
     
            command = "cat /sys/class/net/eth1/operstate"
            interface= ((getmac(command)).decode('ascii'))
            #print("Interface for LAN")
            #print(interface)
            print("ID:")
            print(ID)
            print(boolean2)
            #print(boolean2[0])
            #print(boolean2[1])
            print(float2)
            print(int2)

            print(float_l)
            print(bool_l)
            print(integer_l)
            print(R)
            print(R1)
            #print(name)
            #print(alarmID)
            
            #print(res2)
            #regs_l=0
            #bool_l=bool_l+1
            l=bool_l
            #regs_5=[]
            #a=boolean2[0]
            #b=boolean2[1]
            #if (bool_l>0):      
            #for i in range(bool_l):
            
            Float=[]
            #myList=[]
            #f=""
            
            for i in  range(float_l):
                
                #f=c.read_float(float[i],1)
                #print(round(f,2)
                Float.append(c.read_float(float2[i],1))        
                #float_1 = c c.read_float(float[i],1) 
                #float_2 = c.read_float(7,1)
                #float_3 = c.read_float(9,1)
                #float_4 = c.read_float(11,1)
            print(Float)
            Float=floatC(Float)
            print(Float)
            #Float = list(np.around(np.array(Float),2))
            #round(float(i), 2) for i in Float  
            #print(type(Float))
            #print(Float)
            #value1=str(round(float_1[0],2))
            #value2=str(round(float_2[0],2))
            #value3=str(round(float_3[0],2))
            #value4=str(round(float_4[0],2))
            #value1=str(round(Float[0],2))

            value1=0
            value2=0
            value3=0
            value4=0
            reg5=[]
            Integer=[]
            
            if (len(int2)!=0):
                for i in range(integer_l):
                    Integer.append(c.read_holding_registers(int2[i], 1)) 
                #regs_l=c.read_holding_registers(boolean2[0], 1)
                #regs_l1=c.read_holding_registers(boolean2[1], 1)
                #regs_5.extend(regs_l)
                #regs_5.append(boolean2[i])
                Integer=intC(Integer)
                print("Integer Data")
                print(Integer)
                
            #list1.extend(list2)
            if (len(boolean2)!=0):
                for i in range(len(boolean2)):
                    reg5.append(c.read_holding_registers(boolean2[i], 1)) 
                #regs_l=c.read_holding_registers(boolean2[0], 1)
                #regs_l1=c.read_holding_registers(boolean2[1], 1)
                #regs_5.extend(regs_l)
                #regs_5.append(boolean2[i])
                print("Data Boolean")
                print(reg5)
                print(len(reg5))
                #map(int, reg5)
                reg6=[]
                for i in range(len(reg5)):
        
                    s = [str(integer) for integer in reg5[i]]
                    a_string = "".join(s)

                    res=int(a_string)
                    
                    reg6.append(res)
                
                #s1 = [str(integer) for integer in reg5[1]]
                #a_string1 = "".join(s1) 
                #res1=int(a_string1)
                #print(res)
                print(reg6)
                #res=448
            #print(regs_5)
                #regs_l=[1920]
                #regs_l=[348]
                #regs_l1=[448]
                #print(regs_l)
                #print(regs_l1)
                integer=[]
                for i in range(len(reg6)):
                    #i=""
                                           
                    integer.append(reg6[i])
                #integer=bin(reg6[0])
                print("Integer List")
                print(integer[0])
                
                #integer=int(regs_l[0])

                #int1=484
        # if success display registers
            #if regs_l:
             #   print('reg ad #0 to 9: %s' % regs_l)
              #  print(regs_l[0])
            #else:
            #    print('unable to read registers')
            
        # sleep 2s before next polling
            
        #regs_1_bin=format(integer,'b')
        #print(regs_1_bin)
                
                #time.sleep(2)
                binary=[]
                #for i in range(len(integer)):
               
                    #binary.append(bin(integer[i]))
              
                #print(binary)


                int1=484
                bi1=bin(int1) 

        #print(binary)=str(format(integer,'016b')
                for i in range(len(integer)):
                             
                    regs_2_bin=str(format(integer[i],'016b'))
                    binary.append(regs_2_bin)

                print(binary)

                regs_1_bin=str(format(int1,'016b'))
                print(regs_1_bin)
                #print(regs_1_bin)
        #print(format(x, '08b'))
        #print(format(x, '010b'))
        
        #print(format(x, '016b'))
        #a=format(x, '016b')
        
                #print(regs_1_bin)
        #print(a[7])
         #res[]
                print(len(regs_1_bin))
                print(len(binary[0]))
                res_final=[]
                for i in range(len(binary)):
                    res10=[]
                    for x in range(16):
                        res10.append(binary[i][x])
            #print(res)
                    print(f'Stationary List: {res}')
                    print(res10)
                    
                    res_final.append(res10)
                print("Binary form of all boolean data")
                print(res_final)  
                
                #-----------------------------------------#####
                
                #print("first adress boolean")
                #print(res_final[0])
                print()
                print("Arranged")
                for i in range(len(res_final)):
                    res_final[i]=arrange(res_final[i])
                
                for i in range(len(res_final)):
                    res_final[i]=pop(res_final[i],R1[i])            
                
                for i in range(len(res_final)):
                    print(res_final[i])
                
                res_finalF=[]
                for i in range(len(res_final)):
                    res_finalF=res_finalF+(res_final[i])
                
                print("All Boolean")    
                print(res_finalF)   
                print("All Integer")
                print(Integer)
                print("All Float")
                print(Float)
                print()
                #final=[]
                #final=res_final[0]+res_final[1]+Float
                #print("All values")
                #print(final)
                #final=[]
                #final=Float+res_finalF+Integer
                final=Integer+res_finalF+Float
                #final=Float+res_final[0]+res_final[1]+res_final[2]+Integer
                print(final)    
                
                #time.sleep(0.1)  
                
                n=1
                #Dict = {"HardWareID": 1}
                for i in range(len(name)):
                    Dict["object"+str(i)]={}
                
                for i in range(len(name)):
                    Dict["object"+str(i)]['Description'] = "111"
                    Dict["object"+str(i)]['ParameterName'] = name[i]
                    Dict["object"+str(i)]['value'] = final[i]
                    Dict["object"+str(i)]['AlarmID'] = alarmID[i]
        
                
                print("\nAfter adding dictionary Dict1")
                #print(Dict)
                
                
                res=[]
                for x in range(16):
                    res.append(regs_1_bin[x])
        #print(res)
                #print(f'Stationary List: {res}')
                #print(res)
                #res=res_final[0]    
                tags_bool=0
                for i in range(len(R1)):
                    tags_bool=tags_bool+R1[i]
                print("Boolen tags no")
                print(tags_bool)
                
                final=[0 for i in range(len(name))]
                print(final)            
               
                
            #print("Latest payload")   
            #print(Dict)
            #json_object = json.dumps(Dict)
            payload=json.dumps(Dict)
            
            #for i in range(len(interface)):
            #    if interface[i] == def1[i]:
            #        print("PLC CONNCECTED")
            #        client.publish('iot-data3', payload=payload, qos=1, retain=True)
            #        break
            #    else:
            #        print("PLC NOT CONNECTED")

            if (state=="UP"):
                print("PLC CONNECTED")
                #client.publish('iot-data3', payload=payload, qos=1, retain=True)
            else:
                print("PLC NOT CONNECTED");
                
        #time.sleep(10)
        #final=
    #client.loop_stop()
    #client.disconnect()

    #time.sleep(5)
























