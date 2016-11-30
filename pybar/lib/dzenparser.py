import base64
from io import BytesIO
from PIL import Image

import struct  # convert hex to rgba
import codecs  # convert hex to rgba

# Determine python version used for base64 encoding compatability
import sys
PY3 = sys.version_info[0] >= 3


class DZENCOMMANDS:
    TW = 'tw'  # ^tw() draw to title window (only supported option)
    BG = 'bg'  # ^bg(color) set background color with hex value
    FG = 'fg'  # ^fg(color)
    I = 'i'    # ^i(path)   draw icon
    CA = 'ca'  # ^ca(btn, cmd) clickable area
    PH = 'ph'  # ^ph(width, height, id) non-dzen command, placeholder


def hex2rgba(hexstr):
    '''
    Converts a hexstr to (R,G,B,A).
    The input hexstr should not contain the #-sign.
    Python 2 and Python 3 compatible implementation.
    '''
    return struct.unpack('BBBB', codecs.getdecoder('hex_codec')(hexstr)[0])


def data2base64(data):
    '''
    Converts input data to a base64 representation.
    Output is a (decoded) string.
    Python 2 and Python 3 compatible implementation.
    '''
    output_bytes = base64.b64encode(data)
    if PY3:
        return output_bytes.decode('ascii')
    else:
        return output_bytes


def format_span(colorfg, colorbg, content):
    htmlstr = '<span style="color: {}; background-color: {};">{}</span>'
    return htmlstr.format(colorfg, colorbg, content.replace(' ', '&nbsp;'))


def format_ph(width, height, id, widgetid):
    htmlstr = ('<span widgetid="{3}" style="display:inline-block; '
               'width:{0}px; height:{1}px;" class="bar_placeholder" id="{2}">'
               '&nbsp;</span>')
    return htmlstr.format(width, height, id, widgetid)


def xbm2png(filename, colorfg, colorbg):
    # convert the selected colors to RGBA colors
    rgbacolorfg = hex2rgba("{0}FF".format(colorfg[1:]))
    rgbacolorbg = hex2rgba("{0}00".format(colorbg[1:]))

    output = BytesIO()
    try:
        img = Image.open(filename)
        imgrgba = img.convert('RGBA')
        imgrgbadata = imgrgba.getdata()

        newData = []
        for pixel in imgrgbadata:
            if pixel[0] == 0:
                newData.append(rgbacolorbg)
            else:
                newData.append(rgbacolorfg)

        imgrgba.putdata(newData)
        imgrgba.save(output, 'PNG')
        return output.getvalue()

    finally:
        output.close()


def format_i(imgpath, colorfg, colorbg):
    img_base64 = data2base64(xbm2png(imgpath, colorfg, colorbg))
    return '<img src="data:image/png;base64,{}" alt="X"/>'.format(img_base64)


class Dzen2HTMLFormatter:
    '''
    This simple class is capable of rewriting a single DZEN2 line to a
    matching HTML-string, where the text is put between <span> elements.

    Currently only the ^tw(), ^bg(), ^fg(), and i^() are supported.
    Other commands are ignored.
    '''

    def __init__(self, colorfg="", colorbg="", widtetname=""):
        self.color_fg_default = colorfg
        self.color_bg_default = colorbg

    def format(self, dzenString, wid=None):
        htmlstr = []

        color_fg = self.color_fg_default
        color_bg = self.color_bg_default

        while dzenString:
            # Find the first non-escaped ^
            prePart, _, dzenString = dzenString.partition('^')

            if prePart:
                htmlstr.append(format_span(color_fg, color_bg, prePart))

            if not dzenString:
                break

            command, _, dzenString = dzenString.partition("(")
            args_raw, _, dzenString = dzenString.partition(")")
            args = [arg.strip() for arg in args_raw.split(",")]

            if not command:
                pass

            elif command == DZENCOMMANDS.BG:
                color_bg = args[0]

            elif command == DZENCOMMANDS.FG:
                color_fg = args[0]

            elif command == DZENCOMMANDS.PH:
                width = args[0]
                height = args[1]
                id = args[2]
                htmlstr.append(format_ph(width, height, id, wid))

            elif command == DZENCOMMANDS.I:
                htmlstr.append(format_i(args[0], color_fg, color_bg))

            else:
                print("Unknown command: {}".format(command))
        return ''.join(htmlstr)
