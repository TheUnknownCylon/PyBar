from pybar import Widget


class OBShutdown(Widget):
    '''
    Simple OBShutDown widget. An icon is presented, if the user clicks it,
    obshutdown (third-party) is executed.

    https://github.com/panjandrum/obshutdown/
      --or--
    https://aur.archlinux.org/packages.php?ID=52343
    '''

    def setup(self):
        self.icon("arch")
        self.mouse_click_left = "obshutdown"
