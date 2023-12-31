import json
from pyModbusTCP.utils import encode_ieee, long_list_to_word


def write_float(client, address, floats_list):
    b32_l = [encode_ieee(f) for f in floats_list]
    b16_l = long_list_to_word(b32_l)
    return client.write_multiple_registers(address, b16_l)


def get_hw_id():
    with open('/home/pi/hardwareid.txt', 'r') as f:
        HwId = f.read()
    return int(HwId)


def process_web_hw_status(msg, c, log):
    m_decode = str(msg.payload.decode("UTF-8", "ignore"))
    data = json.loads(m_decode)
    log.info(f'From Write fn RAW data - {data}')
    ID = data['HardwareID']
    log.info(f'From Write fn HW- {ID}')
    log.info(f'From local {get_hw_id()}')

    if get_hw_id() == ID:
        if data['object']['DataType'] == "1":
            tag_i = data['object']['Value']
            ad_i = data['object']['Address']
            tag_I = int(tag_i)
            ad_I = int(ad_i)
            ad_I = ad_I - 1
            c.write_single_register(ad_I, tag_I)
        if data['object']['DataType'] == '3':
            tag_i = data['object']['Value']
            ad_i = data['object']['Address']
            tag_1 = float(tag_i)
            ad_1 = int(ad_i)
            ad_1 = ad_1 - 1
            write_float(c, ad_1, [tag_1])

        if data['object']['DataType'] == '2':
            tagB = data['object']['Value']
            ad_B = data['object']['Address']
            ad_b = int(ad_B)
            tagb = int(tagB)
            ad_b = ad_b - 1

            regs_l = c.read_holding_registers(ad_b, 1)
            integer = int(regs_l[0])

            binary = bin(integer)
            regs_1_bin = str(format(integer, '016b'))

            res = []
            for x in range(16):
                res.append(regs_1_bin[x])

            r1 = res[0] + res[1] + res[2] + res[3] + res[4] + res[5] + res[6] + res[7] + res[8] + res[9] + res[10] + \
                 res[11] + res[12] + res[13] + res[14] + res[15]

