import Xlib
from Xlib.X import CurrentTime as XCurrentTime

from pybar import HTMLPopupWidget


class TrayWindow:

    def __init__(self, name, window):
        self.name = name
        self.window = window
        self.xpos = 0
        self.ypos = 0


class Tray(HTMLPopupWidget):

    def setup(self, barwindow, namerewriter, shownames=True):
        self._namerewriter = namerewriter
        self.shownames = shownames  # Also show application names or just icons
        self._barwindow = barwindow

        self.iconsize = 12  # Holds width and height for each icon
        self.trayicons = []  # Holds all the tray-icons to manage
        self.display = None  # Assume to be set if self.istray is True
        self.istray = self._init_libx()  # True iff we have the tray manager
        self.update()  # Set initial value

    def update(self):
        traybar = ""
        for w in self.trayicons:
            if traybar:
                traybar += "  "
            traybar += "^fg(#EBAC54)[^ph({1},{1},{0})]^fg(#FFFFFF)^fg(#FFFFFF)".format(
                w.window.id, self.iconsize)
            if self.shownames and w.name:
                traybar += " " + w.name

        self.value(traybar)

    def placeholderoffset(self, id, top, left, width, height):
        '''The placeholder has a new location, update the position of the trayicon window'''
        twid = int(id)
        for trayicon in self.trayicons:
            if trayicon.window.id == twid:
                trayicon.xpos = int(left)
                trayicon.ypos = int(top)
                break

        self.repaintTrayIcons()

    def _init_libx(self):
        '''Creates an empty window, that will act as the traymanager.'''

        display = Xlib.display.Display()
        net_system_tray = display.intern_atom(
            "_NET_SYSTEM_TRAY_S%d" % display.get_default_screen())
        manager = display.intern_atom("MANAGER")

        root = display.screen().root
        hiddenwindow = root.create_window(-1, -1,
                                          1, 1, 0, display.screen().root_depth)

        if display.get_selection_owner(net_system_tray) != Xlib.X.NONE:
            print("There is another trayer owner")
            return False

        hiddenwindow.set_selection_owner(net_system_tray, XCurrentTime)
        x11_send_event(root, manager, [
                       XCurrentTime, net_system_tray, hiddenwindow.id], (Xlib.X.StructureNotifyMask))
        display.flush()

        self.display = display
        return True

    def addTrayIcon(self, traywindow):
        trayname = self._namerewriter(
            traywindow.get_wm_name(), traywindow.get_wm_class())
        self.trayicons.append(TrayWindow(trayname, traywindow))
        self.update()

    def removeTrayIcon(self, traywindow):
        self.trayicons = [
            tw for tw in self.trayicons if tw.window.id != traywindow.id]
        self.update()
        self.repaintTrayIcons()

    def repaintTrayIcons(self):
        s = self.iconsize
        try:
            for trayicon in self.trayicons:
                trayicon.window.configure(
                    x=trayicon.xpos, y=trayicon.ypos - 1, width=s, height=s)
                trayicon.window.map()

            self.display.flush()
        except Exception as e:
            print(e)

    def thread(self):
        if not self.istray:
            # We are NOT the tray owner...
            return

        display = self.display
        tray_opcode = display.intern_atom("_NET_SYSTEM_TRAY_OPCODE")
        net_wm_pid = display.intern_atom("_NET_WM_PID")

        while True:
            event = display.next_event()

            if event.type == Xlib.X.DestroyNotify:
                self.removeTrayIcon(event.window)

            elif event.type == Xlib.X.ClientMessage:
                data = event.data[1][1]
                task = event.data[1][2]

                if event.client_type == tray_opcode and data == 0:
                    traywindow = display.create_resource_object("window", task)
                    pid = 0
                    try:
                        pidob = traywindow.get_property(
                            net_wm_pid, Xlib.X.AnyPropertyType, 0, 1024)
                        pid = pidob.value[0]
                    except:
                        pass

                    if pid:
                        windowId = int(self._barwindow.winId())
                        traywindow.reparent(windowId, 0, 0)

                        ourmask = (Xlib.X.ExposureMask |
                                   Xlib.X.StructureNotifyMask)
                        traywindow.change_attributes(event_mask=ourmask)

                        self.addTrayIcon(traywindow)


def x11_send_event(win, ctype, data, mask=None):
    '''Send a ClientMessage event to the win'''

    data = (data + [0] * (5 - len(data)))[:5]
    ev = Xlib.protocol.event.ClientMessage(
        window=win, client_type=ctype, data=(32, (data)))
    if not mask:
        mask = (X.SubstructureRedirectMask | X.SubstructureNotifyMask)
    win.send_event(ev, event_mask=mask)
