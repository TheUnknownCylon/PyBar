#!/bin/python2

from pybar.bar import Bar
from pybar.widgets import BattMon, Clock, OBShutdown
from pybar.widgets.inputreader import InputReader
from pybar.widgets.tray import Tray

from PyQt4.QtGui import QApplication
import sys
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
app = QApplication(sys.argv)


def trayName(name, wm_class):
    if not name and not wm_class:
        name = "Dropbox"
    elif name == "seafile-applet":
        name = "seafile"
    elif name == "NetworkManager Applet":
        name = "NetworkManager"

    return name.title()

if __name__ == "__main__":
    # Create the bar object
    # topbar = Bar(1920, 14, xpos=1680, iconcolor="#EBAC54")  # Top
    #topbar = Bar(1920, 14, xpos=1920, iconcolor="#EBAC54")  # Top
    topbar = Bar(1920, 14, iconcolor="#EBAC54")  # Top
    # bar_bottom = Bar(1920, 6, 0, 1080-6)  #Bottom

    topbar.addWidgetLeft(InputReader())
    # topbar.addWidgetRight(ClockCalendar())
    topbar.addWidgetRight(BattMon())
    topbar.addWidgetRight(Tray(barwindow=topbar.window, namerewriter=trayName))
    topbar.addWidgetRight(Clock())
    topbar.addWidgetRight(OBShutdown())

    # Loop, so that the bar will never disappear.
    app.exec_()
