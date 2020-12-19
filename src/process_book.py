import regex as re
import os
import sys

from config import *
from letters import letters_pt as letters


MAX_LINE_PX = 200

# TODO: Substitute space between one page and the next with the number of
#       unused lines
LINES_PER_PAGE = 15

PAT_PRE_TITLE = re.compile(b'\x00..\x5d\x52\x5d\x52\x5d\x52\x5d\x52...', re.DOTALL)
PAT_PAGE_NUM_ODD = re.compile(b'(\x3e|\x40)\x03.\x00', re.DOTALL)
PAT_PAGE_START = re.compile(b'\x0a\x01\x5d(\x53|\x55)\x5d(\x53|\x55)\x5d(\x53|\x55)\x5d(\x53|\x55)', re.DOTALL)
PAT_BOOK_END = re.compile(b'\x5d\x54\x5d\x54\x5d\x54\x5d\x54', re.DOTALL)
# PAT_BOOK_END = re.compile(b"\x5d(\x53|\x54)\x5d(\x53|\x54)\x5d(\x53|\x54)\x5d(\x53|\x54)", re.DOTALL)


def get_px_width(line: str):
    """Gets the width of a string in pixels, as it would appear on the screen using the game client.

    :param line: The string to measure
    :return: An integer, the width of the string
    """
    line_px = 0
    for char in line:
        if char in letters:
            line_px += letters[char]
        else:
            line_px += 8
            # print('Unrecognised character ||', char, '||', hex(ord(char)))
    return line_px


# Decides whether to add a newline based on the last opcodes read
def addnewln(last_op, vbytes):
    if len(last_op) >= 7:
        # print(last_op)
        if last_op[-7:] in [b"\x00\x00" + vbytes * 2 + b"\x80", b"\x00\x00" + vbytes * 2 + b"\x81"]:
            return b'\n'
        elif len(last_op) >= 8 and last_op[-8:] in [b"\x00\x00" + vbytes + b"\x80" + vbytes + b"\x81", b"\x00\x00" + vbytes + b"\x81" + vbytes + b"\x81"]:
            return b'\n'
    return b''

# Prints page number bytes as int
def print_page_num(b):
    try:
        page_num = b.decode(ENCODING)
        if page_num.isnumeric():
            page_num = int(page_num)
            print('Page number:', page_num)
    except:
        print('Unexpected page number:', b)


