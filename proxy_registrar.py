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

class EchoHandler(SocketServer.DatagramRequestHandler):  # Segun el metodo, actua

    def handle(self):
        while 1:
            line = self.rfile.read()
            print line
            Metodo = line.split(" ")[0]
            if Metodo == "REGISTER":  # EL registrer por separado del uaserver
                Message = line.split("\r\n")
                if len(Message) == 3:  # Nos aseguramos del formato del Register
                    Iter = 0
                    for User in UsuariosReg:  # Revisamos que no haya expirado
                        if float(UsuariosReg[Iter][3]) + \
                                float(UsuariosReg[Iter][4]) < time.time():
                            del UsuariosReg[Iter]
                        Iter = Iter + 1
                    Info = []  # Lista para agrupar los datos del user agent
                    Usuario = line.split(" ")[1]
                    Usuario = Usuario.split(":")[1]
                    Info.append(Usuario)  # incluimos los datos del usuario
                    Info.append("127.0.0.1")
                    Puerto = line.split(" ")[1]
                    Puerto = Puerto.split(":")[2]
                    Info.append(Puerto)  # EL puerto
                    Tiempo_Registro = time.time()
                    Info.append(Tiempo_Registro)  # Tiempo de registro
                    Time_Expiracion = line.split(" ")[-1][:-2]
                    Info.append(Time_Expiracion)  # Tiempo de Expiracion

                    if Time_Expiracion != "0":  # Si no ha expirado el tiempo de reg
                        UsuariosReg.append(Info)  # Info del usuario
                        Database = etiquetas[1]
                        Database = Database["path"]
                        Database = open(
                            Database, "w")  # Escribimos cabecera de cada usuario
                        Database.write("Usuario\tIP\tPuerto\t" +
                                       "Fecha de Registro\tTiempo de expiracion\r\n")  # \t paralelo
                        for User in UsuariosReg:
                            for Elemento1 in User:  # Ponemos los datos de cada user
                                Database.write(str(Elemento1) + "\t")
                            Database.write("\r\n")
                        Database.close()  # Cerramos el log
                        Found = True  # Booleano para indicar que esta el usuario buscado
                    else:  # Tiempo de registro de usuario expirado
                        Iter = 0
                        Found = False
                        for User in UsuariosReg:  # Eliminamos los datos de los exp
                            if User[0] == Usuario:
                                del UsuariosReg[Iter]
                                Found = True
                            Iter = Iter + 1
                        Database = etiquetas[1]
                        Database = Database["path"]
                        Database = open(Database, "w")  # Igual que antes
                        Database.write("Usuario\tIP\tPuerto\t" +
                                       "Fecha de Registro\tTiempo de expiracion\r\n")
                        for User in UsuariosReg:
                            for Elemento1 in User:
                                Database.write(str(Elemento1) + "\t")
                            Database.write("\r\n")
                        Database.close()

                    Log1 = etiquetas[2]
                    Log1 = Log1["path"]
                    Log1 = open(Log1, "a")
                    Tiempo_log = time.strftime('%Y­%m­%d %H:%M:%S',
                                               time.gmtime(time.time()))
                    Log1.write(
                        Tiempo_log[:4])  # Bloque temporal para indicar el recibimiento del Reg
                    Log1.write(Tiempo_log[6:8])
                    Log1.write(Tiempo_log[10:12])
                    Log1.write(Tiempo_log[13:15])
                    Log1.write(Tiempo_log[16:18])
                    Log1.write(Tiempo_log[19:21])
                    Log1.write(" Received from 127.0.0.1:")
                    Log1.write(Puerto)
                    Log1.write(": ")
                    Message = line.split("\r\n")
                    Log1.write(Message[0])
                    Log1.write(" ")
                    Log1.write(Message[1])
                    Log1.write("\r\n")

                    Tiempo_log = time.strftime('%Y­%m­%d %H:%M:%S',
                                               time.gmtime(time.time()))
                    Log1.write(
                        Tiempo_log[:4])  # Bloque temporal para indicar la respuesta
                    Log1.write(Tiempo_log[6:8])
                    Log1.write(Tiempo_log[10:12])
                    Log1.write(Tiempo_log[13:15])
                    Log1.write(Tiempo_log[16:18])
                    Log1.write(Tiempo_log[19:21])
                    Log1.write(" Sent to 127.0.0.1:")
                    Log1.write(Puerto)
                    Log1.write(": ")
                    if Found:  # SI el usuario esta en el Reg sin expirar
                        Log1.write("SIP/2.0 200 OK\r\n")
                        self.wfile.write("SIP/2.0 200 OK\r\n")
                    else:  # Usuario
                        Log1.write("SIP/1.0 404 User Not Found\r\n")
                        self.wfile.write("SIP/1.0 404 User Not Found\r\n")
                    Log1.close()
                else:
                    self.wfile.write(
                        "SIP/2.0 400 Bad Request\r\n")  # Mal formado

            elif Metodo == "INVITE":
                Message = line.split(
                    "\r\n")  # Separamos los elementos del invite
                if len(Message) == 9:  # Deberiamos tener 9 elementos si bien formado
                    Iter = 0
                    for User in UsuariosReg:  # Se revisa la expiracion primero
                        if float(UsuariosReg[Iter][3]) + \
                                float(UsuariosReg[Iter][4]) < time.time():
                            del UsuariosReg[Iter]
                        Iter = Iter + 1
                    Aim = line.split(" ")[1]  # Separamos puerto e IP
                    Aim = Aim.split(":")[1]
                    Found = False
                    for User in UsuariosReg:
                        if User[0] != Aim:
                            IP_origen = User[1]
                            Puerto_origen = User[2]
                            Found = True
                    Log1 = etiquetas[2]
                    Log1 = Log1["path"]
                    Log1 = open(Log1, "a")  # ABrimos el log para invite

                    if Found:
                        Tiempo_log = time.strftime('%Y­%m­%d %H:%M:%S',
                                                   time.gmtime(time.time()))
                        Log1.write(
                            Tiempo_log[:4])  # BLoque temporal para el recibimiento
                        Log1.write(Tiempo_log[6:8])
                        Log1.write(Tiempo_log[10:12])
                        Log1.write(Tiempo_log[13:15])
                        Log1.write(Tiempo_log[16:18])
                        Log1.write(Tiempo_log[19:21])
                        Log1.write(" Received from ")
                        Log1.write(IP_origen)
                        Log1.write(":")
                        Log1.write(Puerto_origen)
                        Log1.write(": ")
                        Log1.write(Message[0])  # Igual que en el cliente.
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
                        Iter = 0
                        Objetivo = False  # Booleano para diferenciar destinatario
                        for User in UsuariosReg:
                            if UsuariosReg[Iter][0] == Aim:  # SI coincide sacamos puerto.
                                Objetivo = True
                                SERVER = UsuariosReg[Iter][1]
                                PORT = int(UsuariosReg[Iter][2])
                                try:
                                    my_socket = socket.socket(socket.AF_INET,
                                                              socket.SOCK_DGRAM)  # Igual a P6
                                    my_socket.setsockopt(socket.SOL_SOCKET,
                                                         socket.SO_REUSEADDR, 1)
                                    my_socket.connect((SERVER, PORT))
                                    my_socket.send(line)
                                    data = my_socket.recv(1024)

                                    print data

                                    my_socket.close(
                                    )  # Necesario cesar para evitar errores.
                                except:  # Si no funciona es que no hay servidor escuchando.
                                    Tiempo_log = time.strftime(
                                        '%Y­%m­%d %H:%M:%S',
                                        time.gmtime(time.time()))
                                    Log1.write(
                                        Tiempo_log[:4])  # Para indicar el error
                                    Log1.write(Tiempo_log[6:8])
                                    Log1.write(Tiempo_log[10:12])
                                    Log1.write(Tiempo_log[13:15])
                                    Log1.write(Tiempo_log[16:18])
                                    Log1.write(Tiempo_log[19:21])
                                    Log1.write(" Error: no server ")
                                    Log1.write("listening at "
                                               + SERVER + " port " + str(PORT) + "\r\n")
                                    Tiempo_log = time.strftime(
                                        '%Y­%m­%d %H:%M:%S',
                                        time.gmtime(time.time()))
                                    Log1.write(
                                        Tiempo_log[:4])  # Para indicar el cierre.
                                    Log1.write(Tiempo_log[6:8])
                                    Log1.write(Tiempo_log[10:12])
                                    Log1.write(Tiempo_log[13:15])
                                    Log1.write(Tiempo_log[16:18])
                                    Log1.write(Tiempo_log[19:21])
                                    Log1.write(" Finishing.")
                                    sys.exit("Error: no server listening at "
                                             + SERVER + " port " + str(PORT))
                                self.wfile.write(
                                    data)  # Si si tenemos servidor escuchando seguimos

                                Tiempo_log = time.strftime(
                                    '%Y­%m­%d %H:%M:%S',
                                    time.gmtime(time.time()))
                                Log1.write(
                                    Tiempo_log[:4])  # Igual al cliente, ponemos los elementos de la SDP
                                Log1.write(Tiempo_log[6:8])
                                Log1.write(Tiempo_log[10:12])
                                Log1.write(Tiempo_log[13:15])
                                Log1.write(Tiempo_log[16:18])
                                Log1.write(Tiempo_log[19:21])
                                Log1.write(" Sent to ")
                                Log1.write(SERVER)
                                Log1.write(":")
                                Log1.write(str(PORT))
                                Log1.write(": ")
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

                                Tiempo_log = time.strftime(
                                    '%Y­%m­%d %H:%M:%S',
                                    time.gmtime(time.time()))
                                Log1.write(
                                    Tiempo_log[:4])  # Exactamente igual para recibimiento.
                                Log1.write(Tiempo_log[6:8])
                                Log1.write(Tiempo_log[10:12])
                                Log1.write(Tiempo_log[13:15])
                                Log1.write(Tiempo_log[16:18])
                                Log1.write(Tiempo_log[19:21])
                                Log1.write(" Received from ")
                                Log1.write(SERVER)
                                Log1.write(":")
                                Log1.write(str(PORT))
                                Log1.write(": ")
                                Message = data.split("\r\n")
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
                                Log1.write(" ")
                                Log1.write(Message[8])
                                Log1.write(" ")
                                Log1.write(Message[9])
                                Log1.write("\r\n")
                            Iter = Iter + 1
                        if Objetivo:  # La otra SDP al destinatario
                            Tiempo_log = time.strftime('%Y­%m­%d %H:%M:%S',
                                                       time.gmtime(time.time()))
                            Log1.write(Tiempo_log[:4])
                            Log1.write(Tiempo_log[6:8])
                            Log1.write(Tiempo_log[10:12])
                            Log1.write(Tiempo_log[13:15])
                            Log1.write(Tiempo_log[16:18])
                            Log1.write(Tiempo_log[19:21])
                            Log1.write(" Sent to ")
                            Log1.write(IP_origen)
                            Log1.write(":")
                            Log1.write(Puerto_origen)
                            Log1.write(": ")
                            Message = data.split("\r\n")
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
                            Log1.write(" ")
                            Log1.write(Message[8])
                            Log1.write(" ")
                            Log1.write(Message[9])
                            Log1.write("\r\n")
                            Log1.close()
                        else:  # Si no esta en la databse el destinatario
                            Tiempo_log = time.strftime('%Y­%m­%d %H:%M:%S',
                                                       time.gmtime(time.time()))
                            Log1.write(Tiempo_log[:4])
                            Log1.write(Tiempo_log[6:8])
                            Log1.write(Tiempo_log[10:12])
                            Log1.write(Tiempo_log[13:15])
                            Log1.write(Tiempo_log[16:18])
                            Log1.write(Tiempo_log[19:21])
                            Log1.write(" Error: User Not Found\r\n")
                            self.wfile.write("SIP/2.0 404 User Not Found\r\n")
                            Log1.close()
                    else:  # Same case.

                        Tiempo_log = time.strftime('%Y­%m­%d %H:%M:%S',
                                                   time.gmtime(time.time()))
                        Log1.write(Tiempo_log[:4])
                        Log1.write(Tiempo_log[6:8])
                        Log1.write(Tiempo_log[10:12])
                        Log1.write(Tiempo_log[13:15])
                        Log1.write(Tiempo_log[16:18])
                        Log1.write(Tiempo_log[19:21])
                        Log1.write(" Error: User Not Found\r\n")
                        self.wfile.write("SIP/2.0 404 User Not Found\r\n")
                        Log1.close()
                else:
                    self.wfile.write(
                        "SIP/2.0 400 Bad Request\r\n")  # Mal formado

