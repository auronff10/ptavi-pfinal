#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa del user agent final
"""
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socket
import sys
import uaserver
import os
import time

if __name__ == "__main__":
    

    try:
        config = sys.argv[1]
        metodo = sys.argv[2]
        option = sys.argv[3]

    except IOError:
        print "Usage: python uaclient.py config method option"
        sys.exit()

    if len(sys.argv) != 4: # Revisamos que haya 4 inputs
        print "Usage: python uaclient.py config method option"
        sys.exit()

    if sys.argv[2] != "REGISTER" and sys.argv[2] != "INVITE" and sys.argv[2] != "BYE":
        sys.exit("Usage: python uaclient.py config method option")

    try:
        parser.parse(open(config)) # Podria ser que config no sea formato leible
    except IOError:
        print 'Usage: python uaclient.py config method option'
        sys.exit()

    parser = make_parser() # Sacamos los tags del xml como en la P3
    cHandler = uaserver.XMLHandler()
    parser.setContentHandler(cHandler)

    etiquetas = cHandler.get_tags() # Para identificar las etiquetas.
    
    Receiver = ""
    Log1 = etiquetas[4]
    Log1 = Log1["path"]
    Log1 = open(Log1, "a") # Abrimos el archivo del log
    Log1.write("______________________________________________________" + "\r\n")
    Tiempo_log = time.strftime('%Y­%m­%d %H:%M:%S', time.gmtime(time.time()))
    Log1.write(Tiempo_log[:4])  # Año
    Log1.write(Tiempo_log[6:8]) # Mes      
    Log1.write(Tiempo_log[10:12]) # Dia
    Log1.write(Tiempo_log[13:15]) # Horas
    Log1.write(Tiempo_log[16:18]) # Minutos
    Log1.write(Tiempo_log[19:21]) # Segundos
    Log1.write(" Starting...\r\n")
    
    Direccion = etiquetas[3] # La direccion  del server proxy
    SERVER = Direccion["ip"]
    PORT = int(Direccion["puerto"])

    if metodo == "REGISTER":

        Usuario = etiquetas[0] #Nombre de usuario dado en el xml
        Usuario = Usuario["username"]
        Direccion = etiquetas[1] # Puerto del usario dado en el xml
        Puerto = Direccion["puerto"]
        expires = sys.argv[3] # Si el metodo es REGISTER, deberiamos tener esto
        LINE = metodo + " sip:" + Usuario + ":" + Puerto + \
        " SIP/2.0\r\n" + "Expires: " + expires
        
        Tiempo_log = time.strftime('%Y­%m­%d %H:%M:%S', time.gmtime(time.time()))
        Log1.write(Tiempo_log[:4]) # Mismo esquema que antes
        Log1.write(Tiempo_log[6:8])
        Log1.write(Tiempo_log[10:12])
        Log1.write(Tiempo_log[13:15])
        Log1.write(Tiempo_log[16:18])
        Log1.write(Tiempo_log[19:21])
        Log1.write(" Sent to ")
        Log1.write(SERVER) # IP del proxy
        Log1.write(":")
        Log1.write(str(PORT)) # Puerto proxy elegido dado en el xml
        Log1.write(": ")
        Message = LINE.split("\r\n") # Info del usuario, metodo enviado arriba
        Log1.write(Message[0]) #Para poner ambas cosas en la misma linea del log
        Log1.write(" ")
        Log1.write(Message[1])
        Log1.write("\r\n")

    elif metodo == "INVITE":

        Usuario = etiquetas[0] 
        Usuario = Usuario["username"] # Usuario origen
        Direccion = etiquetas[1]
        Ip = Direccion["ip"] # IP del server.
        PuertoRTP = etiquetas[2] # Puerto donde tendremos el RTP
        PuertoRTP = PuertoRTP["puerto"]
        Receiver = sys.argv[3] # Dado el invite, este input seria el destino.
        LINE = metodo + " sip:" + Receiver + " SIP/2.0\r\n" + \
        "Content-Type: application/sdp\r\n\r\nv=0\r\no=" + Usuario + \
        " " + Ip + "\r\ns=misesion\r\nt=0\r\nm=audio " + PuertoRTP + " RTP"
        
        Tiempo_log = time.strftime('%Y­%m­%d %H:%M:%S', time.gmtime(time.time()))
        Log1.write(Tiempo_log[:4]) # Referenciamos el tiempo como antes.
        Log1.write(Tiempo_log[6:8])
        Log1.write(Tiempo_log[10:12])
        Log1.write(Tiempo_log[13:15])
        Log1.write(Tiempo_log[16:18])
        Log1.write(Tiempo_log[19:21])
        Log1.write(" Sent to ") # Al igual que en el metodo anterior.
        Log1.write(SERVER)
        Log1.write(":")
        Log1.write(str(PORT))
        Log1.write(": ")
        Message = LINE.split("\r\n")
        Log1.write(Message[0]) # Tenemos 7 saltos, por lo que hay 8 elementos
        Log1.write(" ")
        Log1.write(Message[1])
        Log1.write(" ")
        Log1.write(Message[2])
        Log1.write(" ")
        Log1.write(Message[3])
        Log1.write(" ")
        Log1.write(Message[4]) # Espacio en blanco.
        Log1.write(" ")
        Log1.write(Message[5])
        Log1.write(" ")
        Log1.write(Message[6])
        Log1.write(" ")
        Log1.write(Message[7])
        Log1.write("\r\n")

    elif metodo == "BYE":

        Receiver = sys.argv[3]
        LINE = metodo + " sip:" + Receiver + " SIP/2.0"
        
        Tiempo_log = time.strftime('%Y­%m­%d %H:%M:%S', time.gmtime(time.time()))
        Log1.write(Tiempo_log[:4]) # Como antes definimos el tiempo
        Log1.write(Tiempo_log[6:8])
        Log1.write(Tiempo_log[10:12])
        Log1.write(Tiempo_log[13:15])
        Log1.write(Tiempo_log[16:18])
        Log1.write(Tiempo_log[19:21])
        Log1.write(" Sent to ") # Igual que antes
        Log1.write(SERVER)
        Log1.write(":")
        Log1.write(str(PORT))
        Log1.write(": ")
        Log1.write(LINE) # SOlo tenemos una linea, no hace falta separar.
        Log1.write("\r\n")







