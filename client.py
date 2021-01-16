import socket
clientsocket=socket.socket()
ipaddress='127.0.0.1'
portno=1234
print('waiting for response from server')
try:
    clientsocket.connect((ipaddress,portno))
except socket.error as e:
    print(str(e))
res=clientsocket.recv(1024)
print(res.decode('utf-8'))
while True:
    message=input()
    clientsocket.send(str.encode(message))
    res=clientsocket.recv(1024)
    print(res.decode('utf-8'))
clientsocket.close()

