import time
from datetime import datetime

from pybar import Widget, HTMLPopupWidget


class Clock(Widget):
    '''
    Clock widget, representing the system time.
    '''

    def setup(self, timezone=None, prefix=""):
        self.timezone = timezone
        self.prefix = prefix
        self.icon("clock")
        self.update()

    def update(self):
        timestr = datetime.now(self.timezone).strftime("%H:%M")

        # Funny thing
        if timestr == "13:37":
            timestr = "LE:ET"

        datestr = datetime.now(self.timezone).strftime("%d-%m-%Y")
        self.value(self.prefix + timestr + " " + datestr)

    def thread(self):
        while True:
            self.update()
            time.sleep(30)


class ClockCalendar(HTMLPopupWidget):

    def setup(self):
        self.update()

    def update(self):
        self.value("-----")

    def showPopup(self, top, left):
        print("Show popup request")
        self._drawPopup(top, left, 20, 20)

    def hidePopup(self):
        print("Hide popup request")
        self._hidePopup()