def file_to_wikitext(input_filename: str, debug=False):
    """Main function.

    :param input_filename: The path to the .cap file
    :param debug:
    """
    inp = open(input_filename, 'rb')
    end = inp.seek(0, 2)
    inp.seek(0)
    string = b''
    last_op = b''

    pages = 0

    bytesread = b''
    start = inp.tell()
    title = b''

    while not re.match(PAT_PRE_TITLE, bytesread):
        inp.seek(start)
        bytesread = inp.read(14)
        # print(bytesread)
        start += 1

    #inp.read(inp.read(1))

    start = inp.tell()
    PAT_PAGE_FIRST = re.compile(b'\x00.....\x00\x06\x31', re.DOTALL)
    bytesread = inp.read(9)
    while not re.match(PAT_PAGE_FIRST, bytesread):
        _ = inp.seek(inp.tell() - 8)
        bytesread = inp.read(9)
    vbytes = bytesread[3:5]  # can be 0xC0 or 0xBE
    _ = inp.seek(inp.tell() - 10)
    while True:
        title_byte = inp.read(1)
        title_char = ''
        try:
            title_char = title_byte.decode(ENCODING)
        except:
            pass
        if title_char in letters:
            inp.seek(inp.tell() - 2)
            if inp.read(1) == b'\x00':
                inp.read(1)
                break
            inp.read(1)
            title += title_byte
            inp.seek(inp.tell() - 2)
        else:
            break
    title = list(title)
    title.reverse()
    title = bytes(title)

    print('Title:', title)

    inp.seek(inp.tell() + len(title))
    inp.read(3)

    PAT_PAGE_NUM_EVEN = re.compile(vbytes + b".\x00", re.DOTALL)
    PAT_PAGE_END = re.compile(b"." + vbytes + b".\x00." + vbytes + b"(\x80|\x81).\x00." + vbytes + b"(\x80|\x81)...", re.DOTALL)

    start = inp.tell()
    book_end = False
    page_start_found = False
    found_single_vbytes = False
    vbyte1 = None
    vbyte2 = None

    while not book_end:
        b = inp.read(1)
        while b != b"\x00":
            b = inp.read(1)
            # print('t',inp.tell())
        b = inp.read(1)
        if b == b"\x06":
            b = inp.read(1)
            try:
                _ = int(b)
                # print(_)
            except ValueError:
                inp.seek(inp.tell() - 1)
                continue
        elif b == b"\x07":
            b = inp.read(2)
            try:
                _ = int(b)
                # print(_)
            except ValueError:
                inp.seek(inp.tell() - 2)
                continue
        elif b in [b"\x5d", b"\x54"]:
            b = inp.read(7)
            if b in [b"\x54\x5d\x54\x5d\x54\x5d\x54", b"\x5d\x54\x5d\x54\x5d\x54\x5d"]:
                print('End found.')
            else:
                inp.seek(inp.tell() - 7)
                continue
        else:
            continue
        inp.read(3)
        while not re.match(PAT_PAGE_NUM_EVEN, inp.read(4)):
            _ = inp.seek(inp.tell() - 3)
        page_num_digits = ord(inp.read(1))
        if page_num_digits == 6:
            page_num = inp.read(1)
        elif page_num_digits > 6:
            page_num = inp.read(page_num_digits - 5)
        else:
            print('Unexpected byte for page_num_digits')
        inp.read(7)
        line_chars_num = inp.read(1)[0] - 5
        string += inp.read(line_chars_num)
        page_start_found = False
        while not book_end and not page_start_found:
            bytesread = inp.read(13)
            if vbyte2 is None:
                vbyte2 = bytesread[8:11]
            line_chars_num = inp.read(1)[0] - 5
            possible_string = inp.read(line_chars_num)
            try:
                possible_string.decode(ENCODING)
                # print('OK',inp.tell(),possible_string)
                string += b"\n" + possible_string
            except UnicodeDecodeError:
                #print('pos:',possible_string)
                #print('br',bytesread[:10])
                _ = inp.seek(inp.tell() - line_chars_num - 4)
                page_start_bytes = bytesread[:10]
                while not re.match(PAT_PAGE_START, page_start_bytes):
                    #print('start',page_start_bytes)
                    if re.match(PAT_BOOK_END, page_start_bytes):
                        page_start_found = True
                        book_end = True
                        print('end found')
                        break
                    _ = inp.seek(inp.tell() - 9)
                    page_start_bytes = inp.read(10)
                string += b"\n"
                page_start_found = True
        if (inp.tell() + 50) > end:
            break
        _ = inp.seek(inp.tell() - 1)
    
    # print(string)
    text = string.decode(ENCODING).strip()

    # print(text)

    # Remove <p> tags (doesn't seem to affect the formatting)
    # Remove <br> tags (used for pictures and indices)
    text = re.sub(r'<p(=\d+|)>', '', text)
    text = re.sub(r'<br(=[\d,]+|)>', '', text)

    # Replace <col> tags with Colour template
    text = re.sub(r'<col=([\d\w]{6})>', r'{{' + COLOUR_TEMPLATE + r'|#\1|', text)
    # text = re.sub("</col>", "}}", text)

    # Reduce newlines to 3 maximum
    # Remove spaces before and after newlines
    text = re.sub('\n{4,}', '\n\n\n', text)
    text = re.sub('(\n +| +\n)', '\n', text)

    text = text.split("\n")

    # print(text)

    for n, i in enumerate(text):
        i = re.sub(r'{{' + COLOUR_TEMPLATE + r'\|#[\d\w]{6}\|', '', i)
        i = re.sub(r'</col>', '', i)
        i_px = get_px_width(i)
        if i_px > MAX_LINE_PX:
            print('The following line exceeds the maximum pixel width per line (%d/%d):\n%s\n' % (i_px, MAX_LINE_PX, i))
        if n == (len(text) - 1):
            continue
        if len(text[n+1].strip()) == 0:
            continue
        next_line = text[n+1]
        next_line = re.sub(r'{{' + COLOUR_TEMPLATE + r'\|#[\d\w]{6}\|', '', next_line)
        next_line = re.sub('</col>', '', next_line)
        if 0 < i_px <= MAX_LINE_PX:
            diff = MAX_LINE_PX - i_px
            next_line_match = re.match(r"^[a-zA-Z0-9\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u024F\-\"\',\.\?!\:]+", next_line)
            if next_line_match is None:
                continue
            next_line_match_px = get_px_width(next_line_match.group(0))
            if (next_line_match_px + letters[' ']) >= diff:
                continue
            text[n] += '<br />'
            if False:
                print(f'Line PX: {i_px}', f'Next line word PX: {next_line_match_px+letters[" "]} + 7', f'Diff: {diff}', f'\nLine:    {i}', f'Next line word:    {next_line_match.group(0)}\n', sep='\t|')

    # print(text)

    text = '\n'.join(text).replace('\n ', '')

    text = text.split('\n')
    for n, line in enumerate(text):
        lbracket_count = line.count(r'{{' + COLOUR_TEMPLATE + "|#") - line.count(r'</col>')
        if line.find('<br />') != -1:
            text[n] = re.sub(r'<br />', r'}}' * lbracket_count + '<br />', text[n]).replace('</col>', '}}')
        else:
            text[n] = text[n].replace('</col>', '}}') + r'}}' * lbracket_count

    # print(text)

    text = '\n'.join(text)
    text = re.sub(r'(?<=[^ -]-)\n(\S)', r'\1', text)
    text = re.sub(r'(?<!(<br />|\n))\n(\S)', r' \2', text)

    outputFilename = ''.join(i for i in title.decode(ENCODING) if i not in '\/:*?<>|').rstrip() + '.txt'
    print('Saving to %s...' % outputFilename)
    with open(os.path.join(DIR_BOOKS, outputFilename), 'w') as out:
        out.write(text.strip())
    print('\nSneak peek:\n\n' + text.strip()[:200] + '...')


if __name__ == '__main__':
    file_to_wikitext(sys.argv[1], debug=True)
