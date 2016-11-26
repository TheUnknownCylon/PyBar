
'''
First version of email checking.
Only IMAP is supported.
'''

import sys
from pybar import Widget
from pybar.network import NetworkNotified, nwObserver
import threading
import logging

imapclient_installed = False
try:
    from imapclient import IMAPClient
    imapclient_installed = True
except:
    sys.stderr.write(("imapclient not installed, using the PyBar IMAP widget "
                      "will not work.\nPlease refer to the README for a "
                      "downloadlink.\n"))


class IMAP(Widget, NetworkNotified):

    def setup(self, hostname, username, password, useSSL=True, use_uid=True):
        self.icon("mail")
        self.value("?")

        if not imapclient_installed:
            self.myvalue = "not installed"

        self.do_idle = False
        self.hostname = hostname
        self.username = username
        self.password = password
        self.useSSL = useSSL
        self.use_uid = use_uid

        nwObserver.addWidget(self)

    def nwstate_changed(self):
        '''Callback network change'''

        if not imapclient_installed:
            return

        self.disconnect()

        try:
            self.mainserver = self.connect(
                self.hostname, self.username, self.password)
            self.updatevalue(self.mainserver)
            self.do_idle = True
            threading.Thread(target=self.startThread).start()
        except Exception as e:
            logging.error(e)
            self.value("E")

    def disconnect(self):
        '''Handle a disconnect request. If not connected, nothing happens.'''
        try:
            self.do_idle = False
            self.mainserver.idle_done()
            self.mainserver.logout()
        except:
            pass
        finally:
            self.mainserver = None

    def connect(self, host, username, password):
        '''Connects to the IMAP server and returns a new connection.
        The inbox is selected by default'''
        server = IMAPClient(host, use_uid=self.use_uid, ssl=self.useSSL)
        server.login(username, password)
        server.select_folder('INBOX')
        return server

    def updatevalue(self, server):
        '''Update the numbmer of UNSEEN emails.
        Takes server as a IMAPClient connecction'''
        messages = server.search(['UNSEEN'])
        try:
            self.value("%d" % len(messages))
        except Exception as e:
            self.value("?")
            logging.error(e)

    def startThread(self):
        try:
            self.waitForNewMail(self.mainserver)
        except Exception as e:
            logging.error("Error while waiting for new mail!", e)

    def waitForNewMail(self, server):
        '''Thread waits for new messages to be received.'''

        server.idle()
        while self.do_idle:
            server.idle_check()

            # Got some new info (new item/ item read)! Yeey :)
            s = self.connect(self.hostname, self.username, self.password)
            self.updatevalue(s)
            s.logout()
