
from pybar import Widget
import dbus
import logging

class Wicd(Widget):
    '''
    WICD widget, places the current network status in the PyBar.
    It can take a NetworksObserver instance as observer. If the network
    status changes, the NetworksObserver is called back.
    '''

    def setup(self):
        self.wireless_connected = False
        self.wired_connected = False

        self.wireless_status_text = "?"
        self.wired_status_text = "?"

        self.ip = None
        self.accesspoint = None
        self.signalstrength = None
        self.speed = None

        system_bus = dbus.SystemBus()

        wicd = system_bus.get_object('org.wicd.daemon', '/org/wicd/daemon')
        wicd_interface = dbus.Interface(wicd, dbus_interface='org.wicd.daemon')
        wicd_interface.connect_to_signal('StatusChanged', self.wicdupdate)

        #wired = system_bus.get_object('org.wicd.daemon', '/org/wicd/daemon/wired')
        #wireless = system_bus.get_object('org.wicd.daemon', '/org/wicd/daemon/wireless')

        self.icon("wifi")
        self.updatetext()

    def updatetext(self):
        self.value(self.wireless_status_text)


    def wicdupdate(self, status, values):
        status = int(status)
        wireless_connectionstate = self.wireless_connected

        if status == 0:   #disconnected
            self.wireless_connected = False
            self.wireless_status_text = "_"
        elif status == 1: #Connecting
            self.wireless_connected = False
            self.wireless_status_text = "..."
        elif status == 2: #Connected
            self.wireless_connected = True
            self.wireless_status_text = str(values[2]) + "%"
        else:
            logging.debug("Unknown WICD state: " + repr(status))
            self.wireless_connected = False
            self.wireless_status_text = "?"

        self.updatetext()

        self.ip = values[0]
        self.accesspoint = values[1]

        self.signalstrength = str(values[2])
        self.speed = values[4]


