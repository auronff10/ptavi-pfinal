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


METODOS_PERMITIDOS = ["INVITE", "BYE", "ACK"]

#Datos de conexión

if not os.path.exists(sys.argv[3]) or len(sys.argv) != 4:
    print "Usage: python server.py IP port audio_file"
    sys.exit()


SERVER = sys.argv[1]
PORT_SIP = int(sys.argv[2])
AUDIO = sys.argv[3]

PORT_RTP = 23032
SERVER_RTP = "127.0.0.1"
COMANDO = './mp32rtp -i ' + SERVER_RTP + ' -p ' + str(PORT_RTP) + ' < ' + AUDIO
FICHEROLOG = "log.txt"


def tolog(type,traza,direccion):
    fecha = time.strftime('%Y%m%d%H:%M%S',time.gmtime(time.time()))
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

class EchoHandler(SocketServer.DatagramRequestHandler):
    """
    Echo server class
    """

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            if line != "":
                if "\r\n\r\n" in line:
                    print "El cliente nos manda " + line         
                    line = line.split()
                    if ('sip:' in line[1][:4]) and (line[2] == "SIP/2.0") \
                        and ('@' in line[1]):
                        print line[0]+ " " + line[1]
                        tolog("recivo",( line[0]+ " " + line[1]), self.client_address)
                        if line[0] == "INVITE":
                            mensaje = "SIP/2.0 100 Trying\r\n\r\nSIP/2.0 180 Ringing\r\n\r\nSIP/2.0 200 OK\r\n\r\n"
                            self.wfile.write(mensaje)
                            tolog("envio", mensaje, self.client_address)
                        elif line[0] == "ACK":
                            print "Comienza el RTP " + COMANDO
                            os.system(COMANDO)
                            print "La canción ha terminado"
                        elif line[0] == "BYE":
                            self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
                        elif line[0] not in METODOS_PERMITIDOS:
                            self.wfile.write("SIP/2.0 405 Method \
                                Not Allowed\r\n\r\n")
                    else:
                        self.wfile.write("SIP/2.0 400 Bad Request\r\n\r\n")
                else:
                    self.wfile.write("SIP/2.0 400 Bad Request\r\n\r\n")
            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

if __name__ == "__main__":
    ficherolog = open(FICHEROLOG, "a")
    tolog("interna","Starting...","")
    # Creamos servidor y escuchamos
    serv = SocketServer.UDPServer(("", PORT_SIP), EchoHandler)
    print "Listening..."
    tolog("interna","Listening...","")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print "Programa Abortado"
        ficherolog.close()