# rs-book-capture

Command-line tool for transcribing RuneScape 3 books in wikitext format by capturing network packets.

1. [Requirements](#requirements)
1. [Before starting](#before-starting)
1. [Book capture](#book-capture)
1. [Master farmer log](#master-farmer-log)

## Requirements
* Python 3
* `pyshark` module (install using `pip install pyshark`)

## Before starting
* In `config.py`, change `DST_IP` to your IPv4 address which looks like `192.168.x.x`
* Make sure you're using the correct interface name for pyshark (if you've got Wireshark installed, you can run `tshark -D` to find the number corresponding to the interface that streams the packets. It looks like you can't easily use the friendly name e.g. "WiFi", but there is probably a way to do it)
* Change `LANGUAGE` to anything else if the game client language isn't English

## Book capture

Transcribes books in wikitext format.

### Usage
* Log into RuneScape 3
* In the command line, enter `py -m capture book`
* Wait for the program to tell you when to open the book (this should be a few seconds)
* In the game client, open a book (it should probably be a book with a standard interface)
* Keep clicking next page until the end of the book (or before, if you wish) and close the book
* A file with the transcript of the book formatted to wikitext should have been generated in the `out\books` directory

### Notes
It's buggy. Perhaps it won't realise the book has been closed. If it hasn't almost instantly found the end of the book when you close it or it gets stuck at any other point for a few seconds, close the program and try again.

The transcript file should be reviewed for formatting issues. It's possible that, at the end of a page, it places a `<br />` where there should be two newlines instead. Perhaps some coloured headers have to be changed to actual wiki headers to facilitate navigation, or remove the index, etc. The text itself should be verbatim though.

## Master farmer log

Logs master farmer loot in JSON format.

### Usage
* Log into RuneScape 3
* In the command line, enter `py -m capture thiev`
* Wait for the program to tell you when to start pickpocketing (this should be a few seconds)
* In the game client, start pickpocketing
* Keep pickpocketing undefinitely. Close the program when done
* A JSON file should have been generated in the `out\thieving_logs` directory. The program will log the data to that file every time you run the script.

### Notes
It may stop logging after 200-300 attempts.
