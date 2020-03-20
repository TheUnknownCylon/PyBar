#!/usr/bin/env python3

from pybar.application import run
from pybar.bar import Bar
from pybar.widgets.battmon import BattMon
from pybar.widgets.clock import Clock
from pybar.widgets.obshutdown import OBShutdown
from pybar.widgets.inputreader import InputReader
from pybar.widgets.tray import Tray


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
    topbar = Bar(iconcolor="#EBAC54")

    topbar.addWidgetLeft(InputReader())
    # topbar.addWidgetRight(ClockCalendar())
    topbar.addWidgetRight(BattMon())
    topbar.addWidgetRight(Tray(barwindow=topbar.window, namerewriter=trayName))
    topbar.addWidgetRight(Clock())
    topbar.addWidgetRight(OBShutdown())

    # Loop, so that the bar will never disappear.
    run()
