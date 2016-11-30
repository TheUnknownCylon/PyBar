import os
from pybar.lib.dzenparser import Dzen2HTMLFormatter
from PyQt4.QtCore import Qt, QRect, pyqtSignal
from PyQt4.QtGui import QWidget, QVBoxLayout
from PyQt4.QtWebKit import QWebView, QWebPage
import Xlib.display

try:
    import urlparse
except:
    import urllib.parse as urlparse

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


FGCOLOR = "#FFFFFF"
BGCOLOR = "#1B1D1E"
iconpath = os.path.abspath(os.path.dirname(__file__)) + "/icons"


class Bar:

    def __init__(self, width, height, xpos=0, ypos=0, customIconPath=None,
                 iconcolor=None, textcolor=None):
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
        if widget in self.widgets_left:
            self.drawSection('contentleft', self.widgets_left)

        if widget in self.widgets_right:
            self.drawSection('contentright', self.widgets_right)

    def drawSection(self, containerid, widgets):
        widgetstr = ('<span id="w{}" onmouseout="mouseout(this);"'
                     ' onmouseover="mousehover(this);"'
                     ' onclick="mouseclick(this);">{}</span>&nbsp;')
        value = []
        for w in widgets:
            # Draw the widget, but only if it has content
            text = self.formatter.format(w.toDzen2String(
                self.iconpath, self.iconcolor, self.textcolor),
                "w{0}".format(id(w)))
            if len(text) > 0:
                value.append(widgetstr.format(id(w), text))

        self.window.updateContent.emit(containerid, ('&nbsp;' * 2).join(value))

    def callback(self, widgetname, action, data):
        for widget in self.widgets_left + self.widgets_right:
            if "w{}".format(id(widget)) == widgetname:
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
            x11window.change_property(atom_strut_partial, atom_cardinal, 32,
                                      [0, 0, self._height, 0,  0, 0, 0, 0,
                                       self._xpos, self._xpos + self._width, 0,
                                       0])
            x11window.change_property(atom_strut, atom_cardinal, 32,
                                      [0, 0, self._height, 0])

        else:  # bottom
            x11window.change_property(atom_strut_partial, atom_cardinal, 32,
                                      [0, 0, 0, self._height,  0, 0, 0, 0,
                                       self._xpos, self._xpos + self._width,
                                       self._ypos, self._ypos + self._height])
            x11window.change_property(atom_strut, atom_cardinal, 32, [
                                      0, 0, 0, self._height])

        display.sync()

    def handle_updateContent(self, divid, htmlcode):
        frame = self.view.page().mainFrame()
        escaped = htmlcode.replace('"', '\\\"')
        js = """document.getElementById("{}").innerHTML="{}"; """
        frame.evaluateJavaScript(js.format(divid, escaped))

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
    template = open(templatefilename, 'r').read()
    return template % (width, height - 1, border, BGCOLOR, FGCOLOR)
