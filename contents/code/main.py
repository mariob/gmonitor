# -*- coding: utf-8 -*-
#
#   Copyright (C) 2009 Mario Boikov <mario@beblue.org>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License version 2,
#   or (at your option) any later version, as published by the Free
#   Software Foundation
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details
from PyQt4 import QtCore
from PyQt4 import QtGui

from PyKDE4 import plasmascript
from PyKDE4 import kdeui
from PyKDE4 import kdecore
from PyKDE4.kio import KIO
from PyKDE4.plasma import Plasma

import feedparser

class MailFrame(Plasma.Frame):
    def __init__(self, parent=None):
        super(MailFrame, self).__init__(parent)

        self.layout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Vertical)

        # Create the mail icon widget
        self.mailIcon = Plasma.IconWidget(self)
        self.mailIcon.setIcon(kdeui.KIcon('mail-unread-new'))

        # Create the count label
        self.countLabel = Plasma.Label(self)
        self.countLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.layout.addItem(self.mailIcon)
        self.layout.addItem(self.countLabel)
        self.setLayout(self.layout)

        # Propagate clicks on the mail icon widget
        QtCore.QObject.connect(self.mailIcon, QtCore.SIGNAL('clicked()'),
                               self, QtCore.SIGNAL('clicked()'))

        # Default state
        self.setCount(0)

    def setCount(self, count):
        """ Update the mail icon and text according to the count value """
        self.mailIcon.setEnabled(count > 0)
        if count > 0:
            self.countLabel.setText("<b>Count: {0}</b>".format(count))
        else:
            self.countLabel.setText("<b>No new mail</b>")

class GMonitorApplet(plasmascript.Applet):
    """ Monitors a Gmail inbox and displays the number of unread mail """

    def __init__(self, parent=None):
        super(GMonitorApplet, self).__init__(parent)
        # Fake settings
        self.settings = {}
        self.settings['feed_url'] = 'https://mail.google.com/mail/feed/atom/'
        self.settings['mail_url'] = 'https://mail.google.com'
        self.settings['interval'] = 20 # secs

    def init(self):
        """ Create UI and connect to signals """
        # Don't show 'settings' pop up when right-clicking the applet.
        self.setHasConfigurationInterface(False)

        # Create mail frame instance
        self.mailFrame = MailFrame(self.applet)

        # Layout the mail frame
        layout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Horizontal, self.applet)
        layout.addItem(self.mailFrame)
        self.setLayout(layout)

        # Connect MailFrame.setCount() to the 'mailcount' signal.
        # MailFrame.setcount() will be called with the number of unread mail
        # each time the 'mailcount' signal is emitted. The signal is emitted
        # from the parse_feed() method.
        QtCore.QObject.connect(self, QtCore.SIGNAL('mailcount(int)'),
                               self.mailFrame.setCount)

        # Connect open_browser() to the 'clicked' signal emitted by
        # the MailFrame when the icon is clicked.
        QtCore.QObject.connect(self.mailFrame, QtCore.SIGNAL('clicked()'),
                               self.openBrowser)

        # Create a timer that will poll the feed. This will not actually
        # start the timer yet.
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL('timeout()'),
                               self.fetchFeed)

        # Trigger a manual fetch the first time
        self.fetchFeed()

        # Start the poll timer
        self.timer.start(self.settings["interval"] * 1000)

    def fetchFeed(self):
        """ Download feed """
        url = kdecore.KUrl(self.settings['feed_url'])
        job = KIO.storedGet(url, KIO.Reload, KIO.HideProgressInfo)
        QtCore.QObject.connect(job, QtCore.SIGNAL("result(KJob*)"),
                               self.parseFeed)

    def parseFeed(self, job):
        """ Parse the mail feed from google and emit a signal """
        if job.error():
            job.ui.showErrorDialog()
            return

        d = feedparser.parse(str(job.data()))
        # Emit a 'mailcount' signal with the number of unread mail.
        QtCore.QObject.emit(self, QtCore.SIGNAL('mailcount(int)'),
                            int(d.feed.fullcount))

    def openBrowser(self):
        """ Invoke a new browser instance loading 'mail_url' """
        kdecore.KToolInvocation.invokeBrowser(self.settings['mail_url'])

def CreateApplet(parent):
    """ Create an instance of the GMonitorApplet """
    return GMonitorApplet(parent)
