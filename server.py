import socket
import pickle
from message import message
import os
import hashlib
from _thread import start_new_thread
import encryption

portno=15000
ipaddress="127.0.0.1"

client_info={}
group_info={}

"""with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    s.bind((host,portno))
    while True:
        s.listen()
        conn,addr=s.accept()
        with conn:
            print("connected by",addr)
            data_recv=conn.recv(2048)
            req=pickle.loads(data_recv)
            if(req.message_type=="SOCK_REQ"):
                client_name=req.content.decode('utf-8')
                if client_name in client_info:
                    response=message("SERV","SOCK_RES","text",bytes(client_info[client_name][0],'utf-8'),"","","serv")
                else:
                    response=message("SERV","ERR","text",bytes("reciever not found",'utf-8'),"","","serv")
                data=pickle.dumps(response)
                conn.sendall(data)
            elif req.message_type=="SIGN_UP":
                if req.client_name in client_info:
                    response=message("SERV","ERR","text",bytes("username already exists",'utf-8'),"","","serv")
                else:
                    client_info[req.client_name]=req.content.decode('utf-8').split(",")
                    response=message("SERV","SIGN_UP_RES","text",bytes("Successful",'utf-8'))
                data=pickle.dumps(response)
                conn.sendall(data)
            elif req.message_type=="SIGN_IN":
                if req.client_name not in client_info:
                    response=message("SERV","ERR","text",bytes("user not found",'utf-8'))
                elif not client_info[req.client_name][1] == req.content.decode("utf-8"):
                    response=message("SERV","ERR","text",bytes("invalid username or password",'utf-8'))
                else:
                    response=message("SERV","ERR","text",bytes("LOGIN SUCCESFULL","utf-8"))
                data=pickle.dumps(response)
                conn.sendall(data)
"""

def send_to_client(msg1,msg2,portno):
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        s.connect((ipaddress,portno))
        s.sendall(msg1)
        data=s.recv(10)
        s.sendall(msg2)
    
def pad(msg):
    while not len(msg)%8==0:
        msg+=' '
    return msg

"""def encrypt(message,shared_key):
    shared_key=shared_key[:24]
    cipher=DES3.new(shared_key,DES3.MODE_ECB)
    encrypted_message=cipher.encrypt(message)
    return encrypted_message
    
def decrypt(message,shared_key):
    shared_key=shared_key[:24]
    cipher=DES3.new(shared_key,DES3.MODE_ECB)
    org=cipher.decrypt(message)
    return org
"""

def sign_up(req):
    if(req.client_name in client_info):
        resp=message("SERV","ERR","TEXT",bytes("username already exists",'utf-8'))
    else:
        client_info[req.client_name]=req.content.decode('utf-8').split(",")
        resp=message("SERV","SIGN_UP","TEXT",bytes("SIGN UP SUCCESFULL",'utf-8'))
        print(client_info)
    return resp
    
def sign_in(req):
    if(req.client_name not in client_info):
        resp=message("SERV","ERR","TEXT",bytes("username not found",'utf-8'))
    elif not req.content.decode("utf-8")==client_info[req.client_name][1]:
        resp=message("SERV","ERR","TEXT",bytes("incorrect credentials",'utf-8'))
    else:
        resp=message("SERV","SIGN_IN","TEXT",bytes("Succesfully signed in",'utf-8'))
    return resp
    
def send_sock(req):
    client=req.content.decode("utf-8")
    if(client not in client_info):
        resp=message("SERV","ERR","TEXT",bytes(client+" not found",'utf-8'))
    else:
        resp=message("SERV","SOCK_RES","TEXT",bytes(client_info[client][0],'utf-8'))
    return resp
def create_group(req):
    grouplist=req.content.decode('utf-8').split(",")
    msg=""
    for group in grouplist:
        if group in group_info:
            msg+="Group" + group + "Already exists.Join the group using Join Group command\n"
        else:
            private_key=os.urandom(24)
            key=str(private_key)+group
            private_key=hashlib.sha256(key.encode()).hexdigest()
            private_key=int(private_key,16)
            nonce=str(private_key)
            nonce=nonce[:24]
            group_info[group]={"participants":[req.client_name],"admin":req.client_name,"nonce":nonce}
            msg+="Created group " + group +"|| Admin: "+req.client_name+"\n"
    resp=message("SERV","CRE","TEXT",bytes(msg,'utf-8'))
    return resp

