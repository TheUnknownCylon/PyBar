
import time
from time import strftime
from datetime import datetime

from pybar import Widget

class Clock(Widget):
    '''
    Clock widget, representing the system time.
    '''   
    def setup(self):
        self.update()
        self.icon("clock")
    
    def update(self):
        self.value(strftime("%H:%M", time.localtime()))
    
    def thread(self):
        while True:
            self.update()
            time.sleep(60)



class TimeZoneClock(Widget):
    '''
    Clock widget, printing the current time for a given timezone.
    Setting up with a PyTZ timezone object.
    '''
    def setup(self, timezone, prefix=""):
        '''
        TimeZone should be a PyTZ object, for example:
          timezone = pytz.timezone('US/Pacific-New')
          
        Prefix can be added for human readability.
        '''
        self.prefix = prefix
        self.timezone = timezone
        self.icon("clock")
        self.update()

    def update(self):
        self.value(self.prefix + datetime.now(self.timezone).strftime("%H:%M"))

    def thread(self):
        while True:
            self.update()
            time.sleep(60)
            
