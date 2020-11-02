import pyshark
import datetime
import os
import re
import json

from config import *


print('Program started. Preparing for capture...')
_ = os.system('')

def msg_to_hex(msg):
    return ':'.join(['{0:02x}'.format(ord(char)) for char in msg])

def find_pos(payload, msg):
    ret = [m.end() for m in re.finditer(msg, payload)]
    return ret

pre_msg_bytes = '6d:00:00:00:00:00:'

msg_attempt = pre_msg_bytes + msg_to_hex('You pick the master farmer\'s pocket.')
msg_fail = pre_msg_bytes + msg_to_hex('You fail to pick the master farmer\'s pocket.')
msg_success = pre_msg_bytes + msg_to_hex('You steal ')
msg_multiple = pre_msg_bytes + msg_to_hex('Your lightning-fast reactions allow you to steal ')

multiple_2 = msg_to_hex('double')
multiple_3 = msg_to_hex('triple')
multiple_4 = msg_to_hex('quadruple')

messages = [msg_attempt, msg_fail, msg_success, msg_multiple]

capture = pyshark.LiveCapture(interface=INTERFACE, display_filter='not tcp.analysis.retransmission')
# capture.set_debug()

stream_index = None

data = {'seeds': {}, 'fail': 0, 'success': 0, 'multiple_2': 0, 'multiple_3': 0, 'multiple_4': 0}

log_name = 'master farmer log.json'
jsonfilename = os.path.join(DIR_THIEV_LOGS, log_name)

if os.path.exists(jsonfilename):
    jsonFile = open(jsonfilename, "r")
    data = json.load(jsonFile)
    jsonFile.close()

try:
    for n,packet in enumerate(capture.sniff_continuously()):
        if n == 0:
            print('Program ready for capture. %sStart pickpocketing.%s' % ('\33[36m', '\33[0m'))
        if n % 100 == 0:
            print(n)
        if not hasattr(packet, 'ip') or packet.ip.dst != DST_IP:
            continue
        if hasattr(packet, 'tcp') and hasattr(packet.tcp, 'payload'):
            payload = str(packet.tcp.payload)
            # print(stream_index)
            if stream_index is None and any(msg in payload for msg in messages):
                stream_index = packet.tcp.stream
            if packet.tcp.stream == stream_index and any(msg in payload for msg in messages):
                temp_data = {'seeds': {}, 'fail': 0, 'success': 0, 'multiple_2': 0, 'multiple_3': 0, 'multiple_4': 0}
                succ_pos = find_pos(payload, msg_success)
                for pos in succ_pos:
                    pos += 1
                    seed_num_str = payload[pos:pos+5]
                    if seed_num_str == msg_to_hex('a '):
                        seed_num = 1
                    elif seed_num_str == msg_to_hex('an'):
                        seed_num = 1
                        pos += 3
                    else:
                        seed_num = int(chr(int(seed_num_str[:2], 16)))
                    pos += 5
                    seed_name = ''
                    while payload[pos:pos+15].find(msg_to_hex(' seed')) == -1:
                        # print(payload[pos:pos+15])
                        seed_name += payload[pos:pos+3]
                        pos += 3
                    seed_name = bytearray.fromhex(seed_name.replace(':','')).decode().lower()
                    print(seed_num, seed_name, end='')
                    if seed_name in data['seeds']:
                        print('', data['seeds'][seed_name]['cases'], n)
                    else:
                        print('')
                    if seed_name not in temp_data['seeds']:
                        temp_data['seeds'][seed_name] = {'cases': 1, 'amount': seed_num}
                    else:
                        temp_data['seeds'][seed_name]['cases'] += 1
                        temp_data['seeds'][seed_name]['amount'] += seed_num
                mult_pos = find_pos(payload, msg_multiple)
                for pos in mult_pos:
                    if payload[pos:pos+18].find(multiple_2) != -1:
                        temp_data['multiple_2'] += 1
                        continue
                    if payload[pos:pos+18].find(multiple_3) != -1:
                        temp_data['multiple_3'] += 1
                        continue
                    if payload[pos:pos+27].find(multiple_4) != -1:
                        temp_data['multiple_4'] += 1
                
                for seed_name in temp_data['seeds']:
                    if seed_name in data['seeds']:
                        data['seeds'][seed_name]['cases'] += temp_data['seeds'][seed_name]['cases']
                        data['seeds'][seed_name]['amount'] += temp_data['seeds'][seed_name]['amount']
                    else:
                        data['seeds'][seed_name] = {
                            'cases': temp_data['seeds'][seed_name]['cases'],
                            'amount': temp_data['seeds'][seed_name]['amount']
                        }
                data['success'] += len(succ_pos)
                data['fail'] += payload.count(msg_fail)
                data['multiple_2'] += temp_data['multiple_2']
                data['multiple_3'] += temp_data['multiple_3']
                data['multiple_4'] += temp_data['multiple_4']
except KeyboardInterrupt:
    print('Closing program manually. Output:\n')
except:
    print('An error has occurred.')
    raise
finally:
    parsed = json.dumps(data, indent=2)
    print(parsed)
    date = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    with open(os.path.join(DIR_THIEV_LOGS, log_name), 'w') as f:
        f.write(parsed)
