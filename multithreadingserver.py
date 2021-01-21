import socket
import os
from _thread import start_new_thread


clientinfo=[]

groupinfo={}
'''
It is a dictinary where group name is key.
Value is another dictionary with keys "participants" - a list of usernames, "admin" - user who created , "nonce" - a group secret key
'''
def create_user(message,portno):
    print(message)
    list=message.split()
    length=len(clientinfo)
    for i in range(length):
        if(list[1]==clientinfo[i]['rollno']):
            response='roll number already present please enter another one'
            return response
    clientinfo.append({'rollno':list[1],'username':list[2],'password':list[3],'login':False,'port':list[4]})
    print(clientinfo)
    response='you have signed up succesfully now please sign in'
    return response

def login(message,portno):
    list=message.split()
    length=len(clientinfo)
    for i in range(length):
        if(list[1]==clientinfo[i]['rollno'] and list[2]==clientinfo[i]['password']):
            clientinfo[i]['login']=True
            response='loggedin '+clientinfo[i]['username']
            return response
    
    response='invalid credentials please check'
    return response

def joinGroup(message):
    print(message)
    command_list = message.split()
    print(command_list)
    group_request_list = list(command_list[2:-1])
    username = command_list[-1]
    print(group_request_list)
    response =""
    for group in group_request_list:
        if group in groupinfo:
            groupinfo[group]["participants"].append(command_list[-1])
            response += "you are added to group " + group +"\n"
        else: 
            groupinfo[group] = {"participants" : [username], "admin" : username, "nonce" : os.urandom(24)}
            response += "Created Group " + group + "Admin : "+ admin + "\n"
    print(groupinfo)
    return response

def createGroup(message):
    command_list = message.split()
    print(command_list)
    group_request_list = list(command_list[2:-1])
    username = command_list[-1]
    print(group_request_list)
    response =""
    for group in group_request_list:
        if group in groupinfo:
            response += "Group " + group + " Already exists. Join the group by Join Group command"+"\n"
        else:
            groupinfo[group] = {"participants" : [username], "admin" : username, "nonce" : os.urandom(24)}
            response += "Created Group " + group + " ||  Admin : "+ username + "\n"
    print(groupinfo)
    return response

def listGroups():
    response = ""
    for group in groupinfo:
        response += group+ " participant count: "+ str(len(groupinfo[group]["participants"]))+"\n"
    return response

def deleteGroup(message):
    print(message)
    command_list = message.split()
    print(command_list)
    username = command_list[-1]
    response =""
    for g in command_list[2:-1]:
        if groupinfo[g]["admin"] == username:
            groupinfo.pop(g)
            response += " Group " + g + " deleted successfully\n"
        else:
            response += "You do not have authority to delete Group. Only admin of the group can delete the group"+ g+ "\n"
    print(groupinfo)
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


        elif(initial == 'create'):
            resp = createGroup(response)
        elif(initial == 'delete'):
            resp = deleteGroup(response)

        elif(initial == 'join'):
            resp = joinGroup(response)
        elif(initial == 'list'):
            resp = listGroups()

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
