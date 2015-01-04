#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa servidor proxy-registrar
"""
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import os
import time
import sys
import SocketServer
import uaserver
import socket


class SessionHandler(ContentHandler):  # Igual a la del uaserver, sacamos las tags

    def __init__(self):
        self.lista = []

    def startElement(self, name, attrs):

        if name == "server":
            self.server = {}
            self.server["name"] = attrs.get("name", "")
            self.server["ip"] = attrs.get("ip", "127.0.0.1")
            self.server["puerto"] = attrs.get("puerto", "")
            self.lista.append(self.server)

        elif name == "database":
            self.database = {}
            self.database["path"] = attrs.get("path", "")
            self.lista.append(self.database)

        elif name == "log":
            self.log = {}
            self.log["path"] = attrs.get("path", "")
            self.lista.append(self.log)

    def get_tags(self):
        return self.lista

