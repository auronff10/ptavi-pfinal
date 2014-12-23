#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase
"""
import sys
import SocketServer
import os.path
import os
import time
import parserconfig
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

METODOS_PERMITIDOS = ["INVITE", "BYE", "ACK"]

#Datos de conexión

if len(sys.argv) != 2:
    print "Usage: python server.py config"
    sys.exit()

FICHEROCONFIG = sys.argv[1]

def readficheroconfig():
    parser = make_parser()
    ParserDTD = parserconfig.ParserDTD()
    parser.setContentHandler(ParserDTD)
    parser.parse(open(FICHEROCONFIG))
    TAGS = ParserDTD.get_tags()
    return TAGS

CONFIG = {}
CONFIG = readficheroconfig()
SERVER = CONFIG["uaserver_ip"]
PORT_SIP = int(CONFIG["uaserver_puerto"])
AUDIO = CONFIG["audio_path"]


#INFORMACIÓN QUE EXTRAEREMOS DEL SDP DEL CLIENTE
PORT_RTP = 23032
SERVER_RTP = "127.0.0.1"
#INFORMACIÓN QUE EXTRAEREMOS DEL SDP DEL CLIENTE
COMANDO = './mp32rtp -i ' + SERVER_RTP + ' -p ' + str(PORT_RTP) + ' < ' + AUDIO
FICHEROLOG = CONFIG["log_path"]

def tolog(type,traza,direccion):
    fecha = time.strftime('%Y%m%d%H%M%S',time.gmtime(time.time()))
    traza = traza.replace("\r\n", " ")
    if type == "interna":
        trazatolog = fecha + " " + traza +"\r\n"
        ficherolog.write(trazatolog)
    elif type == "envio":
        trazatolog = fecha + " Sent to " + direccion[0] + ":" + str(direccion[1]) + " " + traza + "\r\n"
        ficherolog.write(trazatolog)
    elif type == "recivo":
        trazatolog = fecha + " Received from " + direccion[0] + ":" + str(direccion[1]) + " " + traza + "\r\n"
        ficherolog.write(trazatolog)

class SIPHandler(SocketServer.DatagramRequestHandler):
    """
    SIP server class
    """

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            mensaje =""
            line = self.rfile.read()
            if line != "":
                if "\r\n\r\n" in line:
                    print "El cliente nos manda " + line         
                    line = line.split()
                    if ('sip:' in line[1][:4]) and (line[2] == "SIP/2.0") \
                        and ('@' in line[1]):
                        tolog("recivo",( line[0]+ " " + line[1]), self.client_address)
                        if line[0] == "INVITE":
                            mensaje = "SIP/2.0 100 Trying\r\n\r\nSIP/2.0 180 Ringing\r\n\r\nSIP/2.0 200 OK\r\n\r\n"
                        elif line[0] == "ACK":
                            print "Comienza el RTP " + COMANDO
                            os.system(COMANDO)
                            tolog("envio", "Comienza el envio de RTP", self.client_address)
                            print "La canción ha terminado"
                        elif line[0] == "BYE":
                            mensaje = "SIP/2.0 200 OK\r\n\r\n"
                        elif line[0] not in METODOS_PERMITIDOS:
                            mensaje = "SIP/2.0 405 Method Not Allowed\r\n\r\n"
                    else:
                        mensaje = "SIP/2.0 400 Bad Request\r\n\r\n"
                else:
                    mensaje = "SIP/2.0 400 Bad Request\r\n\r\n"
                if mensaje != "":    
                    self.wfile.write(mensaje)
                    tolog("envio", mensaje, self.client_address)      
            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

if __name__ == "__main__":
    ficherolog = open(FICHEROLOG, "a")
    tolog("interna","Starting...","")
    # Creamos servidor y escuchamos
    serv = SocketServer.UDPServer(("", PORT_SIP), SIPHandler)
    print "Listening..."
    tolog("interna","Listening...","")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print "Programa Abortado"
        tolog("interna","Finishing\r\n\r\n","")
        ficherolog.close()