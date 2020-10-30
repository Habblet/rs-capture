import pyshark
import datetime
import os

from config import *
from process_book import file_to_wikitext


print('Program started. Preparing for capture...')
_ = os.system('')

DEBUG = True

date = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')

capture = pyshark.LiveCapture(interface=INTERFACE)
# capture.set_debug()

outfilename = os.path.join(DIR_CAPTURES, date + '.cap')
output = ''

stream_index = None
source_ip = None
found_book = False

for n,packet in enumerate(capture.sniff_continuously()):
    if n == 0:
        print('Program ready for capture. %sOpen a book.%s' % ('\33[36m', '\33[0m'))
    if not hasattr(packet, 'ip') or packet.ip.dst != DST_IP:
        continue
    if hasattr(packet, 'tcp') and hasattr(packet.tcp, 'payload'):
        if (':5d:52' * 4) in packet.tcp.payload:
            found_book = True
            stream_index = packet.tcp.stream
            source_ip = packet.ip.src
            print('Book stream found.')
            output += str(packet.tcp.payload)
        elif found_book and packet.tcp.stream == stream_index and packet.ip.src == source_ip:
            if any(i in packet.tcp.payload for i in [':5d:54' * 4]):#, ":5d:53" * 4]):
                print('Book end found.')
                output += ':' + str(packet.tcp.payload)
                capture.close()
                break
            else:
                output += ':' + str(packet.tcp.payload)
                pass

with open(outfilename, 'wb') as o:
    b = [bytes.fromhex(i) for i in output.split(':')]
    o.write(b''.join(b))
    print('Saved filtered stream to file. Processing...')

file_to_wikitext(outfilename, debug=DEBUG)
