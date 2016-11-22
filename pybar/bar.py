
##########################################################################
## X11 imports and methods

import Xlib.display
display = Xlib.display.Display()
root = display.screen().root

atom_strut = display.intern_atom("_NET_WM_STRUT")
atom_strut_partial = display.intern_atom("_NET_WM_STRUT_PARTIAL")
atom_cardinal = display.intern_atom('CARDINAL')
atom_net_system_tray = display.intern_atom(
    "_NET_SYSTEM_TRAY_S%d" % display.get_default_screen())
atom_manager = display.intern_atom("MANAGER")
atom_tray_opcode = display.intern_atom("_NET_SYSTEM_TRAY_OPCODE")
atom_net_wm_pid = display.intern_atom("_NET_WM_PID")


def x11_send_event(win, ctype, data, mask=None):
    """ Send a ClientMessage event to the root """
    data = (data + [0] * (5 - len(data)))[:5]
    ev = Xlib.protocol.event.ClientMessage(
        window=win, client_type=ctype, data=(32, (data)))
    if not mask:
        mask = (X.SubstructureRedirectMask | X.SubstructureNotifyMask)
    root.send_event(ev, event_mask=mask)


##########################################################################

import os
from pybar.lib.dzenparser import Dzen2HTMLFormatter
from PyQt4.QtCore import Qt, QRect, pyqtSignal
from PyQt4.QtGui import QWidget, QVBoxLayout
from PyQt4.QtWebKit import QWebView, QWebPage

try:
    import urlparse
except:
    import urllib.parse as urlparse


FGCOLOR = "#FFFFFF"
BGCOLOR = "#1B1D1E"
iconpath = os.path.abspath(os.path.dirname(__file__)) + "/icons"


class Bar:

    def __init__(self, width, height, xpos=0, ypos=0, customIconPath=None, iconcolor=None, textcolor=None):
        self.widgets_left = []
        self.widgets_right = []

        self.iconpath = customIconPath or iconpath
        self.iconcolor = iconcolor or ""
        self.textcolor = textcolor or ""

        self.window = Window(self, xpos, ypos, width, height)
        self.window.show()

        self.formatter = Dzen2HTMLFormatter(FGCOLOR, BGCOLOR)

        self._height = height

    def addWidgetLeft(self, widget):
        widget.setmanager(self)
        self.widgets_left.append(widget)
        self.draw(widget)

    def addWidgetRight(self, widget):
        widget.setmanager(self)
        self.widgets_right.append(widget)
        self.draw(widget)

    def draw(self, widget):
        '''Widget callback. One widget informs its value has changed.'''
        value = ""

        if widget in self.widgets_left:
            for w in self.widgets_left:
                value += w.toDzen2String(self.iconpath,
                                         self.iconcolor, self.textcolor) + "  "
            self.window.updateContent.emit(
                'contentleft', self.formatter.format(value.strip()))

        if widget in self.widgets_right:
            for w in self.widgets_right:

                # Draw the widget, but only if it has content
                text = self.formatter.format(w.toDzen2String(
                    self.iconpath, self.iconcolor, self.textcolor), "w{0}".format(id(w)))
                if len(text) > 0:
                    value += '&nbsp;&nbsp;<span id="w{}" onmouseout="mouseout(this);" onmouseover="mousehover(this);" onclick="mouseclick(this);">{}</span>&nbsp;'.format(
                        id(w), text)

            self.window.updateContent.emit('contentright', value)

    def callback(self, widgetname, action, data):
        for widget in self.widgets_left + self.widgets_right:
            if "w{}".format(id(widget)) == widgetname:
                #widget.__getattribute__(action)(data)
                getattr(widget, action)(**data)


class Window(QWidget):

    updateContent = pyqtSignal(str, str, name='updateContent')

    def __init__(self, callback, xpos, ypos, width, height):
        super(Window, self).__init__()

        self._xpos = xpos
        self._ypos = ypos
        self._width = width
        self._height = height
        self._callback = callback

        self.setStyleSheet(
            "QWidget { background-color : #1B1D1E; color : #FFFFFF;  }")
        self.setAsBar()

        view = QWebView(self)
        view.setContextMenuPolicy(Qt.CustomContextMenu)
        view.statusBarMessage.connect(self.qt_statusbar_callback)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view)

        view.setPage(QWebPage())
        view.setHtml(htmltemplate(self._width, self._height,
                                  "bottom" if ypos == 0 else "top"))

        self.view = view
        self.updateContent.connect(self.handle_updateContent)

    def setAsBar(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.X11BypassWindowManagerHint)
        self.setGeometry(QRect(self._xpos, self._ypos,
                               self._width, self._height))

        x11window = display.create_resource_object('window', self.winId())
        if self._ypos < 100:
            x11window.change_property(atom_strut_partial, atom_cardinal, 32, [
                                      0, 0, self._height, 0,  0, 0, 0, 0, self._xpos, self._xpos + self._width, 0, 0])
            x11window.change_property(atom_strut, atom_cardinal, 32, [
                                      0, 0, self._height, 0])

        else:  # bottom
            x11window.change_property(atom_strut_partial, atom_cardinal, 32, [
                                      0, 0, 0, self._height,  0, 0, 0, 0, self._xpos, self._xpos + self._width, self._ypos, self._ypos + self._height])
            x11window.change_property(atom_strut, atom_cardinal, 32, [
                                      0, 0, 0, self._height])

        display.sync()

    def handle_updateContent(self, divid, htmlcode):
        frame = self.view.page().mainFrame()
        escaped = htmlcode.replace('"', '\\\"')
        frame.evaluateJavaScript(
            """document.getElementById("%s").innerHTML="%s"; """ % (divid, escaped))

    def qt_statusbar_callback(self, url):
        urldata = urlparse.urlparse(str(url))
        if urldata.scheme == "pybar":
            widget = urldata.hostname
            action = urldata.path[1:]
            dataraw = urlparse.parse_qs(urldata.query)
            data = {k: v[0] for k, v in dataraw.items()}
            self._callback.callback(widget, action, data)


##########################################################################

def htmltemplate(width, height, border):
    templatefilename = os.path.join(os.path.dirname(__file__), 'template.html')
    return open(templatefilename, 'r').read() % (width, height - 1, border, BGCOLOR, FGCOLOR)
