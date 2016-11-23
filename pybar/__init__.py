import os
import sys
import threading
import logging

iconpath = os.path.abspath(os.path.dirname(__file__))+"/icons"

try:
    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)
except Exception as e:
    logging.info("Could not initialize dbus: {}".format(e))


class WidgetManager():
    '''
    Instance of this class will hold all initialized widgets.
    Widgets are displayed in placement order. If a widget updates its value
    the WidgetManager prints the whole Dzen2 String.

    Currently there is no way to remove, or stop the WidgetManager :P (lol)
    '''
    def __init__(self, wm_output=sys.stdout, customIconPath=None, iconcolor=None, textcolor=None):
        self.widgets = []
        self.iconpath  = customIconPath or iconpath
        self.iconcolor = iconcolor or ""
        self.textcolor = textcolor or ""
        self.wm_output = wm_output

    def add(self, widget):
        try:
            widget.setmanager(self)
            self.widgets.append(widget)
            self.draw(widget) #force the drawing of the newly added widget
        except:
            pass # Adding the widget failed


    def draw(self, widget):
        '''
        Widget callback. One widget informs its value has changed.
        TODO: maybe cache values in a dict and build a string from those values instead of accessing
              each widget myvalue field each time.
        '''
        value = ""
        for w in self.widgets:
            value += w.toDzen2String(self.iconpath, self.iconcolor, self.textcolor)+"  "

        # self.wm_output.write("^tw()"+value + "\n")
        # self.wm_output.flush()


class Widget():
    '''
    Widget base class. All elements in the PyBar are called widgets.

    * Each widget holds a String value, which is printed in the PyBar.
    * If a widget wants its value changed, the self.value(newvalue) method should
      be called. The value in the PyBar is updated automatically.
    * If a widget needs to monitor or update a value periodically, then the widget
      should implement the thread() method.
    '''

    def __init__(self, *args, **kwargs):
        self.myvalue = ""
        self.iconvalue = ""

        #For now mouse actions can be defined, but can only be overwritten in
        # setup
        self.mouse_click_left = None
        self.mouse_click_right = None
        self.mouse_click_middle = None
        self.mouse_scroll_up = None
        self.mouse_scroll_down = None

        self._args = args
        self._kwargs = kwargs

    def setmanager(self, manager):
        '''
        Call this manager to set the widgets main manager.
        When using this Widget for PyBar properly, only the
        WidgetManager will call this method.
        '''
        self.manager = manager
        self.setup(*self._args, **self._kwargs)
        threading.Thread(target=self.thread).start()

    def setup(self):
        '''
        Is called when the widget should initialize itself.
        An initial value can be set by calling the value() method.
        '''
        pass

    def thread(self):
        '''
        This method is started in a new thread. Can be used to monitor or
        periodically check a value.
        '''
        pass

    def icon(self, newicon):
        '''
        Update the widget icon.
        '''
        self.iconvalue = newicon
        self.manager.draw(self)

    def value(self, newvalue):
        '''
        Updates the widget textual value. Calling this method will call
        other methods necessary to update the value in the PyBar.
        '''
        self.myvalue = newvalue
        self.manager.draw(self)


    def toDzen2String(self, iconpath, iconcolor, textcolor):
        icontext = self.iconvalue or ""
        if icontext:
            icontext = "^fg("+iconcolor+")" + "^i("+iconpath+"/"+icontext+".xbm)" + "^fg("+textcolor+")"

        valuetext = self.myvalue or ""
        if valuetext:
            valuetext = "^fg("+textcolor+")" + valuetext

        #determine mouse action wrappers
        mouse_wrap_start = ""
        mouse_wrap_end = ""
        if(self.mouse_click_left):
            mouse_wrap_start += "^ca(1,{})".format(self.mouse_click_left)
            mouse_wrap_end += "^ca()"
        if(self.mouse_click_middle):
            mouse_wrap_start += "^ca(3,{})".format(self.mouse_click_middle)
            mouse_wrap_end += "^ca()"
        if(self.mouse_click_right):
            mouse_wrap_start += "^ca(2,{})".format(self.mouse_click_right)
            mouse_wrap_end += "^ca()"
        if(self.mouse_scroll_down):
            mouse_wrap_start += "^ca(4,{})".format(self.mouse_scroll_down)
            mouse_wrap_end += "^ca()"
        if(self.mouse_scroll_up):
            mouse_wrap_start += "^ca(5,{})".format(self.mouse_scroll_up)
            mouse_wrap_end += "^ca()"


        if icontext and valuetext:
            return mouse_wrap_start+icontext+" "+valuetext+mouse_wrap_end
        elif icontext or valuetext:
            return mouse_wrap_start+icontext+valuetext+mouse_wrap_end
        else:
            return ""



from PyQt4.QtGui import QWidget
from PyQt4.QtCore import Qt, QRect

class HTMLPopupWidget(Widget):
    '''
    Class that represents a widget with popup support.
    A Qt Window (QWidget) is created and can be used for drawing, manipulating
    this class.

    Note: mouseEntersWindow and mouseLeavesWindow should not be replaced with
     other functionality (expanding is possible).
    '''

    def __init__(self, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)

        # Create a window which has no border, and which is always on top
        self._window = QWidget()
        self._window.setWindowFlags(Qt.FramelessWindowHint)
        self._window.setWindowFlags(Qt.X11BypassWindowManagerHint | Qt.WindowStaysOnTopHint)

        # Flag which is True when a draw has been requested, but it can not be
        # assumed that the focus is in this window.
        self.drawrequested = False

        # Flag which is True when the mouse is in the window
        self.mouseinwindow = False

        # If the mouse enters or leaves the window, act!
        self._window.enterEvent = self.mouseEntersWindow
        self._window.leaveEvent = self.mouseLeavesWindow

        # Some colors stuff
        self._window.setStyleSheet("QWidget { background-color : #1B1D1E; color : #FFFFFF; border: 2px solid #804000; border-top: none }");


    def showPopup(self, top, left):
        '''Method to be overwritten. Is called when the Window is allowed to show
        a popup. If the Widget decides to show a popup, it should call the
        self._drawPopup method.'''
        raise NotImplemented()


    def hidePopup(self):
        '''Method to be overwritten. Is called when the Window is supposed to
        close it's active popup. If the Widget decides to hide the popup, it
        should call the self._hidePopup() method.'''
        raise NotImplemented()


    #################################

    def mouseEntersWindow(self, *args, **kwargs):
        self.mouseinwindow = True


    def mouseLeavesWindow(self, *args, **kwargs):
        self.mouseinwindow = False
        self.hidePopupRequest()


    def changeGeometry(self, top, left, width, height, autocorrect=True):
        self._window.setGeometry(QRect(left, top, width, height))
        #TODO: Autocorrect if left+width > screenwidth


    def showPopupRequest(self, top, left):
        self.drawrequested = True
        if not self._window.isVisible():
            self.showPopup(top, left)


    def hidePopupRequest(self):
        self.drawrequested = False
        if not self.mouseinwindow and not self.drawrequested:
            self.hidePopup()


    def _drawPopup(self, top, left, width, height, autocorrect=True):
        self.changeGeometry(top, left, width, height, autocorrect)
        self._window.show()
        self.drawrequested = True


    def _hidePopup(self):
        self._window.hide()


