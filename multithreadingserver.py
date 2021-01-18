import socket
import os
from _thread import start_new_thread
clientinfo=[]
groupinfo=[]
def create_user(message,portno):
    list=message.split()
    length=len(clientinfo)
    for i in range(length):
        if(list[1]==clientinfo[i]['rollno']):
            response='roll number already present please enter another one'
            return response
    clientinfo.append({'rollno':list[1],'username':list[2],'password':list[3],'login':False,'port':list[4]})
    response='you have signed up succesfully now please sign in'
    return response

def login(message,portno):
    list=message.split()
    length=len(clientinfo)
    for i in range(length):
        if(list[1]==clientinfo[i]['rollno'] and list[2]==clientinfo[i]['password']):
            clientinfo[i]['login']=True
            response='you are succesfully logged in'
            return response
    
    response='invalid credentials please check'
    return response


def sendmessage(message):
    list=message.split()
    length=len(clientinfo)
    for i in range(length):
        if(list[1]==clientinfo[i]['rollno'] and clientinfo[i]['login']==True):
            response='portno '+clientinfo[i]['port']
            return response
    response='member not present in the network or he is not login!!'
    return response
     
def parse(message):
    list=message.split()
    return list[0]

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

def multithreadedclient(connection,portno):
    connection.send(str.encode("hello i am there!! and your port no is"+str(portno)))
    while True:
        receiveddata=connection.recv(2048)
        response=receiveddata.decode('utf-8')
        initial=parse(response)
        if(initial=='signup'):
            resp=create_user(response,portno)
        elif(initial=='signin'):
            resp=login(response,portno)
        elif(initial=='send'):
            resp=sendmessage(response)

            
        if not receiveddata:
            break
        connection.sendall(str.encode(resp))
    connection.close()
while True:
    Client, address=Serversocket.accept()
    print('connected to :' + address[0] + ':' + str(address[1]))
    start_new_thread(multithreadedclient,(Client,address[1]))
    count+=1
    print('Clients Connected :' + str(count))
Serversocket.close()


        
