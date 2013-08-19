import thread
import os, sys
import gobject

iconpath = os.path.abspath(os.path.dirname(__file__))+"/icons"

try:
    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)
except Exception as e:
    print("Could not initialize dbus: "+e)


def loop():
    '''Never ending loop, DBus callbacks enabled.'''
    loop = gobject.MainLoop()
    gobject.threads_init() #@UndefinedVariable
    loop.run()


class WidgetManager():
    '''
    Instance of this class will hold all initialized widgets.
    Widgets are displayed in placement order. If a widget updates its value
    the WidgetManager prints the whole Dzen2 String.
    
    Currently there is no way to remove, or stop the WidgetManager :P (lol)
    '''
    def __init__(self, wm_output=sys.stdout, customIconPath=None, iconcolor=None, textcolor=None):
        self.widgets = []
        self.iconpath  = customIconPath or iconpath
        self.iconcolor = iconcolor or ""
        self.textcolor = textcolor or ""
        self.wm_output = wm_output
    
    def add(self, widget):
        try:
            widget.setmanager(self)
            self.widgets.append(widget)
            self.draw(widget) #force the drawing of the newly added widget
        except:
            pass # Adding the widget failed
  
  
    def draw(self, widget):
        '''
        Widget callback. One widget informs its value has changed.
        TODO: maybe cache values in a dict and build a string from those values instead of accessing
              each widget myvalue field each time.
        '''
        value = ""
        for w in self.widgets:
            value += w.toDzen2String(self.iconpath, self.iconcolor, self.textcolor)+"  "
       
        self.wm_output.write("^tw()"+value + "\n")
        self.wm_output.flush()


class Widget():
    '''
    Widget base class. All elements in the PyBar are called widgets.
    
    * Each widget holds a String value, which is printed in the PyBar.
    * If a widget wants its value changed, the self.value(newvalue) method should
      be called. The value in the PyBar is updated automatically.
    * If a widget needs to monitor or update a value periodically, then the widget
      should implement the thread() method.
    '''
        
    def __init__(self, *args, **kwargs):
        self.myvalue = ""
        self.iconvalue = ""
        
        #For now mouse actions can be defined, but can only be overwritten in setup
        # Consider them as java-protected vars.
        self.mouse_click_left = None
        self.mouse_click_right = None
        self.mouse_click_middle = None
        self.mouse_scroll_up = None
        self.mouse_scroll_down = None
        
        self._args = args
        self._kwargs = kwargs

    def setmanager(self, manager):
        '''
        Call this manager to set the widgets main manager.
        When using this Widget for PyBar properly, only the
        WidgetManager will call this method.
        '''
        self.manager = manager
        self.setup(*self._args, **self._kwargs)
        thread.start_new_thread(self.thread, ())
  
    def setup(self):
        '''
        Is called when the widget should initialize itself.
        An initial value can be set by calling the value() method.
        '''
        pass
  
    def thread(self):
        '''
        This method is started in a new thread. Can be used to monitor or
        periodically check a value.
        '''
        pass
    
    def icon(self, newicon):
        '''
        Update the widget icon.
        '''
        self.iconvalue = newicon
        self.manager.draw(self)
  
    def value(self, newvalue):
        '''
        Updates the widget textual value. Calling this method will call
        other methods necessary to update the value in the PyBar.
        '''
        self.myvalue = newvalue
        self.manager.draw(self)
    
    
    def toDzen2String(self, iconpath, iconcolor, textcolor):
        icontext = self.iconvalue or ""
        if icontext:
            icontext = "^fg("+iconcolor+")" + "^i("+iconpath+"/"+icontext+".xbm)"
            
        valuetext = self.myvalue or ""
        if valuetext:
            valuetext = "^fg("+textcolor+")" + valuetext
        
        #determine mouse action wrappers
        mouse_wrap_start = ""
        mouse_wrap_end = ""
        if(self.mouse_click_left):
            mouse_wrap_start += "^ca(1,%s)" % self.mouse_click_left
            mouse_wrap_end += "^ca()"
        if(self.mouse_click_middle):
            mouse_wrap_start += "^ca(3,%s)" % self.mouse_click_middle
            mouse_wrap_end += "^ca()"
        if(self.mouse_click_right):
            mouse_wrap_start += "^ca(2,%s)" % self.mouse_click_right
            mouse_wrap_end += "^ca()"
        if(self.mouse_scroll_down):
            mouse_wrap_start += "^ca(4,%s)" % self.mouse_scroll_down
            mouse_wrap_end += "^ca()"
        if(self.mouse_scroll_up):
            mouse_wrap_start += "^ca(5,%s)" % self.mouse_scroll_up
            mouse_wrap_end += "^ca()"

        
        if icontext and valuetext:
            return mouse_wrap_start+icontext+" "+valuetext+mouse_wrap_end
        elif icontext or valuetext:
            return mouse_wrap_start+icontext+valuetext+mouse_wrap_end
        else:
            return ""
