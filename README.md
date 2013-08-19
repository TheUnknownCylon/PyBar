PyBar Readme file
=================

Motivation
----------
Lightweight or tiled Linux window managers do usually not provide a full-fledged desktop environment. Users of these systems may want to have some information, such as the current time or system status, nicely visible on the screen. PyBar, in combination with Dzen2, can be used to achieve this. By placing several widgets on the PyBar, PyBar presents information in an elegant way to its user(s). In this way the user can easily see the current time, battery status, or network status without the need for a full (resource unfriendly) desktop environment.

There are many alternatives for PyBar. Usually `Conky` is used to feed information to `Dzen2`. Other tools and widget-based systems are also written by others. The main motivation of PyBar is that I wanted to have some sort of `fun` (yes: programming is fun to me). As I like my used tiling window manager XMonad installation, and the fact that I am reasonably happy with PyBar, I decided to share it with the rest of the world. So here it is. `:)`. Its not the best, not the greatest, and there may be some bugs `:(`, but if you are interested, feel free to use it. If you find a bug, please report it. I will fix it then `:D` (free of charge).

Example output
--------------
TODO: put a desktop screenshot here :)


Installation
------------
PyBar comes with no installation tool by default. In order to try PyBar, you can just clone the GIT repository. After you have downloaded the source code, you can create a configuration as described in the next section.

