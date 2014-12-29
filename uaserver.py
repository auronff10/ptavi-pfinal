#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import os
import time
import sys
import SocketServer

class SessionHandler(ContentHandler):

    def __init__(self): #Iniciamos 
        self.lista = []

    def startElement(self, name, attrs): # Tomamos los tags como en el SmallSmil

        if name == "account": 
            self.account = {}
            self.account["username"] = attrs.get("username", "")
            self.lista.append(self.account)

        elif name == "uaserver":
            self.uaserver = {}
            self.uaserver["ip"] = attrs.get("ip", "127.0.0.1")
            self.uaserver["puerto"] = attrs.get("puerto", "")
            self.lista.append(self.uaserver)

        elif name == "rtpaudio":
            self.rtpaudio = {}
            self.rtpaudio['puerto'] = attrs.get("puerto", "")
            self.lista.append(self.rtpaudio)

        elif name == "regproxy":
            self.regproxy = {}
            self.regproxy["ip"] = attrs.get("ip", "127.0.0.1")
            self.regproxy["puerto"] = attrs.get("puerto", "")
            self.lista.append(self.regproxy)

        elif name == "log":
            self.log = {}
            self.log["path"] = attrs.get("path", "")
            self.lista.append(self.log)
        elif name == "audio":
            self.audio = {}
            self.audio["path"] = attrs.get("path", "")
            self.lista.append(self.audio)

    def get_tags(self):
        return self.lista




