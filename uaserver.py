#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import os
import time
import sys
import SocketServer


class SessionHandler(ContentHandler):

    def __init__(self):  # Iniciamos
        self.lista = []

    def startElement(self, name, attrs):  # Tomamos los tags como en P4

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


class EchoHandler(SocketServer.DatagramRequestHandler):  # Igual a la P6

    """
    Echo server class
    """

    def handle(self):  # Recibimos del cliente,dependiendo del metodo actuamos
        while 1:
            line = self.rfile.read()
            print line
            metodo = line.split(" ")[0]  # Metodo introducido.

            if metodo == "INVITE":  # El Registrer lo consideraremo en el proxy
                Log1 = etiquetas[4]
                Log1 = Log1["path"]
                Log1 = open(Log1, "a")  # Abrimos el log con el nombre del xml.
                Log1.write(
                    "__________________________________________" + "\r\n")
                           # Separacion en el log

                Tiempo_log = time.strftime('%Y­%m­%d %H:%M:%S',
                                           time.gmtime(time.time()))
                Log1.write(Tiempo_log[:4])
                Log1.write(Tiempo_log[6:8])
                Log1.write(Tiempo_log[10:12])
                Log1.write(Tiempo_log[13:15])
                Log1.write(Tiempo_log[16:18])
                Log1.write(Tiempo_log[19:21])

                Log1.write(" Received from ")
                           # Extraemos IP y Puerto del proxy.
                Proxy_stats = etiquetas[3]
                Puerto_Proxy = Proxy_stats["puerto"]
                Proxy_IP = Proxy_stats["ip"]

                Log1.write(Proxy_IP)
                Log1.write(":")
                Log1.write(Puerto_Proxy)
                Log1.write(": ")
                Message = line.split("\r\n")
                if len(Message) == 9:  # EL Description con mismos elementos
                    Log1.write(Message[0])
                    Log1.write(" ")
                    Log1.write(Message[1])
                    Log1.write(" ")
                    Log1.write(Message[2])
                    Log1.write(" ")
                    Log1.write(Message[3])
                    Log1.write(" ")
                    Log1.write(Message[4])
                    Log1.write(" ")
                    Log1.write(Message[5])
                    Log1.write(" ")
                    Log1.write(Message[6])
                    Log1.write(" ")
                    Log1.write(Message[7])
                    Log1.write("\r\n")

                    Tiempo_log = time.strftime('%Y­%m­%d %H:%M:%S',
                                               time.gmtime(time.time()))
                    Log1.write(Tiempo_log[:4])
                    Log1.write(Tiempo_log[6:8])
                    Log1.write(Tiempo_log[10:12])
                    Log1.write(Tiempo_log[13:15])
                    Log1.write(Tiempo_log[16:18])
                    Log1.write(Tiempo_log[19:21])

                    Log1.write(" Sent to ")  # Puerto e IP del proxy.
                    Log1.write(Proxy_IP)
                    Log1.write(":")
                    Log1.write(Puerto_Proxy)
                    Log1.write(":")
                    self.wfile.write("SIP/2.0 100 Trying\r\n")  # Respuestas
                    self.wfile.write("SIP/2.0 180 Ringing\r\n")
                    self.wfile.write("SIP/2.0 200 OK\r\n")

                    self.wfile.write("Content-Type: application/sdp\r\n\r\n")
                    self.wfile.write("v=0\r\n")  # Completamos el Description
                    Usuario = etiquetas[0]
                    Usuario = Usuario["username"]
                    Direccion = etiquetas[1]
                    Ip = Direccion["ip"]
                    self.wfile.write("o=" + Usuario + " " + Ip + "\r\n")
                    self.wfile.write("s=misesion\r\n")
                    self.wfile.write("t=0\r\n")
                    PuertoRTP = etiquetas[2]
                    PuertoRTP = PuertoRTP["puerto"]
                    self.wfile.write("m=audio " + PuertoRTP + " RTP\r\n")

                    Log1.write(" SIP/2.0 100 Trying")
                               # La misma info en el log.
                    Log1.write(" SIP/2.0 180 Ringing")
                    Log1.write(" SIP/2.0 200 OK")
                    Log1.write(" Content-Type: application/sdp")
                    Log1.write(" v=0")
                    Log1.write(" o=" + Usuario + " " + Ip)
                    Log1.write(" s=misesion")
                    Log1.write(" t=0")
                    Log1.write("m=audio " + PuertoRTP + " RTP\r\n")
                    Log1.close()

                    Usuario1 = line.split("o=")[1]  # Separamos la IP y puerto
                    Usuario1 = Usuario1.split(" ")[0]
                    Ip1 = line.split("o=")[1]
                    Ip1 = Ip1.split(" ")[1]
                    Ip1 = Ip1.split("\r\n")[0]
                    Puerto1 = line.split("m=")[1]
                    Puerto1 = Puerto1.split(" ")[1]
                    Lista = [Ip1, Puerto1]
                    Description[
                        Usuario1] = Lista  # Pasan al diccionario los datos

                else:
                    self.wfile.write("SIP/2.0 400 Bad Request\r\n")

            elif metodo == "ACK":

                for User in Description:
                    Log1 = etiquetas[4]
                    Log1 = Log1["path"]
                    Log1 = open(Log1, "a")
                                # ABrimos el log y vamos appendiendo
                    Lista = Description[
                        User]  # Para transmicion RTP puerto e IP
                    Cancion = etiquetas[5]
                    Cancion = Cancion["path"]  # Cancion.mp3

                    Tiempo_log = time.strftime('%Y­%m­%d %H:%M:%S',
                                               time.gmtime(time.time()))
                    Log1.write(Tiempo_log[:4])
                    Log1.write(Tiempo_log[6:8])
                    Log1.write(Tiempo_log[10:12])
                    Log1.write(Tiempo_log[13:15])
                    Log1.write(Tiempo_log[16:18])
                    Log1.write(Tiempo_log[19:21])

                    Log1.write(" Received from ")  # Recibimos del proxy
                    Proxy_stats = etiquetas[3]
                    Proxy_IP = Proxy_stats["ip"]
                    Puerto_Proxy = Proxy_stats["puerto"]
                    Log1.write(Proxy_IP)
                    Log1.write(":")
                    Log1.write(Puerto_Proxy)
                    Log1.write(": ")
                    Log1.write(line)

                    Tiempo_log = time.strftime('%Y­%m­%d %H:%M:%S',
                                               time.gmtime(time.time()))
                    Log1.write(Tiempo_log[:4])  # repetimos bloque temporal RTP
                    Log1.write(Tiempo_log[6:8])
                    Log1.write(Tiempo_log[10:12])
                    Log1.write(Tiempo_log[13:15])
                    Log1.write(Tiempo_log[16:18])
                    Log1.write(Tiempo_log[19:21])

                    Log1.write(" Beginning RTP transfer...\r\n")  # Igual a P6
                    aEjecutar = "./mp32rtp -i " + Lista[0] + " -p " + Lista[1]
                    aEjecutar += " < " + Cancion
                    print "Vamos a ejecutar", aEjecutar
                    os.system(aEjecutar)

                    Tiempo_log = time.strftime('%Y­%m­%d %H:%M:%S',
                                               time.gmtime(time.time()))
                    Log1.write(Tiempo_log[:4])  # FInalizacion RTP.
                    Log1.write(Tiempo_log[6:8])
                    Log1.write(Tiempo_log[10:12])
                    Log1.write(Tiempo_log[13:15])
                    Log1.write(Tiempo_log[16:18])
                    Log1.write(Tiempo_log[19:21])
                    Log1.write(" Ending RTP transfer.\r\n")
                    Log1.close()

            elif metodo == "BYE":

                Log1 = etiquetas[4]  # Abrimos el log as always.
                Log1 = Log1["path"]
                Log1 = open(Log1, "a")

                Tiempo_log = time.strftime('%Y­%m­%d %H:%M:%S',
                                           time.gmtime(time.time()))
                Log1.write(Tiempo_log[:4])  # Bloque de recepcion dl Proxy
                Log1.write(Tiempo_log[6:8])
                Log1.write(Tiempo_log[10:12])
                Log1.write(Tiempo_log[13:15])
                Log1.write(Tiempo_log[16:18])
                Log1.write(Tiempo_log[19:21])
                Log1.write(" Received from ")
                Proxy_stats = etiquetas[3]
                Proxy_IP = Proxy_stats["ip"]
                Puerto_Proxy = Proxy_stats["puerto"]
                Log1.write(Proxy_IP)
                Log1.write(":")
                Log1.write(Puerto_Proxy)
                Log1.write(": ")
                Log1.write(line)

                self.wfile.write("SIP/2.0 200 OK\r\n")

                Tiempo_log = time.strftime('%Y­%m­%d %H:%M:%S',
                                           time.gmtime(time.time()))
                Log1.write(Tiempo_log[:4])  # Bloque para indicar el envio.
                Log1.write(Tiempo_log[6:8])
                Log1.write(Tiempo_log[10:12])
                Log1.write(Tiempo_log[13:15])
                Log1.write(Tiempo_log[16:18])
                Log1.write(Tiempo_log[19:21])
                Log1.write(" Sent to ")
                Proxy_stats = etiquetas[3]
                Proxy_IP = Proxy_stats["ip"]
                Puerto_Proxy = Proxy_stats["puerto"]
                Log1.write(Proxy_IP)
                Log1.write(":")
                Log1.write(Puerto_Proxy)
                Log1.write(": ")
                Log1.write("SIP/2.0 200 OK\r\n")

                Tiempo_log = time.strftime('%Y­%m­%d %H:%M:%S',
                                           time.gmtime(time.time()))
                Log1.write(Tiempo_log[:4])  # Bloque temporal para finalizacion
                Log1.write(Tiempo_log[6:8])
                Log1.write(Tiempo_log[10:12])
                Log1.write(Tiempo_log[13:15])
                Log1.write(Tiempo_log[16:18])
                Log1.write(Tiempo_log[19:21])
                Log1.write(" Finishing.")
            elif metodo != "REGISTER" and metodo != "INVITE" and \
                    metodo != "BYE" and metodo:  # Comprobamos el metodo.
                self.wfile.write("SIP/2.0 405 Method Not Allowed\r\n")

            if not line:
                break

if __name__ == "__main__":

    if len(sys.argv) != 2:  # Comprobamos los parametros introducidos.
        sys.exit("Usage: python uaserver.py config")

    parser = make_parser()  # Sacamos las etiquetas
    cHandler = SessionHandler()
    parser.setContentHandler(cHandler)
    etiquetas = cHandler.get_tags()
    config = sys.argv[1]

    try:
        parser.parse(open(config))  # Comprobamos que sea leible el config
    except:
        sys.exit("Usage: python uaserver.py config")

    Direccion = etiquetas[1]  # Donde tenemos IP y puerto.

    Description = {}  # Abrimos un diccionario para los datos de la SDP

    Ip = Direccion["ip"]  # Igual que en la P6, escuchamos.
    Puerto = Direccion["puerto"]
    serv = SocketServer.UDPServer((Ip, int(Puerto)), EchoHandler)
    print "Listening..."
    serv.serve_forever()
