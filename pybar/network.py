import os
import socket
import threading

RTMGRP_LINK        = 0x001
RTMGRP_IPV4_IFADDR = 0x010
RTMGRP_IPV6_IFADDR = 0x100


class NetworkNotified:
    '''Interface object, can receive network connect and disconnect messages
      from a NetworkNotifier.'''
    
    def nwstate_changed(self):
        '''Is called when the state of a a network has changed.'''
        pass


class NetworksObserver:
    '''
    Class which observe the network state. The class waits for network-state
    changes messages from the (linux) kernel. Once observed that the network
    state has changed, it uses a third-party to see what's happening.
    
    '''    
        
    def __init__(self):
        self.widgets = []
        threading.Thread(target=self.observe).start()
       
       
    def addWidget(self, widget):
        self.widgets.append(widget)
        widget.nwstate_changed()
    
    
    def observe(self):
        while(1):
            s = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, socket.NETLINK_ROUTE)
            s.bind((os.getpid(), RTMGRP_IPV4_IFADDR | RTMGRP_IPV6_IFADDR))
            s.recv(4096)
            s.close()
            
            #the network state has changed, inform observers
            for widget in self.widgets:
                try:
                    widget.nwstate_changed()
                except Exception as _:
                    pass


# If this module is loaded, start a network observer to which observables can
#  connect to themselves.
nwObserver = NetworksObserver()        
