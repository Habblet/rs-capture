"""
usage: py -m capture [command]

rs-capture is a command-line tool for RuneScape 3 that captures network 
packets and extracts relevant information. Currently, it can transcribe books 
and log master farmer lot, though it has its bugs.

commands:
    book        captures a book
    thiev       captures master farmer loot
    
    -h, --help  shows this message
"""

import sys


argnum = len(sys.argv)

if argnum == 1:
    print(__doc__)
elif argnum > 1:
    cmd = sys.argv[1]
    if sys.argv[1] in ['-h', '--help']:
        print(__doc__)
    elif sys.argv[1] == 'book':
        import capture_book
    elif sys.argv[1] == 'thiev':
        import log_thieving