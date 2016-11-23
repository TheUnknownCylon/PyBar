import base64
from io import BytesIO
from PIL import Image

import struct #convert hex to rgba
import codecs #convert hex to rgba

# Determine python version used for base64 encoding compatability
import sys
PY3 = sys.version_info[0] >= 3

class DZENCOMMANDS:
    TW = 'tw'
    BG = 'bg'
    FG = 'fg'
    I  = 'i'
    CA = 'ca'
    PH = 'ph'  #non-dzen command, placeholder


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


    def xbm2png(self, filename, fgcolor, bgcolor):
        output = BytesIO()

        try:
            img = Image.open(filename)
            imgrgba = img.convert('RGBA')
            imgrgbadata = imgrgba.getdata()

            newData = []
            for pixel in imgrgbadata:
                if pixel[0] == 0:
                    newData.append(bgcolor)
                else:
                    newData.append(fgcolor)

            imgrgba.putdata(newData)
            imgrgba.save(output, 'PNG')
            return output.getvalue()

        finally:
            output.close()


    def format(self, dzenString, wid=None):
        htmlstr = ''

        color_fg = ""
        color_bg = ""

        openSpan = False  # True if there is a <span> currently opened
        newspan = True    # True if a value of the current span is not up to date
                          #  once a new span can be created, it will.
        ca_stack = []     # Stack of command actions, which should be closed with ^C(A)

        while dzenString:
            #Find the first non-escaped ^

            prePart, _, dzenString = dzenString.partition("^")
            if not dzenString:
                htmlstr += prePart
                break

            else:
                if newspan:
                    if openSpan:
                        htmlstr += "</span>"

                    htmlstr += '<span style="'
                    htmlstr += 'color: {};'.format(color_fg if color_fg else self.color_fg_default)
                    htmlstr += 'background-color: {};'.format(color_bg if color_bg else self.color_bg_default)
                    htmlstr += '">'
                    openSpan = True
                    newspan = False
                htmlstr += prePart.replace(" ", "&nbsp;")

                command, _, dzenString = dzenString.partition("(")
                args_raw, _, dzenString = dzenString.partition(")")
                args = [arg.strip() for arg in args_raw.split(",")]

                if not command:
                    pass

                elif command == DZENCOMMANDS.BG:
                    newspan = True
                    color_bg = args[0]

                elif command == DZENCOMMANDS.FG:
                    newspan = True
                    color_fg = args[0]

                elif command == DZENCOMMANDS.PH:
                    w = args[0]
                    h = args[1]
                    id = args[2]
                    htmlstr += '<span widgetid="{3}" style="display:inline-block; width:{0}px; height:{1}px;" class="bar_placeholder" id="{2}">&nbsp;</span>'.format(w,h,id, wid)

                elif command == DZENCOMMANDS.I:
                    if newspan:
                        if openSpan:
                            htmlstr += "</span>"

                        htmlstr += '<span style="'
                        htmlstr += 'color: {};'.format(color_fg if color_fg else "")
                        htmlstr += 'background-color: {};'.format(color_bg if color_bg else "")
                        htmlstr += '">'
                        openSpan = True
                        newspan = False

                    #convert the selected colors to RGBA colors
                    rgbacolorfg = hex2rgba("{0}FF".format(color_fg[1:] if color_fg else self.color_fg_default[1:]))
                    rgbacolorbg = hex2rgba("{0}00".format(color_bg[1:] if color_bg else self.color_bg_default[1:]))

                    img_base64 = data2base64(self.xbm2png(args[0], rgbacolorfg, rgbacolorbg))
                    htmlstr += '<img src="data:image/png;base64,{}" alt="X"/>'.format(img_base64)

        if openSpan:
            htmlstr += "</span>"

        return htmlstr
