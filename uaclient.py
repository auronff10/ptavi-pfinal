#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa cliente que abre un socket a un servidor
"""


import sys
import socket


# Cliente UDP simple.

try:
    #Parametros para la conexión.
    METODO = sys.argv[1]
    SIP = sys.argv[2]
except IndexError:
    print "Usage: python client.py method receiver@IP:SIPport"
    sys.exit()

# Dirección IP del servidor.

SIP = SIP.split("@")
SIP[1] = SIP[1].split(":")

USER = SIP[0]
SERVER = SIP[1][0]
PORT = int(SIP[1][1])

ACK = "ACK" + ' ' + USER + '@' + SERVER + " SIP/2.0\r\n"

# Contenido que vamos a enviar
LINE = METODO + ' ' + USER + "@" + SERVER + " SIP/2.0\r\n"

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
    print "Error: No server listening at " + SERVER + " port " + str(PORT)
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
