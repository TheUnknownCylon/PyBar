import sys
from pybar import Widget

class InputReader(Widget):
    '''Simple widget that reads and draws Dzen2 formatted strings.'''

    def setup(self):
        self.update()

    def update(self):
        self.value("")

    def thread(self):
        line = sys.stdin.readline()
        while line:
            self.value(line.rstrip("\n"))
            line = sys.stdin.readline()

