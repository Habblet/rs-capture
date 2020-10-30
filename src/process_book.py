import regex as re
import os
import sys

from config import *
from letters import letters_pt as letters


MAX_LINE_PX = 200

# TODO: Substitute space between one page and the next with the number of
#       unused lines
LINES_PER_PAGE = 15

PAT_PRE_TITLE = re.compile(b'\x00..\x5d\x52\x5d\x52\x5d\x52\x5d\x52\x00..', re.DOTALL)
PAT_PAGE_NUM_ODD = re.compile(b'(\x3e|\x40)\x03.\x00', re.DOTALL)
PAT_PAGE_START = re.compile(b'\x0a\x01\x5d(\x53|\x55)\x5d(\x53|\x55)\x5d(\x53|\x55)\x5d(\x53|\x55)', re.DOTALL)
PAT_BOOK_END = re.compile(b'\x5d\x54\x5d\x54\x5d\x54\x5d\x54', re.DOTALL)
# PAT_BOOK_END = re.compile(b"\x5d(\x53|\x54)\x5d(\x53|\x54)\x5d(\x53|\x54)\x5d(\x53|\x54)", re.DOTALL)

# Gets the width of a string in pixels as it would appear
# on the screen using the game client
def get_px_width(line):
    line_px = 0
    for char in line:
        if char in letters:
            line_px += letters[char]
        else:
            line_px += 8
            # print('Unrecognised character ||', char, '||', hex(ord(char)))
    return line_px


# Decides whether to add a newline based on the last opcodes read
def addnewln(last_op, vbyte):
    if len(last_op) >= 7:
        # print(last_op)
        if last_op[-7:] in [b'\x00\x00\x03' + vbyte + b'\x03' + vbyte + b'\x80', b'\x00\x00\x03' + vbyte + b'\x03' + vbyte + b'\x81']:
            return b'\n'
        elif len(last_op) >= 8 and last_op[-8:] in [b'\x00\x00\x03' + vbyte + b'\x80\x03' + vbyte + b'\x81', b'\x00\x00\x03' + vbyte + b'\x81\x03' + vbyte + b'\x81']:
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

# Main function
def file_to_wikitext(inputFilename, debug=False):
    inp = open(inputFilename, 'rb')
    end = inp.seek(0, 2)
    inp.seek(0)
    string = b''
    last_op = b''

    pages = 0

    bytesread = b''
    start = inp.tell()
    title = b''
    # mixed_packets = False
    # contains_index = False

    while not re.match(PAT_PRE_TITLE, bytesread):
        inp.seek(start)
        bytesread = inp.read(14)
        # print(bytesread)
        start += 1
    # if bytesread[-13:-11] == b"\x01\x00":
    #     mixed_packets = True
    #     print("Stream contains mixed packets.")

    start = inp.tell()
    PAT_PAGE_FIRST = re.compile(b'\x00\x00.\x03(\xbe|\xc0).\x00', re.DOTALL)
    bytesread = inp.read(7)
    while not re.match(PAT_PAGE_FIRST, bytesread):
        _ = inp.seek(inp.tell() - 6)
        bytesread = inp.read(7)
    vbyte = bytes([bytesread[4]])  # can be 0xC0 or 0xBE
    _ = inp.seek(inp.tell() - 8)
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

    PAT_PAGE_NUM_EVEN = re.compile(b"\x03" + vbyte + b".\x00", re.DOTALL)
    PAT_PAGE_END = re.compile(b"(\x19|\x30|\x61)\x03" + vbyte + b".\x00.\x03" + vbyte + b"(\x80|\x81).\x00.\x03" + vbyte + b"(\x80|\x81)...", re.DOTALL)

    start = inp.tell()
    book_end = False
    page_start_found = False

    while not book_end:
        b = inp.read(4)
        page_odd = re.match(PAT_PAGE_NUM_ODD, b) if pages != 0 else re.match(PAT_PAGE_NUM_EVEN, b)
        if page_odd:
            page_num_digits = ord(inp.read(1))
            page_num = None
            if page_num_digits == 6:
                page_num = inp.read(1)
            elif 6 < page_num_digits < 8:
                page_num = inp.read(page_num_digits - 5)
            else:
                print('Unexpected byte for page_num_digits')
                continue
            print_page_num(page_num)
            pages += 1
            page_num = None
            while not re.match(PAT_PAGE_NUM_EVEN, inp.read(4)):
                _ = inp.seek(inp.tell() - 3)
            page_num_digits = ord(inp.read(1))
            if page_num_digits == 6:
                page_num = inp.read(1)
            elif page_num_digits > 6:
                page_num = inp.read(page_num_digits - 5)
            else:
                print('Unexpected byte for page_num_digits')
            print_page_num(page_num)
            pages += 1
            while True:
                op = inp.read(2)
                if op == b'\x00\x00':
                    if re.match(PAT_PAGE_END, inp.read(18)):
                        page_start_bytes = inp.read(10)
                        while not re.match(PAT_PAGE_START, page_start_bytes):
                            if re.match(PAT_BOOK_END, page_start_bytes):
                                book_end = True
                                break
                            _ = inp.seek(inp.tell() - 9)
                            page_start_bytes = inp.read(10)
                        if string[-1] != ord('\n'):
                            pass
                            string += b"\n"
                        page_start_found = True
                        break
                    else:
                        _ = inp.seek(inp.tell() - 18)
                        last_op += op
                        _ = inp.read(1)
                elif op == b'\x03' + vbyte:
                    op = inp.read(1)
                    if op in [b'\x80', b'\x81']:
                        # Handles bytes found before some images
                        inp.read(1)
                        pre_img_bytes = inp.read(2)
                        if pre_img_bytes == b'\xbe\x03':
                            inp.read(17)
                        else:
                            inp.seek(inp.tell() - 3)
                            last_op += b'\x03' + vbyte + op
                            if not page_start_found:
                                string += addnewln(last_op, vbyte)
                            if inp.read(1) != b'\x00':
                                _ = inp.read(2)
                            else:
                                if inp.read(1) == b'\x00':
                                    _ = inp.read(1)
                    else:
                        last_op += b"\x03" + vbyte
                        _ = inp.read(2)
                else:
                    page_start_found = False
                    _ = inp.seek(inp.tell() - 2)
                    string += inp.read(1)
                if (inp.tell() + 50) > end:
                    break
        if (inp.tell() + 50) > end:
            break
        _ = inp.seek(inp.tell() - 3)

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
