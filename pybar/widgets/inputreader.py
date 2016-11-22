import sys
from pybar import Widget

class InputReader(Widget):
    '''Simple widget that takes a Dzen2 formatted string as input, and draws
    it on the bar.'''

    def setup(self):
        self.update()

    def update(self):
        self.value("")

    def thread(self):
        line = sys.stdin.readline()
        while line:
            self.value(line.rstrip("\n"))
            line = sys.stdin.readline()

