#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

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

FICHEROCONFIG = sys.argv[1]
CONFIG = readficheroconfig(FICHEROCONFIG)
PORT = int(CONFIG["server_puerto"])
NAME = CONFIG["server_name"]
FICHEROLOG = CONFIG["log_path"]
FICHERODATABASE = CONFIG["database_path"]
PUERTO_CLIENT = {}
METODOS_PERMITIDOS = ["REGISTER", "INVITE", "BYE"]
REGISTRO = {}

tolog(FICHEROLOG, "interna", "Starting...", "")


def restablecer_usuarios(fichero, REGISTRO):
    """
    Implementa el requisito avanzado "Restablecer Usuarios Conectados"
    leyendo del fichero correspondiente de la configuración
    del proxy_registrar.
    """
    ficheroregistro = open(fichero, "r")
    for frase in ficheroregistro:
        frase = frase.split()
        if len(frase) >= 5:
            username = frase[0]
            if username != "User":
                REGISTRO[username] = [frase[1], frase[2], frase[4], frase[3]]
    ficheroregistro.close()


class SIPRegisterHandler(SocketServer.DatagramRequestHandler):

    def borrar_caducados(self, registro):
        """
        Borra los usuarios presentes en el registro cuyo fecha
        de caducidad haya llegado
        """
        self.lista_aux = []
        for key in registro:
            fecha = registro[key][3]
            expires = registro[key][2]
            if time.time() >= float(fecha) + float(expires):
                self.lista_aux.append(key)
        for key in self.lista_aux:
            del registro[key]

    def register2file(self, registro):
        """
        Imprime en el fichero "registered.txt" el contenido del registro
        de usuarios
        """
        fichero = open("registered.txt", "w")
        fichero.write("User \t IP \t Puerto \t Fecha \t Expires \n")
        for key in registro:
            fichero.write(key + " " + registro[key][0] \
                + " " + registro[key][1] + " ")
            expires = registro[key][2]
            fecha = registro[key][3]
            fichero.write(str(fecha) + " " + str(expires) + "\n")

    def handle(self):

        """
        Recive y procesa todos los mensajes recividos por el servidor del tipo
        REGISTER.
        Introduce en el registro aquellos usuarios cuya petición sea valida y
        borra aquellos que manden una petición con el campo Expires = 0.
        """
        self.borrar_caducados(REGISTRO)
        self.register2file(REGISTRO)
        print "Petición recibida del Cliente: "
        print "IP:" + str(self.client_address[0]),
        print " Puerto: " + str(self.client_address[1])
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            mensaje = ""
            line = self.rfile.read()
            if line != "":
                if "\r\n\r\n" in line:
                    print "El cliente nos manda " + line
                    mensaje_reenviar = line
                    line = line.split()
                    if ('sip:' in line[1][:4]) and (line[2] == "SIP/2.0") \
                        and ('@' in line[1]):
                        tolog(FICHEROLOG, "recivo", mensaje_reenviar,\
                            self.client_address)
                        if line[0] == "INVITE":
                            line[1] = line[1].split(":")
                            #Compruebo que ambos clientes esten registrados
                            if str(line[1][1]) in REGISTRO:
                                IP_CLIENT = self.client_address[0]
                                PUERTO_CLIENT["client"] = self.client_address[1]
                                USERNAME_CLIENT = line[6].split("=")[1]
                                if USERNAME_CLIENT in REGISTRO:
                                    #Realizo el reenvion hacia el servidor que corresponda
                                    PORT_REENVIO = int(REGISTRO[str(line[1][1])][1])
                                    IP_REENVIO = REGISTRO[str(line[1][1])][0]
                                    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                                    my_socket.connect((IP_REENVIO, PORT_REENVIO))
                                    my_socket.send(mensaje_reenviar)
                                    tolog(FICHEROLOG, "envio", mensaje_reenviar, [IP_REENVIO, PORT_REENVIO])
                                    PUERTO_CLIENT["client"] = self.client_address[1]
                                    #Espero respuesta del servidor
                                    try:
                                        respuesta = my_socket.recv(1024)
                                        print "Respuesta del servidor:", respuesta
                                    except socket.error:
                                        fecha = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
                                        error = " Error: No server listening at " + IP_REENVIO + " port " + str(PORT_REENVIO)
                                        print fecha + error
                                        tolog(FICHEROLOG, "interna", error, "")
                                        respuesta = "SIP/2.0 404 User Not Found"

                                    print "Reenvio al cliente."
                                    self.wfile.write(respuesta)
                                else:
                                    #Respuesta correspondiente a la petición de/hacia un usuario no registrado
                                    mensaje = "SIP/2.0 404 User Not Found"
                            else:
                                mensaje = "SIP/2.0 404 User Not Found"
                        elif line[0] == "REGISTER":
                            #Procedo al intrudir al cliente que nos envia el REGISTER en el registro de usuarios.
                            line[1] = line[1].split(":")
                            self.wfile.write(line[2] + " 200 OK\r\n\r\n")
                            if line[4] != "0":
                                fecharegistro = time.time()
                                REGISTRO[line[1][1]] = [str(self.client_address[0]), line[1][2], line[4], fecharegistro]
                            else:
                                #Si el valor del Expires del REGISTER es igual a 0, da de baja a ese usuario
                                if line[1][1] in REGISTRO:
                                    del REGISTRO[line[1][1]]
                        elif line[0] == "ACK":
                            line[1] = line[1].split(":")
                            PORT_REENVIO = int(REGISTRO[str(line[1][1])][1])
                            IP_REENVIO = REGISTRO[str(line[1][1])][0]
                            #Reenvio del ACK
                            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            my_socket.connect((IP_REENVIO, PORT_REENVIO))
                            my_socket.send(mensaje_reenviar)
                            tolog(FICHEROLOG, "envio", mensaje_reenviar, [IP_REENVIO, PORT_REENVIO])
                        elif line[0] == "BYE":
                            user = str(line[1])
                            user = user.split(":")
                            if user[1] in REGISTRO:
                                line[1] = line[1].split(":")
                                PORT_REENVIO = int(REGISTRO[str(line[1][1])][1])
                                IP_REENVIO = REGISTRO[str(line[1][1])][0]
                                #Reenvio del BYE
                                my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                                my_socket.connect((IP_REENVIO, PORT_REENVIO))
                                my_socket.send(mensaje_reenviar)
                                tolog(FICHEROLOG, "envio", mensaje_reenviar, [IP_REENVIO, PORT_REENVIO])
                                try:
                                    #Espero la respuesta del servidor
                                    respuesta = my_socket.recv(1024)
                                    print "Respuesta del servidor:", respuesta
                                except socket.error:
                                    fecha = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
                                    error = " Error: No server listening at " + IP_REENVIO + " port " + str(PORT_REENVIO)
                                    print fecha + error
                                    tolog(FICHEROLOG, "interna", error, "")
                                    respuesta = "SIP/2.0 404 User Not Found"
                                print "Reenvio al cliente"
                                self.wfile.write(respuesta)
                            else:
                                respuesta = "SIP/2.0 404 User Not Found"
                                self.wfile.write(respuesta)

                        elif line[0] not in METODOS_PERMITIDOS:
                            #Mensaje de respuesta correspondiente al recibir un mensaje con un método no permitido
                            mensaje = "SIP/2.0 405 Method Not Allowed\r\n\r\n"
                else:
                    mensaje = "SIP/2.0 400 Bad Request\r\n\r\n"
                self.borrar_caducados(REGISTRO)
                self.register2file(REGISTRO)
                if mensaje != "":
                    #Envio del mensaje correspondiente cuando sea necesario
                    self.wfile.write(mensaje)
                    tolog(FICHEROLOG, "envio", mensaje, self.client_address)
            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

if __name__ == "__main__":
    #Restablecimiento de usuarios conectados presentes en el fichero.
    restablecer_usuarios(FICHERODATABASE, REGISTRO)
    # Creamos servidor y escuchamos
    serv = SocketServer.UDPServer(("", PORT), SIPRegisterHandler)
    print "Server " + NAME + " listening at port " + str(PORT) + "..."
    serv.serve_forever()
