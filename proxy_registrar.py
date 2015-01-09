#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor de eco
en UDP simple
"""

import SocketServer
import sys
from uaserver import ParserDTD
from uaserver import tolog
import time
import socket
from xml.sax import make_parser

if len(sys.argv) != 2:
    print "Usage: python proxy_registrar.py config"
    sys.exit()



def readficheroconfig(fichero):
    parser = make_parser()
    parserdtd = ParserDTD()
    parser.setContentHandler(parserdtd)
    parser.parse(open(fichero))
    TAGS = parserdtd.get_tags()
    return TAGS

def cabeceraproxy(mensaje, IP, PORT):
    #num_aleatorio = random
    cabeceraproxy = "Via:SIP/2.0/UDP" + IP + ":" + str(PORT) +";"
    cabeceraproxy += "branch="
    mensaje = mensaje.split("\r\n\r\n")


FICHEROCONFIG = sys.argv[1]


CONFIG = readficheroconfig(FICHEROCONFIG)
PORT = int(CONFIG["server_puerto"])
NAME = CONFIG["server_name"]
FICHEROLOG = CONFIG["log_path"]
FICHERODATABASE = CONFIG["database_path"]
PUERTO_CLIENT = {}

METODOS_PERMITIDOS =  ["REGISTER","INVITE", "BYE"]

REGISTRO = {}

tolog(FICHEROLOG, "interna","Starting...","")

def restablecer_usuarios(fichero, REGISTRO):
    ficheroregistro = open(fichero, "r")
    for frase in ficheroregistro: 
        frase = frase.split()
        username = frase[0]
        if username != "User":
            REGISTRO[username] = [frase[1], frase[2], frase[4], frase[3]]
    print REGISTRO
    ficheroregistro.close()


class SIPRegisterHandler(SocketServer.DatagramRequestHandler):
 
    def borrar_caducados(self, registro):
        """
        Borra los usuarios presentes en el registro cuyo fecha
        de caducidad haya llegado
        """
        self.lista_aux = []
        for key in registro:
            if time.time() >= float(registro[key][3]) + float(registro[key][2]):
                self.lista_aux.append(key)
        for key in self.lista_aux:
            del registro[key]

    def register2file(self, registro):
        """
        Imprime en el fichero "registered.txt" el contenido del registro
        de usuarios
        """
        fichero = open("registered.txt", "w")
        fichero.write("User \t IP \t Puerto \t Fecha \t Expires \n" )
        for key in registro:
            fichero.write(key + " " + registro[key][0] + " " + registro[key][1] + " ")
            expires = registro[key][2]
            fecha = registro[key][3]
            fichero.write(str(fecha) + " " + str(expires) + "\n")

    

    #ESTO PROBABLEMENTE VAYA FUERA ACUERDATE

    def reenvio(self,ip,puerto,mensaje):
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((ip, puerto))
        my_socket.send(mensaje)
        #my_socket.close()

    

    def handle(self):

        """
        Recive y procesa todos los mensajes recividos por el servidor del tipo
        REGISTER.

        Introduce en el registro aquellos usuarios cuya petición sea valida y
        borra aquellos que manden una petición con el campo Expires = 0.
        """

        self.borrar_caducados(REGISTRO)
        self.register2file(REGISTRO)


        print "Petición recibida del Cliente: ",
        print "IP:" + str(self.client_address[0]),
        print " Puerto: " + str(self.client_address[1])
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            mensaje =""
            line = self.rfile.read()
            if line != "":
                if "\r\n\r\n" in line:
                    print "El cliente nos manda " + line
                    mensaje_reenviar = line
                    line = line.split()
                    if ('sip:' in line[1][:4]) and (line[2] == "SIP/2.0") \
                        and ('@' in line[1]):
                        tolog(FICHEROLOG, "recivo",mensaje_reenviar, self.client_address)
                        if line[0] == "INVITE":
                            line[1] = line[1].split(":")
                            if REGISTRO.has_key(str(line[1][1])):
                                IP_CLIENT = self.client_address[0]
                                PUERTO_CLIENT["client"] = self.client_address[1]
                                USERNAME_CLIENT = line[6].split("=")[1]
                                if REGISTRO.has_key(USERNAME_CLIENT):
                                    PORT_REENVIO = int(REGISTRO[str(line[1][1])][1])
                                    IP_REENVIO = REGISTRO[str(line[1][1])][0]
                                    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                                    my_socket.connect((IP_REENVIO, PORT_REENVIO))
                                    my_socket.send(mensaje_reenviar)
                                    
                                    tolog(FICHEROLOG, "envio",mensaje_reenviar, [IP_REENVIO,PORT_REENVIO])
                                    PUERTO_CLIENT["client"] = self.client_address[1]
                                    try:
                                        respuesta= my_socket.recv(1024)
                                        print "RECIBO DEL SERVIDOR", respuesta
                                    except socket.error:
                                        fecha = time.strftime('%Y%m%d%H%M%S',time.gmtime(time.time()))
                                        error = " Error: No server listening at " + IP_REENVIO + " port " + str(PORT_REENVIO)
                                        print fecha +  error
                                        tolog(FICHEROLOG, "interna", error, "")
                                        respuesta = "SIP/2.0 404 User Not Found"

                                    print "REENVIO AL CLIENTE"
                                    self.wfile.write(respuesta)
                                else:
                                    mensaje ="SIP/2.0 404 User Not Found"
                            else:
                                mensaje ="SIP/2.0 404 User Not Found"


                        elif line[0] == "REGISTER":
                            line[1] = line[1].split(":")
                            self.wfile.write(line[2] + " 200 OK\r\n\r\n")
                            if line[4] != "0":
                                fecharegistro = time.time()
                                REGISTRO[line[1][1]] = [str(self.client_address[0]), line[1][2], line[4], fecharegistro]
                                print fecharegistro
                            else:
                                if line[1][1] in REGISTRO:
                                    del REGISTRO[line[1][1]]
                        elif line[0] == "ACK":
                            line[1] = line[1].split(":")
                            PORT_REENVIO = int(REGISTRO[str(line[1][1])][1])
                            IP_REENVIO = REGISTRO[str(line[1][1])][0]

                            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            my_socket.connect((IP_REENVIO, PORT_REENVIO))
                            my_socket.send(mensaje_reenviar)

                            tolog(FICHEROLOG, "envio",mensaje_reenviar, [IP_REENVIO,PORT_REENVIO])


                            #tolog("envio", "Comienza el envio de RTP", self.client_address)
                        elif line[0] == "BYE":
                            user = str(line[1])
                            user = user.split(":")
                            print self.client_address
                            if REGISTRO.has_key(user[1]):
                                line[1] = line[1].split(":")
                                PORT_REENVIO = int(REGISTRO[str(line[1][1])][1])
                                IP_REENVIO = REGISTRO[str(line[1][1])][0]

                                my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                                my_socket.connect((IP_REENVIO, PORT_REENVIO))
                                my_socket.send(mensaje_reenviar)

                                tolog(FICHEROLOG, "envio",mensaje_reenviar, [IP_REENVIO,PORT_REENVIO])


                                try:
                                    respuesta= my_socket.recv(1024)
                                    print "RECIBO DEL SERVIDOR", respuesta
                                except socket.error:
                                    fecha = time.strftime('%Y%m%d%H%M%S',time.gmtime(time.time()))
                                    error = " Error: No server listening at " + IP_REENVIO + " port " + str(PORT_REENVIO)
                                    print fecha +  error
                                    tolog(FICHEROLOG, "interna", error, "")
                                    respuesta = "SIP/2.0 404 User Not Found"

                                print "REENVIO AL CLIENTE"
                                self.wfile.write(respuesta)
                            else:
                                respuesta = "SIP/2.0 404 User Not Found"
                                self.wfile.write(respuesta)

                        elif line[0] not in METODOS_PERMITIDOS:
                            mensaje = "SIP/2.0 405 Method Not Allowed\r\n\r\n"
                    '''       
                    elif line[6] == "SIP/2.0" and line[7] == "200" and line[8] == "OK":
                        self.reenvio(self.client_address[0],PUERTO_CLIENT["client"] ,"AA")
                        #mensaje = "SIP/2.0 400 Bad Request\r\n\r\n"
                    '''    
                else:
                    mensaje = "SIP/2.0 400 Bad Request\r\n\r\n"
                self.borrar_caducados(REGISTRO)
                self.register2file(REGISTRO)
                print REGISTRO
                if mensaje != "":    
                    self.wfile.write(mensaje)
                    tolog(FICHEROLOG, "envio", mensaje, self.client_address)      
            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

if __name__ == "__main__":
    
    restablecer_usuarios(FICHERODATABASE,REGISTRO)
    
    # Creamos servidor de eco y escuchamos
    serv = SocketServer.UDPServer(("", PORT), SIPRegisterHandler)
    print "Server " + NAME + " listening at port " +  str(PORT) + "..."
    serv.serve_forever()
