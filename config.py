import os


# Network
DST_IP = '192.168.1.63'  # your IPv4 address (run "ipconfig" in the command line) e.g. 192.168.x.x
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