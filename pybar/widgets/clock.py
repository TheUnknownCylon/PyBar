import time
from datetime import datetime

from pybar import Widget


class Clock(Widget):
    '''
    Clock widget, representing the system time.
    '''

    def setup(self, showDate=True, timezone=None, prefix=""):
        self._showDate = showDate
        self._timezone = timezone
        self._prefix = prefix
        self.icon("clock")
        self.update()

    def update(self):
        timestr = datetime.now(self._timezone).strftime("%H:%M")

        # Funny thing
        if timestr == "13:37":
            timestr = "LE:ET"

        datestr = ""
        if self._showDate:
            datestr = datetime.now(self._timezone).strftime("%d-%m-%Y")

        self.value(self._prefix + timestr + " " + datestr)

    def thread(self):
        while True:
            self.update()
            time.sleep(20)