def join_grp(req):
    grouplist=req.content.decode('utf-8').split(",")
    client_name=req.client_name
    #print(client_name)
    msg=""
    for group in grouplist:
        if group in group_info:
            #print(group_info[group]["participants"])
            #print(client_name in group_info[group]["participants"])
            if (client_name in group_info[group]["participants"]):
                msg+="You are already in this group :"+ group+"\n"
            else:
                group_info[group]["participants"].append(client_name)
                msg+="you are added to group:"+group+"\n"
        else:
            private_key=os.urandom(24)
            key=str(private_key)+group
            private_key=hashlib.sha256(key.encode()).hexdigest()
            private_key=int(private_key,16)
            nonce=str(private_key)
            nonce=nonce[:24]
            group_info[group]={"participants":[req.client_name],"admin":req.client_name,"nonce":nonce}
            msg+="Created group " + group +"|| Admin: "+req.client_name+"\n"
    resp=message("SERV","JOIN","TEXT",bytes(msg,'utf-8'))
    return resp
            
def list_groups(req):
    msg=""
    #print(group_info)
    for group in group_info:
        msg+=group+" participant count:"+str(len(group_info[group]["participants"]))+"\n"
    resp=message("SERV","LIST","TEXT",bytes(msg,'utf-8'))
    return resp
    
def send_nonce(req):
    grouplist=req.content.decode('utf-8').split(",")
    msgs=[]
    if(len(grouplist)==1 and grouplist[0]=="*"):
        for group in group_info:
            if req.client_name in group_info[group]["participants"]:
                msg=group+":"+group_info[group]["nonce"]
                msgs.append(msg)
    else:
        for group in grouplist:
            if group not in group_info:
                msg=group+":NAN1"
                msgs.append(msg)
            else:
                #print(group_info[group]["participants"])
                if req.client_name not in group_info[group]["participants"]:
                    msg=group+":NAN2"
                    msgs.append(msg)
                else:
                    msg=group+":"+group_info[group]["nonce"]
                    msgs.append(msg)
    msg=",".join(msgs)
    msg=pad(msg)
    cipher=encryption.encrypt_des3(msg,client_info[req.client_name][1])
    resp=message("SERV","NONCE_RES","TEXT",cipher)
    return resp
    
def send_clients(msg,group_name,client_name,content_type,file_name=""):
    #print("sending to group members:"+group_name)
    msg_length=str(len(msg))
    msg_length=pad(msg_length)
    for client in group_info[group_name]["participants"]:
        if not client==client_name:
            print(client)
            cipher=encryption.encrypt_des3(msg_length,client_info[client][1])
            msg1=message("SERV","GRP_MSG","TEXT",cipher,file_name,client_name=client_name,group_name=group_name)
            msg1=pickle.dumps(msg1)
            cipher=encryption.encrypt_des3(msg,client_info[client][1])
            msg2=message("SERV","GRP_MSG",content_type,cipher,file_name,client_name=client_name,group_name=group_name)
            msg2=pickle.dumps(msg2)
            start_new_thread(send_to_client,(msg1,msg2,int(client_info[client][0])))

def multithreadedclient(connection,portno):
    data=connection.recv(2048)
    req=pickle.loads(data)
    if(req.message_type=="SIGN_UP"):
        response=sign_up(req)
        data=pickle.dumps(response)
        connection.sendall(data)
    elif(req.message_type=="SIGN_IN"):
        response=sign_in(req)
        data=pickle.dumps(response)
        connection.sendall(data)
    elif(req.message_type=="SOCK_REQ"):
        response=send_sock(req)
        data=pickle.dumps(response)
        connection.sendall(data)
    elif(req.message_type=="CRE"):
        response=create_group(req)
        data=pickle.dumps(response)
        connection.sendall(data)
    elif(req.message_type=="JOIN"):
        response=join_grp(req)
        data=pickle.dumps(response)
        connection.sendall(data)
    elif(req.message_type=="LIST"):
        response=list_groups(req)
        data=pickle.dumps(response)
        connection.sendall(data)
    elif(req.message_type=="NONCE_REQ"):
        response=send_nonce(req)
        data=pickle.dumps(response)
        connection.sendall(data)
    elif(req.message_type=="GRP_MSG"):
        #print("group message request recieved")
        client_msg_length=int(encryption.decrypt_des3(req.content,group_info[req.group_name]["nonce"]).decode('utf-8'))
        #print(client_msg_length)
        connection.sendall(bytes("ok",'utf-8'))
        data1=bytearray()
        while client_msg_length>0:
            data=connection.recv(2048)
            data1.extend(data)
            client_msg_length=client_msg_length-2048
        data=bytes(data1)
        req=pickle.loads(data)
        client_msg=encryption.decrypt_des3(req.content,group_info[req.group_name]["nonce"])
        send_clients(client_msg,req.group_name,req.client_name,req.content_type,req.file_name)
        
    
with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    s.bind((ipaddress,portno))
    s.listen(10)
    while True:
        client,address=s.accept()
        start_new_thread(multithreadedclient,(client,address[1]))
    
