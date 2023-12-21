import json
import time

from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import encode_ieee, long_list_to_word


def write_float(client, address, floats_list):
    b32_l = [encode_ieee(f) for f in floats_list]
    b16_l = long_list_to_word(b32_l)
    return client.write_multiple_registers(address, b16_l)

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
    a = []
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
def process_web_hw_status(msg):
    c = ModbusClient(host='192.168.3.1', port=502, auto_open=True, debug=False)
    m_decode = str(msg.payload.decode("UTF-8", "ignore"))
    data = json.loads(m_decode)
    total = 1
    global nameW
    nameW = []
    global addW
    addW = []
    global datTW
    datTW = []
    global maskW
    maskW = []
    global tagW
    priceW = ""
    price1W = 0
    price2W = 0
    # n=1
    ID = data['HardwareID']

    if self.get_hw_id() == ID:
        nameW.append(data['object']['ParameterName'])
        addW.append(data['object']['Address'])
        datTW.append(data['object']['DataType'])
        maskW.append(data['object']['Mask'])
        tagW = data['object']['Value']

        bin_datW = ""

        tag_f = 0.0
        ad_f = 0
        tag_i = 0

        if datTW[0] == '2':
            tagB = data['object']['Value']
            ad_B = data['object']['Address']
            ad_b = int(ad_B)
            tagb = int(tagB)
            ad_b = ad_b - 1
            floatW = 0

        if datTW[0] == '3':
            tag_f = data['object']['Value']
            ad_f = data['object']['Address']
            tag_1 = float(tag_f)
            ad_1 = int(ad_f)
            ad_1 = ad_1 - 1
            floatW = 1

        if datTW[0] == '1':
            tag_i = data['object']['Value']
            ad_i = data['object']['Address']
            tag_I = int(tag_i)
            ad_I = int(ad_i)
            ad_I = ad_I - 1
            floatW = 0

        bin_dat = ""

        if datTW[0] == '1':
            write = 1
            for ad in range(1):
                regs_l1 = c.read_holding_registers(ad_I, 1)
                integer5 = int(regs_l1[0])
                is_ok = c.write_single_register(ad_I, tag_I)
                write = 0
                time.sleep(1)

        if datTW[0] == '2':
            write = 1
            r1 = ""
            for ad in range(1):
                regs_l = c.read_holding_registers(ad_b, 1)
                integer = int(regs_l[0])

                binary = bin(integer)
                regs_1_bin = str(format(integer, '016b'))

                global res
                res = []

                for x in range(16):
                    res.append(regs_1_bin[x])
                r1 = res[0] + res[1] + res[2] + res[3] + res[4] + res[5] + res[6] + res[7] + res[8] + res[9] + res[
                    10] + res[11] + res[12] + res[13] + res[14] + res[15]

                if maskW[0] == '256':
                    res[7] = tagb
                if maskW[0] == '512':
                    res[6] = tagb
                if maskW[0] == '1024':
                    res[5] = tagb
                if maskW[0] == '2048':
                    res[4] = tagb

                if maskW[0] == '4096':
                    res[3] = tagb
                if maskW[0] == '8192':
                    res[2] = tagb
                if maskW[0] == '16384':
                    res[1] = tagb
                if maskW[0] == '32768':
                    res[0] = tagb

                if maskW[0] == '1':
                    res[15] = tagb
                if maskW[0] == '2':
                    res[14] = tagb
                if maskW[0] == '4':
                    res[13] = tagb
                if maskW[0] == '8':
                    res[12] = tagb

                if maskW[0] == '16':
                    res[11] = tagb
                if maskW[0] == '32':
                    res[10] = tagb
                if maskW[0] == '64':
                    res[9] = tagb
                if maskW[0] == '128':
                    res[8] = tagb
                r1_new = ""

                r1_new = str(res[0]) + str(res[1]) + str(res[2]) + str(res[3]) + str(res[4]) + str(res[5]) + str(
                    res[6]) + str(res[7]) + str(res[8]) + str(res[9]) + str(res[10]) + str(res[11]) + str(
                    res[12]) + str(res[13]) + str(res[14]) + str(res[15])


                convert_back(r1_new)
                reg_value = convert_back(r1_new)

                new = 0
                ad = 0
                is_ok = c.write_single_register(ad_b, reg_value)
                write = 0
                time.sleep(1)

        if datTW[0] == '3':
            write = 1
            write_float(c, ad_1, [tag_1])
            write = 0
            time.sleep(1)