# rs-book-capture

Command-line tool for transcribing RuneScape 3 books as wikitext by capturing network packets.

## Requirements
* Python 3
* `pyshark` module (install using `pip install pyshark`)

## Before starting
* Create `captures` and `books` folders where you will run the script.
* In `capture_book.py`, change `DST_IP` to your IPv4 address which looks like `192.168.x.x`.
* Make sure you're using the correct interface name for pyshark
* Change `LANGUAGE` to anything else if the game client language isn't English
* `DEBUG` doesn't really do anything right now

## Usage
* Log into RuneScape 3
* In the command line, enter `py -m capture_book`
* Wait for the program to tell you when to open the book (this should be a few seconds)
* In the game client, open a book (it should probably be a book with a standard interface)
* Keep clicking next page until the end of the book (or before, if you wish) and close the book
* A file with the transcript of the book formatted to wikitext should have been generated in the `books` directory

## Notes
It's buggy. Perhaps it won't realise the book has been closed. If it hasn't almost instantly found the end of the book when you close it, close the program and try again.
