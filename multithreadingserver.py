import socket
import os
from _thread import start_new_thread
Serversocket=socket.socket()
ipadress='127.0.0.1'
portno = 1234
count = 0
try:
    Serversocket.bind((ipadress,portno))
except socket.error as e:
    print(str(e))
print('server is listening')
Serversocket.listen(5)
def multithreadedclient(connection):
    connection.send(str.encode("hello i am there!!"))
    while True:
        receiveddata=connection.recv(2048)
        response='Server Message:'+receiveddata.decode('utf-8')
        if not receiveddata:
            break
        connection.sendall(str.encode(response))
    connection.close()
while True:
    Client, address=Serversocket.accept()
    print('connected to :' + address[0] + ':' + str(address[1]))
    start_new_thread(multithreadedclient,(Client,))
    count+=1
    print('Clients Connected :' + str(count))
Serversocket.close()


        