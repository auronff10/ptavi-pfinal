#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa cliente que abre un socket a un servidor
"""


import sys
import socket
import parserconfig
import time
from xml.sax import make_parser

if len(sys.argv) != 4:
    print "Usage: python server.py config metodo opcion"
    sys.exit()


#Parametros para la conexión.
    
FICHEROCONFIG = sys.argv[1]
METODO = sys.argv[2]
OPCION = sys.argv[3]

def readficheroconfig():
    parser = make_parser()
    ParserDTD = parserconfig.ParserDTD()
    parser.setContentHandler(ParserDTD)
    parser.parse(open("ua2.xml"))
    TAGS = ParserDTD.get_tags()
    return TAGS

CONFIG ={}
CONFIG = readficheroconfig()

# Dirección IP del servidor.

USER = CONFIG["account_username"]
SERVER = CONFIG["uaserver_ip"]
PORT = int(CONFIG["uaserver_puerto"])
PORT_RTP = int(CONFIG["rtpaudio_puerto"])

SDP = "v=0\r\n" + "o=" + USER + "\r\n" + "s=misesion\r\n" + "m=audio " + str(PORT_RTP) + " RTP"


ACK = "ACK" + ' sip:' + USER + '@' + SERVER + " SIP/2.0\r\n"

# Contenido que vamos a enviar
if METODO == "INVITE":
    LINE = "INVITE" + ' sip:' + USER + "@" + SERVER + " SIP/2.0\r\n" 
    LINE += "Content-Type: application/sdp\r\n\r\n"
    LINE += SDP
elif METODO == "REGISTER":
    LINE = ""
elif METODO == "BYE":
    LINE = ""

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((SERVER, PORT))

print "Enviando: " + LINE
my_socket.send(LINE + '\r\n')
try:
    data = my_socket.recv(1024)
    print 'Recibido -- ', data
except socket.error:
    fecha = time.strftime('%Y%m%d%H%M%S',time.gmtime(time.time()))
    print fecha + " Error: No server listening at " + SERVER + " port " + str(PORT)
    sys.exit()

data = data.split('\r\n\r\n')

if (data[0] == "SIP/2.0 100 Trying"):
        if (data[1] == "SIP/2.0 180 Ringing"):
            if (data[2] == "SIP/2.0 200 OK"):
                print "Enviando: " + ACK
                my_socket.send(ACK + '\r\n')

print "Terminando socket..."

# Cerramos todo.
my_socket.close()
print "Fin."
