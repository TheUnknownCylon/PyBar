
from pybar import Widget
import dbus

class BattMonStates:
    '''
    All battery status as described on the UPower interface.
    '''
    UNKNOWN = 0
    CHARGING = 1
    DISCHARCHING = 2
    EMPTY = 3
    FULLY_CHARGED = 4
    PENDING_CHARGE = 5
    PENDING_DISCHARGE = 6


class BattMon(Widget):
    '''
    Battery monitoring widget.
    Requires you to have UPower installed in order to function.
    
    Is not tested on desktops. Most likely there will be no information.
    '''
    def setup(self):
        self._batteries = []

        system_bus = dbus.SystemBus()
        
        upower = system_bus.get_object('org.freedesktop.UPower', '/org/freedesktop/UPower')
        enumDevices = upower.get_dbus_method('EnumerateDevices', 'org.freedesktop.UPower')
        for device in enumDevices():
            if "BAT" in device:
                ubat = system_bus.get_object('org.freedesktop.UPower', str(device))
                self._batteries.append(ubat) #store the battery for later access
        
                # Register to dbus change method
                ubat_interface = dbus.Interface(ubat, dbus_interface='org.freedesktop.UPower.Device')
                ubat_interface.connect_to_signal('Changed', self.loadValue)
        
        self.loadValue()
        
        
    def loadValue(self):
        valuestr = ""
        powersupply = False
        for ubat in self._batteries:
            props = ubat.get_dbus_method('GetAll', 'org.freedesktop.DBus.Properties')("org.freedesktop.UPower.Device")
            percentage = int(props["Percentage"]) #%
            #timetofull = int(props["TimeToFull"]) #seconds
            #timeleft = int(props["TimeToEmpty"]) #seconds
            state = int(props["State"])
            if state==BattMonStates.CHARGING or state==BattMonStates.FULLY_CHARGED or state==BattMonStates.PENDING_CHARGE:
                powersupply = True 
            if valuestr:
                valuestr += " "     
            valuestr += str(percentage) + "%"
            
        if powersupply or len(valuestr)==0:
            self.icon("plug")
        else:
            self.icon("battery")
        self.value(valuestr)
        