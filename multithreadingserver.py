import socket
import os
import pickle
from _thread import start_new_thread
from message import Message
clientinfo=[]
groupinfo={}
'''
It is a dictinary where group name is key.
Value is another dictionary with keys "participants" - a list of usernames, "admin" - user who created , "nonce" - a group secret key
'''
sendmessage_object=Message("","","",b'',"","","","","","",[],False)
def fill_the_object(initial,response):
    sendmessage_object.empty()
    if initial in ('signup','signin','create','join','list','delete'):
        sendmessage_object.message_from="SERVER"
        sendmessage_object.message_type="general_response"
        sendmessage_object.content=response.encode('utf-8')
    elif(initial=='send'):
        if 'portno' in response:
            sendmessage_object.message_from="SERVER"
            sendmessage_object.message_type="SOCK_RESPONSE"
            sendmessage_object.content=response.encode('utf-8')
        else:
            sendmessage_object.message_from="SERVER"
            sendmessage_object.message_type="general_response"
            sendmessage_object.content=response.encode('utf-8')
    return sendmessage_object

def create_user(roll_no,user_name,password,portno):
    length=len(clientinfo)
    for i in range(length):
        if(roll_no==clientinfo[i]['rollno']):
            response='roll number already present please enter another one'
            return response
    clientinfo.append({'rollno':roll_no,'username':user_name,'password':password,'login':False,'port':portno})
    print(clientinfo)
    response='you have signed up succesfully now please sign in'
    return response

def login(roll_no,password):
    length=len(clientinfo)
    for i in range(length):
        if(roll_no==clientinfo[i]['rollno'] and password==clientinfo[i]['password']):
            clientinfo[i]['login']=True
            response='loggedin '+clientinfo[i]['username']
            return response
    
    response='invalid credentials please check'
    return response

def joinGroup(username,group_list):
    print(group_list)
    response =""
    for group in group_list:
        if group in groupinfo:
            groupinfo[group]["participants"].append(username)
            response += "you are added to group " + group +"\n"
        else: 
            groupinfo[group] = {"participants" : [username], "admin" : username, "nonce" : os.urandom(24)}
            response += "Created Group " + group + "Admin : "+ username + "\n"
    print(groupinfo)
    return response

def createGroup(admin,group_list):
    print(group_list)
    response =""
    for group in group_list:
        if group in groupinfo:
            response += "Group " + group + " Already exists. Join the group by Join Group command"+"\n"
        else:
            groupinfo[group] = {"participants" : [admin], "admin" : admin, "nonce" : os.urandom(24)}
            response += "Created Group " + group + " ||  Admin : "+ admin + "\n"
    print(groupinfo)
    return response

def listGroups():
    response = ""
    for group in groupinfo:
        response += group+ " participant count: "+ str(len(groupinfo[group]["participants"]))+"\n"
    return response

def deleteGroup(username,group_list):
    response =""
    for g in group_list:
        if groupinfo[g]["admin"] == username:
            groupinfo.pop(g)
            response += " Group " + g + " deleted successfully\n"
        else:
            response += "You do not have authority to delete Group. Only admin of the group can delete the group"+ g+ "\n"
    print(groupinfo)
    return response

def sendmessagetoclient(message):
    length=len(clientinfo)
    for i in range(length):
        if(message==clientinfo[i]['rollno'] and clientinfo[i]['login']==True):
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
        if receiveddata:
            message_object=pickle.loads(receiveddata)
            initial=message_object.message_type
            if(initial=='signup'):
                roll_no=message_object.client_rollnumber
                username=message_object.client_name
                password=message_object.client_password
                portno=message_object.client_portno
                resp=create_user(roll_no,username,password,portno)
            elif(initial=='signin'):
                roll_no=message_object.client_rollnumber
                password=message_object.client_password
                resp=login(roll_no,password)
            elif(initial=='create'):
                admin=message_object.client_name
                group_list=message_object.group_list
                resp=createGroup(admin,group_list)
            elif(initial=='join'):
                username=message_object.client_name
                group_list=message_object.group_list
                resp=joinGroup(username,group_list)
            elif(initial=='list'):
                resp=listGroups()
            elif(initial=='delete'):
                username=message_object.client_name
                group_list=message_object.group_list
                resp=deleteGroup(username,group_list)
            elif(initial=='send'):
                roll_no=message_object.client_rollnumber
                resp=sendmessagetoclient(roll_no)
            sendmessage=fill_the_object(initial,resp)
            sendmessagebytes=pickle.dumps(sendmessage)
        if not receiveddata:
            break
        connection.sendall(sendmessagebytes)
    connection.close()
while True:
    Client, address=Serversocket.accept()
    print('connected to :' + address[0] + ':' + str(address[1]))
    start_new_thread(multithreadedclient,(Client,address[1]))
    count+=1
    print('Clients Connected :' + str(count))
Serversocket.close()
