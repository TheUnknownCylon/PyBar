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