The PyBar output is meant to pipe to `Dzen2`, so you may also want to install Dzen2 (https://github.com/robm/dzen). PyBar also requires `DBus` to be installed (but usually this is already installed).

Creating a configuration, and running it
----------------------------------------
PyBar has no nice configuration utility. Instead, you have to write a small python application which acts as some sort of configuration. Below a heavily commented simple configuration is given, which only prints the default time in a bar.

The easiest way to create a configuration, is to create a new file in the same folder as the pybar package lives in. In this example we will store the configuration as `mybar.py`.

```python
#First import the PyBar required pybar elements.
from pybar import WidgetManager, loop as pybarloop

#Next import the Widgets we are going to use, in this example we will
# use the clock widget.
from pybar.widgets import Clock
    
#Create a bar-instance. To this instance the widgets will be appended.
# Optionally Several arguments can be given to the WidgetManager:
#    customIconPath="/home/remco/.xmonad/icons"   | a custom path to the widget icons
#    iconcolor="#EBAC54"                          | gives a color to the widget icons
#    textcolor="white"                            | gives a color to the widget text
bar = WidgetManager(iconcolor="#EBAC54", textcolor="white")
    
#Add a clock-widget to the bar
bar.add(Clock())

#Start a loop, so PyBar will never stop
pybarloop()
```

Now we can execute this example, and spawn this application to a new Dzen2 instance. On Arch Linux, now run the following command: `python2 mybar.py | dzen2`. On other Linux distributions, you may need to replace `python2` with another python application.

Next, if you want to align the text, change the background color, or change the text alignment, please refer to the Dzen2 configuration (https://github.com/robm/dzen/blob/master/README). If you want to use PyBar in conjunction with XMonad, please continue reading until you reach the BONUS sections.



Available Widgets
-----------------
In this Section, the available PyBar widgets are listed. For each widget, also Python code is given which demonstrates how to initialize the widget. Note that there are not that many Widgets available. However they may give you some nice functionalities. Writing a new widget is not that difficult. For hints on how to write (and submit) your own widgets, have a look at one of the BONUS sections in this document).

* `Clock` Prints the default system time.

        Clock()
        

* `TimeZoneClock` Prints the time for a given time zone. This can be useful if you or a close relative resides in a different time zone than you are usually. The second argument is optional, and is a text printed before the time (so you can easily distinguish it from other `Clock` and `TimeZoneClock` objects).

        import pytz        # Python timezone support: http://pypi.python.org/pypi/pytz
        TimeZoneClock(pytz.timezone('US/Pacific-New'), 'CA')


* `ObShutdown` A simple widget which shows you an (Arch Linux `\0/` ) icon. If you click on this icon, `obshutdown` is executed. ObShutdown is a simple shutdown dialog (https://github.com/panjandrum/obshutdown/).

        ObShutdown()
        
        
* `BattMon` Prints the battery charged percentage for each of your batteries.
  Requires that you have `UPower` installed on your system.

        BattMon()
        

* `Wicd` Prints the connection status and signal strength of your WIRELESS network for the Wicd   network manager. Requires you to have configured Wicd (https://launchpad.net/wicd) as network manager.

        Wicd()
        
        
* `EmailIMAP` Prints the number of unread messages in your IMAP-inbox. Requires that you have `IMAPClient` (http://imapclient.freshfoo.com/) installed on your system. Since the IMAPClient implementation does not detect network connection errors very well, a NetworkObserver callback is used to (re)connect if internet access becomes available.

        emailwidget = EmailIMAP(
                hostname = "<enter your imap hostname here>",
                username = "<enter your imap username here>",
                password = "<enter your imap password here>".
                useSSL   = True,     #if not set, defaults to True
                use_uid  = True      #if not set, defaults to True
            )
        networkobserver.addWidget(emailwidget)



Example configuration
---------------------
The following example demonstrates the creating of all widgets.

```python
from pybar import WidgetManager, loop as pybarloop
from pybar.widgets import Wicd, BattMon, Clock, TimeZoneClock, OBShutdown, EmailIMAP
import pytz

# Create the bar object
bar = WidgetManager(iconcolor="#EBAC54")

# Initialize the email widget first (for readability)
emailwidget = EmailIMAP(
                hostname = "<YOUR HOSTNAME HERE>",
                username = "<YOUR PASSWORD HERE>",
                password = "<YOUR HOSTNAME HERE>"
            )

# Now add widgets to the bar, they will be placed from left to right.
# The Wicd widget will inform the network observer if the network status changes.
bar.add(BattMon())
bar.add(Wicd(networkobserver))
bar.add(emailwidget)
bar.add(Clock())
bar.add(TimeZoneClock(
            timezone=pytz.timezone('US/Pacific-New'),
            prefix='CA '))
bar.add(OBShutdown())

# Loop, so that the bar will never disappear.
pybarloop()
```

Bonus: PyBar and XMonad
-----------------------
XMonad (http://xmonad.org/) is a tiling window manager written in Haskell. It is common (but not required) that XMonad users print some information on top of the screen in some sort of status bar. PyBar can be used on top of Dzen2 to fill the system bar. The following XMonad configuration code shows you how PyBar and Dzen2 can be configured for this task. 

_Note that there is no general way to do this. I present just one possibility._

First of all, download Dzen.hs from `https://bitbucket.org/pelletier/dotfiles/src/5a44877b593b/xmonad/lib/Dzen.hs` and place it in `~/.xmonad/lib.Dzen.hs`.

In this setup you will get two Dzen2 instances at top of your screen:
`[============________]`, where `==` takes 60% of your screen width, and `__` takes 40% of your screen width. `==` can be used to display you desktops, and `__` is used to display the PyBar output.

```haskell
    -- use the default as a base and override width and coloring
myLeftBar :: DzenConf
myLeftBar = defaultDzen
    { width   = Just $ Percent 60 -- span 60%
    , Dzen.bgColor = Just "#1B1D1E"
    }

-- use the left one as a base, moving it to the right and making it  
-- right-aligned.
myRightBar :: DzenConf
myRightBar = myLeftBar
    { xPosition = Just $ Percent 60 -- start where the other stopped
    , width     = Just $ Percent 40 -- and span the rest
    , alignment = Just RightAlign
    }
```
        
In your main loop, put the following Haskell code (where you have to fix the path to the PyBar config file):

```haskell
main = do
    dzenTopBar <- spawnDzen myLeftBar
    spawnToDzen "python2 ~/programs/pybar/mybar.py" myRightBar
```
    
And output the loghook to the left Dzen2 instance (which now is called dzenTopBar)

```haskell
    xmonad $ withUrgencyHook NoUrgencyHook $ defaultConfig {
        -- you may have another config here 
        logHook    = takeTopFocus >> logHook' dzenTopBar,
        --
    }
```

Bonus: Writing your own Widget
------------------------------
Assuming you can develop small applications in Python(v2), writing a PyBar widget is very easy. The following text explains how you can write a widget yourself. If you believe your widget is cool and handy for other users as well, feel free to share it with me (please do it in the form of a GitHub pull-request). 

In order to write your own widget, you can extend the `pybar.Widget` class.

* Overwrite the `def setup(self):` method to do the initial setup. You can add parameters to this method as well.
* If you want your widget to poll or update values after waiting, you can overwrite the `def thread(self):` method. After the setup() is handled, this method will automatically executed in a new thread.
* If you want to set or change a widgets value, you should call `self.value("mynewvalue")`. The value in the bar will automatically be updated.
* If you want to set or change change the widgets icon, you should call `self.value("iconname")`. Icons should be put in the `icons` folder, and should be in the `.xbc` format.
* Set the initial icon and value in the `setup()` method. 
* Dbus is already initialized, so you do not have to do that your own.
* If you need a network-aware widget, let your widget ALSO extend the `pybar.network.NetworkNotified` class. The widget should register itself to the network observer:

    from pybar.network import nwObserver
    
    #inside widget setup()
    nwObserver.addWidget(self)

* You can set a mouse left-click, right-click, middle-click, scroll-up, and scroll-down over widget actions by setting one of these in your `setup()` method:

```python
self.mouse_click_left = "firefox"   #executes "firefox" on left click
self.mouse_click_right = None
self.mouse_click_middle = None
self.mouse_scroll_up = None
self.mouse_scroll_down = None
````

* You can use Dzen2 text-strings to format your text


An example of a widget (just the simple clock widget):

```python
from pybar import Widget

import time
from time import strftime
from datetime import datetime

class Clock(Widget):
    def setup(self):
        """
        Setup method, sets the clock-icon and makes sure the current time is set as value.
        """
        self.icon("clock")
        self.update()
        
    def update(self):
        """
        Calls the .value() method, so the time-value is updated on the PyBar.
        """
        self.value(strftime("%H:%M", time.localtime()))
    
    def thread(self):
        """Simple thread, update the time each minute."""
        while True:
            self.update()
            time.sleep(60)
```

Future work
-----------
Several things I want to implement, but that are not done yet`?`:

* Add a volume widget, ALSA and maybe PulseAudio.
* Add a general `bar` widget, that can show values in a rectangle (e.g. ```volume [======....]60%```).
* If possible, implement a Notifier-daemon .
* Dropbox widget, but seems quite problematic. I can not find a nice interface to access Dropbox from other applications. (I don't want to have to original Dropbox icon on my screen, it can live on my desktop9 (waste)-desktop).
* CPU status? (maybe, I don't miss this kind of widgets...)
* `Now playing...` widget for players that have implemented MPRIS (including Spotify, MPD, PyMP (my own unfinished creation `:P`) and other popular players.
* Flashing widgets (in case battery is almost dry)


NAQ (Never Asked Questions)
---------------------------
`Q`: I want a click-action for a widget, but the widget has none
`A`: You can do two things. Option one: sub-class the widget, and overwrite the setup method. In there set the action, e.g. `self.mouse_click_left = "firefox"` (of course, do this after calling the initial superclass setup). The second option is to overwrite the value after you have created the object.
    
    bar = WidgetManager()
    myclock = Clock()
    myclock.mouse_click_left = "firefox http://www.timeanddate.com/worldclock/"
    bar.add(myclock)
    bar.inform()  #Redraws the text-bar.
    