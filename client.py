import socket
import sys
import os
from _thread import start_new_thread
def parse(message):
    list=message.split()
    return list[0]
ipaddress='127.0.0.1'
portno=1234
def receivingdata(connection,port):
    received=connection.recv(2048)
    print(received.decode('utf-8'))
    connection.close()
    
def clientlistenthread():
    listeningsocket=socket.socket()
    try:
        listeningsocket.bind((ipaddress,int(sys.argv[1])))
    except socket.error as e:
        print(str(e))
    print('client is listening on port no'+str(sys.argv[1]))
    listeningsocket.listen(5)
    while True:
        client, address =listeningsocket.accept()
        start_new_thread(receivingdata,(client,address[1]))
def send(received,messagesent):
    newsocket=socket.socket()
    list=recevied.split()
    try:
        newsocket.connect((ipaddress,int(list[1])))
    except socket.error as e:
        print(str(e))
    newsocket.send(str.encode(messagesent))
    
start_new_thread(clientlistenthread,())
####
clientsocket=socket.socket()
#connection with server is starting
try:
    clientsocket.connect((ipaddress,portno))
except socket.error as e:
    print(str(e))
res=clientsocket.recv(1024)
print(res.decode('utf-8'))
while True:
    message=input()
    initial=parse(message)
    if(initial=='signup'):
        message+=" "
        message+=sys.argv[1]
    elif(initial=='send'):
        list=message.split(' ',2)
        sendingmessage=list[2]
        message=list[0]+' '+list[1]

    clientsocket.send(str.encode(message))
    res=clientsocket.recv(1024)
    recevied=res.decode('utf-8')
    initial=parse(recevied)
    if(initial=='portno'):
        send(recevied,sendingmessage)
    else:
        print(recevied)
clientsocket.close()

