#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa cliente que abre un socket a un servidor
"""


import sys
import socket
import uaserver
import time
import os
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
    ParserDTD = uaserver.ParserDTD()
    parser.setContentHandler(ParserDTD)
    parser.parse(open(FICHEROCONFIG))
    TAGS = ParserDTD.get_tags()
    return TAGS

CONFIG ={}
CONFIG = readficheroconfig()

# Dirección IP del servidor.

USER = CONFIG["account_username"]
SERVER = CONFIG["uaserver_ip"]
IP_PROXY = CONFIG["regproxy_ip"]
PORT_PROXY = int(CONFIG["regproxy_puerto"])
PORT_RTP = int(CONFIG["rtpaudio_puerto"])
PORT_UASERVER = int(CONFIG["uaserver_puerto"])
AUDIO = CONFIG["audio_path"]
FICHEROLOG = CONFIG["log_path"]

SDP = "v=0\r\n" + "o=" + USER + '@' + SERVER + " " + SERVER + "\r\n" + "s=misesion\r\n" + "m=audio " + str(PORT_RTP) + " RTP"
ACK = "ACK" + ' sip:' + OPCION + " SIP/2.0\r\n"
CVLC = "cvlc rtp://@" + SERVER + ":" + str(PORT_RTP) + "&"



uaserver.tolog(FICHEROLOG, "interna","Starting...","")

# Contenido que vamos a enviar
if METODO == "INVITE":
    LINE = "INVITE" + ' sip:' + OPCION  + " SIP/2.0\r\n" 
    LINE += "Content-Type: application/sdp\r\n\r\n"
    LINE += SDP
elif METODO == "REGISTER":
    LINE = "REGISTER" + " sip:" + USER + "@" + SERVER +":" + str(PORT_UASERVER) + " SIP/2.0\r\n"
    LINE += "Expires: " + str(OPCION)+ "\r\n\r\n"
elif METODO == "BYE":
    LINE = "BYE" + ' sip:' + OPCION  + " SIP/2.0\r\n\r\n" 
else:
    LINE = METODO + " sip:" + USER + "@" + SERVER +":" + str(PORT_UASERVER) + " SIP/2.0\r\n\r\n"

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((IP_PROXY, PORT_PROXY))

print "Enviando: " + LINE
my_socket.send(LINE)
uaserver.tolog(FICHEROLOG, "envio", LINE, [SERVER,str(PORT_PROXY)])
try:
    data = my_socket.recv(1024)
    uaserver.tolog(FICHEROLOG, "recivo", data, [SERVER,str(PORT_PROXY)])
    print 'Recibido -- ', data
except socket.error:
    fecha = time.strftime('%Y%m%d%H%M%S',time.gmtime(time.time()))
    error = " Error: No server listening at " + SERVER + " port " + str(PORT_PROXY)
    print fecha + error
    uaserver.tolog(FICHEROLOG, "interna", error, "")
    sys.exit()

data = data.split('\r\n\r\n')

if (data[0] == "SIP/2.0 100 Trying"):
        if (data[1] == "SIP/2.0 180 Ringing"):
            if (data[2] == "SIP/2.0 200 OK\r\nContent-Type: application/sdp"):
                data[3] = data[3].split()
                PORT_RTP = data[3][4]
                print "Enviando: " + ACK
                my_socket.send(ACK + '\r\n')
                IP_RTP = OPCION.split("@")[1]
                os.system(CVLC)
                COMANDO = './mp32rtp -i ' + IP_RTP + ' -p ' + str(PORT_RTP) + ' < ' + AUDIO
                print "COMIENZA EL RTP " + COMANDO
                os.system(COMANDO)
                uaserver.tolog(FICHEROLOG, "envio", "Comienza el envio de RTP", [IP_RTP,str(PORT_RTP)])
                print "RTP FINALIZADO"

print "Terminando socket..."
uaserver.tolog(FICHEROLOG, "interna","Finishing...","")


# Cerramos todo.
my_socket.close()
print "Fin."
