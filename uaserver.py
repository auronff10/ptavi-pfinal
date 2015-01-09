#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase
"""
import sys
import SocketServer
import socket
import os.path
import os
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class ParserDTD(ContentHandler):

    def __init__(self):
        self.diccionario = {}
        self.tags = ['account', 'uaserver', 'rtpaudio',\
            'regproxy', 'log', 'audio', 'server', 'database']
        self.atributos = {
            'account': ['username', 'passwd'],
            'uaserver': ['ip', 'puerto'],
            'rtpaudio': ['puerto'],
            'regproxy': ['ip', 'puerto'],
            'log': ['path'],
            'audio': ['path'],
            'server': ['name', 'ip', 'puerto'],
            'database': ['path', 'passwdpath']
        }

    def startElement(self, name, attrs):
        datos = []
        if name in self.tags:
            for atributo in self.atributos[name]:
                self.diccionario[name + "_" + atributo] = attrs.get(atributo, "")

    def get_tags(self):
        return self.diccionario


def tolog(fichero, type, traza, direccion):
    ficherolog = open(fichero, "a")
    fecha = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
    traza = traza.replace("\r\n", " ")
    if type == "interna":
        trazatolog = fecha + " " + traza + "\r\n"
        ficherolog.write(trazatolog)
    elif type == "envio":
        trazatolog = fecha + " Sent to " + direccion[0]
        trazatolog += ":" + str(direccion[1]) + " " + traza + "\r\n"
        ficherolog.write(trazatolog)
    elif type == "recivo":
        trazatolog = fecha + " Received from " + direccion[0]
        trazatolog += ":" + str(direccion[1]) + " " + traza + "\r\n"
        ficherolog.write(trazatolog)

if __name__ == "__main__":
    FICHEROCONFIG = sys.argv[1]

    def readficheroconfig(fichero):
        parser = make_parser()
        parserdtd = ParserDTD()
        parser.setContentHandler(parserdtd)
        parser.parse(open(fichero))
        TAGS = parserdtd.get_tags()
        return TAGS

    METODOS_PERMITIDOS = ["INVITE", "BYE", "ACK"]

    #Datos de conexión

    if len(sys.argv) != 2:
        print "Usage: python server.py config"
        sys.exit()

    FICHEROCONFIG = sys.argv[1]
    CONFIG = {}
    CONFIG = readficheroconfig(FICHEROCONFIG)
    SERVER = CONFIG["uaserver_ip"]
    PORT_SIP = int(CONFIG["uaserver_puerto"])
    PORT_RTP = int(CONFIG["rtpaudio_puerto"])
    USER = CONFIG["account_username"]
    AUDIO = CONFIG["audio_path"]
    INFO_USER = {}
    FICHEROLOG = CONFIG["log_path"]
    SDP = "v=0\r\n" + "o=" + USER + "\r\n" + "s=misesion\r\n" + "m=audio " + str(PORT_RTP) + " RTP"
    CVLC = "cvlc rtp://@" + SERVER + ":" + str(PORT_RTP) + "&"

    class SIPHandler(SocketServer.DatagramRequestHandler):
        """
        SIP server class
        """

        def handle(self):
            # Escribe dirección y puerto del cliente (de tupla client_address)
            while 1:
                # Leyendo línea a línea lo que nos envía el cliente
                mensaje = ""
                line = self.rfile.read()
                if line != "":
                    if "\r\n\r\n" in line:
                        print "El cliente nos manda " + line
                        cabeceras = line.split("\r\n\r\n")[0]
                        sdp = line.split("\r\n\r\n")[1]
                        cabeceras = cabeceras.split()
                        sdp = sdp.split()
                        if ('sip:' in cabeceras[1][:4]) and (cabeceras[2] == "SIP/2.0") \
                            and ('@' in cabeceras[1]):
                            tolog(FICHEROLOG, "recivo", (cabeceras[0] + " " + cabeceras[1]), self.client_address)
                            if cabeceras[0] == "INVITE":
                                USERNAME_CLIENT = sdp[1].split("=")[1]
                                INFO_USER["user_name"] = USERNAME_CLIENT
                                INFO_USER["port"] = [sdp[5]]
                                SDP = "v=0\r\n" + "o=" + USERNAME_CLIENT + " " + SERVER + "\r\n" + "s=misesion\r\n" + "m=audio " + str(PORT_RTP) + " RTP"
                                mensaje = "SIP/2.0 100 Trying\r\n\r\nSIP/2.0 180 Ringing\r\n\r\n"
                                mensaje += "SIP/2.0 200 OK\r\nContent-Type: application/sdp\r\n\r\n"
                                mensaje += SDP
                                mensaje += "\r\n"
                            elif cabeceras[0] == "ACK":
                                USERNAME_CLIENT = cabeceras[1].split(":")[1]
                                SERVER_RTP = USERNAME_CLIENT.split("@")[1]
                                CLIENT_PORT_RTP = INFO_USER["port"][0]
                                COMANDO = './mp32rtp -i ' + SERVER_RTP + ' -p ' + str(CLIENT_PORT_RTP) + ' < ' + AUDIO
                                print "Comienza el RTP " + COMANDO
                                os.system(CVLC)
                                os.system(COMANDO)
                                tolog(FICHEROLOG, "envio", "Comienza el envio de RTP", [SERVER_RTP, str(CLIENT_PORT_RTP)])
                                print "La canción ha terminado"
                            elif cabeceras[0] == "BYE":
                                mensaje = "SIP/2.0 200 OK\r\n\r\n"
                            elif cabeceras[0] not in METODOS_PERMITIDOS:
                                mensaje = "SIP/2.0 405 Method Not Allowed\r\n\r\n"
                        else:
                            mensaje = "SIP/2.0 400 Bad Request\r\n\r\n"
                    else:
                        mensaje = "SIP/2.0 400 Bad Request\r\n\r\n"
                    if mensaje != "":
                        self.wfile.write(mensaje)
                        tolog(FICHEROLOG, "envio", mensaje, self.client_address)
                # Si no hay más líneas salimos del bucle infinito
                if not line:
                    break

    if __name__ == "__main__":
        tolog(FICHEROLOG, "interna", "Starting...", "")
        # Creamos servidor y escuchamos
        serv = SocketServer.UDPServer(("", PORT_SIP), SIPHandler)
        print "Listening..."
        tolog(FICHEROLOG, "interna", "Listening...", "")
        try:
            serv.serve_forever()
        except KeyboardInterrupt:
            print "Programa Abortado."
            tolog(FICHEROLOG, "interna", "Finishing...", "")
