import os


# Network
DST_IP = ''  # your IPv4 address
INTERFACE  = '7'  # The network interface "name"

# Directories
DIR_OUT = os.path.join('..', 'out')
DIR_CAPTURES = os.path.join('..', 'captures')
DIR_BOOKS = os.path.join(DIR_OUT, 'books')
DIR_THIEV_LOGS = os.path.join(DIR_OUT, 'thieving_logs')

# Other
LANGUAGE = 'en-GB'  # language of the game client
ENCODING = 'utf-8' if LANGUAGE == 'en-GB' else 'iso-8859-1'
COLOUR_TEMPLATE = 'Colour' if LANGUAGE == 'en-GB' else 'Cor'

if DST_IP == '':
    print('You need to set DST_IP in config.py to your IPv4 address.\n\nOn Windows, enter \'ipconfig\' in the command line. It should look like 192.168.x.x.')
    exit()
