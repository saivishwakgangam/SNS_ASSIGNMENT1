import socket
import pickle
from message import message
import hashlib
import sys
#import os
from _thread import start_new_thread
from Crypto.Cipher import DES3
import time
import encryption
global signup_status
global signin_status

host="127.0.0.1"
port=15000
listening_port=str(sys.argv[1])
roll_number=str(sys.argv[2])
#prime_number=671998030559713968361666935769 #p
#generator=2  #g
user_name=""
pass_word=""
peer_info={}
key_info={}
private_key=""
public_key=""
def pad(msg):
    while not len(msg)%8==0:
        msg=msg+' '
    return msg
def pad_file(msg):
    while not len(msg)%8==0:
        msg=msg+b' '
    return msg

"""def gen_public_key():
    global private_key
    global public_key
    private_key=os.urandom(24)
    key=str(private_key)+roll_number
    final_key=hashlib.sha256(key.encode()).hexdigest()
    private_key=int(final_key,16)
    sender_pub_key=int(pow(generator,private_key,prime_number))
    public_key=str(sender_pub_key)

def gen_shared_key(req):
    sender_name=req.client_name
    sender_public_key=int(req.content.decode('utf-8'))
    shared_key=int(pow(sender_public_key,private_key,prime_number)) #S^a mod p/S^b modp
    key_info[sender_name]=shared_key
"""

def send_to_server(msg1,msg2=b'',message_type=""):
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        s.connect((host,port))
        s.sendall(msg1)
        if not message_type=="GRP_MSG":
            data_recv=s.recv(2048)
            res=pickle.loads(data_recv)
            return res
        else:
            data_recv=s.recv(10)
            s.sendall(msg2)
            
def send_to_client(data1,data2,port,message_type):
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        s.connect((host,port))
        s.sendall(data1)
        data_recv=s.recv(8)
        s.sendall(data2)
        if(message_type=="KEY_EX_REQ"):
            data_recv=s.recv(2048)
            res=pickle.loads(data_recv)
            return res
            
def sock_req(client_name):
    msg=message("CLI","SOCK_REQ","TEXT",bytes(client_name,'utf-8'),"","","dattu")
    msg=pickle.dumps(msg)
    res=send_to_server(msg,message_type="SOCK_REQ")
    return res
    

def sign_up(username,password,listening_socket):
    temp=username+password
    password=hashlib.sha256(temp.encode())
    password=password.hexdigest()
    msg=message("CLI","SIGN_UP","TEXT",bytes(listening_socket+","+password,'utf-8'),"","",username)
    msg=pickle.dumps(msg)
    res=send_to_server(msg,message_type="SIGN_UP")
    return res

def sign_in(username,password):
    temp=username+password
    global user_name
    global pass_word
    user_name=username
    pass_word=hashlib.sha256(temp.encode()).hexdigest()
    msg=message("CLI","SIGN_IN","TEXT",bytes(pass_word,'utf-8'),client_name=user_name)
    msg=pickle.dumps(msg)
    res=send_to_server(msg,message_type="SIGN_IN")
    return res

def create_grp(group_name):
    msg=message("CLI","CRE","TEXT",bytes(group_name,'utf-8'),client_name=user_name)
    msg=pickle.dumps(msg)
    res=send_to_server(msg,message_type="CRE")
    return res

def list_grps():
    msg=message("CLI","LIST","TEXT",bytes("list_groups",'utf-8'),client_name=user_name)
    msg=pickle.dumps(msg)
    res=send_to_server(msg,message_type="LIST")
    return res

def join_grp(groups):
    msg=message("CLI","JOIN","TEXT",bytes(groups,'utf-8'),client_name=user_name)
    msg=pickle.dumps(msg)
    res=send_to_server(msg,message_type="JOIN")
    return res

def req_nonce(groups):
    msg=message("CLI","NONCE_REQ","TEXT",bytes(groups,'utf-8'),client_name=user_name)
    msg=pickle.dumps(msg)
    res=send_to_server(msg,message_type="NONCE_REQ")
    return res

def key_exchange(reciever_name):
    msg1=message("CLI","KEY_EX_REQ","TEXT",bytes(public_key,'utf-8'),"","",client_name=user_name)
    msg1=pickle.dumps(msg1)
    sending_length=str(len(msg1))
    msg2=message("CLI","KEY_EX_REQ","TEXT",bytes(sending_length,'utf-8'),"","",user_name)
    msg2=pickle.dumps(msg2)
    res=send_to_client(msg2,msg1,peer_info[reciever_name],"KEY_EX_REQ")
    sender_public_key=int(res.content.decode('utf-8'))
    key_info[res.client_name]=encryption.gen_shared_key(sender_public_key,private_key)
    
"""def encrypt(msg,shared_key):
    shared_key=shared_key[:24]
    cipher=DES3.new(shared_key,DES3.MODE_ECB)
    encrypted_message=cipher.encrypt(msg)
    return encrypted_message
    
def decrypt(msg,shared_key):
    shared_key=shared_key[:24]
    cipher=DES3.new(shared_key,DES3.MODE_ECB)
    org=cipher.decrypt(msg)
    return org"""
    
def send_client(msg,receiving_client,file_name="",content_type="TEXT"):
    cipher=encryption.encrypt_des3(msg,str(key_info[receiving_client]))
    msg1=message("CLI","NORMAL_MSG",content_type,cipher,file_name,"",user_name)
    msg1=pickle.dumps(msg1)
    cipher=encryption.encrypt_des3(pad(str(len(msg1))),str(key_info[receiving_client]))
    msg2=message("CLI","NORMAL_MSG","TEXT",cipher,"","",user_name)
    msg2=pickle.dumps(msg2)
    send_to_client(msg2,msg1,peer_info[receiving_client],"NORMAL_MSG")

def send_group(msg,nonce,grp_name,file_name="",content_type="TEXT"):
    cipher=encryption.encrypt_des3(msg,nonce)
    msg1=message("CLI","GRP_MSG",content_type,cipher,file_name,"",user_name,group_name=grp_name)
    msg1=pickle.dumps(msg1)
    cipher=encryption.encrypt_des3(pad(str(len(msg1))),nonce)
    msg2=message("CLI","GRP_MSG","TEXT",cipher,client_name=user_name,group_name=grp_name)
    msg2=pickle.dumps(msg2)
    send_to_server(msg2,msg1,"GRP_MSG")

def read_file(file_name):
    file=open(file_name,"rb")
    return file.read()

def receivingdata(conn,port):
    data=conn.recv(2048)
    req=pickle.loads(data)
    conn.send(bytes("ok",'utf-8'))
    if(req.message_type=="KEY_EX_REQ"):
        data=conn.recv(2048)
        req=pickle.loads(data)
        sender_public_key=int(req.content.decode('utf-8'))
        key_info[req.client_name]=encryption.gen_shared_key(sender_public_key,private_key)
        msg=message("CLI","KEY_EX_RES","TEXT",bytes(public_key,'utf-8'),"","",client_name=user_name)
        data=pickle.dumps(msg)
        conn.sendall(data)
    elif(req.message_type=="NORMAL_MSG" and req.message_from=="CLI"):
        length=encryption.decrypt_des3(req.content,str(key_info[req.client_name]))
        length=int(length.decode('utf-8'))
        data1=bytearray()
        while length>0:
            data=conn.recv(2048)
            data1.extend(data)
            length=length-2048
        data=bytes(data1)
        req=pickle.loads(data)
        recieved_data=encryption.decrypt_des3(req.content,str(key_info[req.client_name]))
        if(req.content_type=="TEXT"):
            recieved_data=recieved_data.strip(b' ')
            print(req.client_name+":"+recieved_data.decode('utf-8'))
        else:
            recieved_data=recieved_data.strip(b' ')
            file1=open(req.client_name+"_"+req.file_name,"wb")
            file1.write(recieved_data)
            file1.close()
            print(req.client_name+":"+req.file_name+" file")
    elif(req.message_type=="GRP_MSG" and req.message_from=="SERV"):
        length=int(encryption.decrypt_des3(req.content,pass_word).decode('utf-8'))
        data1=bytearray()
        while length>0:
            data=conn.recv(2048)
            data1.extend(data)
            length=length-2048
        data=bytes(data1)
        req=pickle.loads(data)
        recieved_data=encryption.decrypt_des3(req.content,pass_word)
        if(req.content_type=="TEXT"):
            recieved_data=recieved_data.strip(b' ')
            print(req.group_name+"::"+req.client_name+":"+recieved_data.decode('utf-8'))
        else:
            recieved_data=recieved_data.strip(b' ')
            file1=open(req.group_name+"_"+req.client_name+"_"+req.file_name,"wb")
            file1.write(recieved_data)
            file1.close()
            print(req.group_name+"::"+req.client_name+":"+req.file_name+" file")
        
def clientlisteningthread():
    listeningsocket=socket.socket()
    try:
        listeningsocket.bind((host,int(listening_port)))
    except socket.error as e:
        print(str(e))
    print('client is listening on port no'+listening_port)
    listeningsocket.listen(5)
    while True:
        client, address =listeningsocket.accept()
        start_new_thread(receivingdata,(client,address[1]))

start_new_thread(clientlisteningthread,())
private_key,public_key=encryption.gen_public_key(roll_number)
print("Welcome to E2E Messaging System")
print(
'''
* To run client : python client.py PORT RollNumber

* present : Working model
* signup : signup username password
* signin : signin username password
* message peer : send username_of_receiver message
* send file to peer: send_file username_of_receiver filename
* create group : create_grp group_name1,group_name2 ...
* join group : join_grp group_name1,group_name2 ...
* list groups : list 
* send message to groups: send_grp group_list message
* send file to groups: send_grp_file group_list filename
''')
signup_status=False
signin_status=False
while True:
    command=input("")
    parsed=command.split()
    if(parsed[0].lower()=="signup"):
        if(signup_status==False):
            res=sign_up(parsed[1],parsed[2],listening_port)
            print(res.content.decode('utf-8'))
            if(res.content.decode('utf-8')=="SIGN UP SUCCESFULL"):
                signup_status=True
        else:
            print('you have already signed up')

    elif parsed[0].lower()=="signin":
        if(signin_status==False):
            res=sign_in(parsed[1],parsed[2])
            print(res.content.decode('utf-8'))
            if(res.content.decode('utf-8')=="Succesfully signed in"):
                signin_status=True
        else:
            print("you have already signed in")
    if(signin_status and signup_status):
        if(parsed[0].lower()=="send"):
            peer_socket=""
            if parsed[1] not in peer_info and not parsed[1]==user_name:
                res=sock_req(parsed[1])
                if(res.message_type=="ERR"):
                    print(res.content.decode('utf-8'))
                elif parsed[1] in key_info:
                    peer_socket=int(res.content.decode('utf-8'))
                    peer_info[parsed[1]]=peer_socket
                else:
                    peer_socket=int(res.content.decode('utf-8'))
                    peer_info[parsed[1]]=peer_socket
                    key_exchange(parsed[1])
            msg=""
            for i in range(2,len(parsed)):
                msg=msg+parsed[i]
                msg+=" "
            msg=pad(msg)
            send_client(msg,parsed[1])
        elif(parsed[0].lower()=="create_grp"):
            res=create_grp(parsed[1])
            print(res.content.decode('utf-8'))
        elif parsed[0].lower()=="list":
            res=list_grps()
            print(res.content.decode('utf-8'))
        elif parsed[0].lower()=="join_grp":
            res=join_grp(parsed[1])
            print(res.content.decode('utf-8'))
        elif parsed[0].lower()=="send_grp":
            groups=parsed[1]
            res=req_nonce(groups)
            msg=""
            for i in range(2,len(parsed)):
                msg=msg+parsed[i]
                msg=msg+" "
            msg=pad(msg)
            if(len(msg)>0):
                grp_nonces=encryption.decrypt_des3(res.content,pass_word).decode('utf-8')
                grp_nonces=grp_nonces.rstrip()
                for nonce in grp_nonces.split(","):
                    grp_name=nonce.split(":")[0]
                    grp_nonce=nonce.split(":")[1]
                    if(grp_nonce=="NAN1"):
                        print(grp_name+" does not exist")
                    elif(grp_nonce=="NAN2"):
                        print("You are not a member of "+grp_name)
                    else:
                        send_group(msg,grp_nonce,grp_name)
        elif parsed[0].lower()=="send_file":
            peer_socket=""
            if parsed[1] not in peer_info:
                res=sock_req(parsed[1])
                if(res.message_type=="ERR"):
                    print(res.content.decode('utf-8'))
                elif parsed[1] in key_info:
                    peer_socket=int(res.content.decode('utf-8'))
                    peer_info[parsed[1]]=peer_socket
                else:
                    peer_socket=int(res.content.decode('utf-8'))
                    peer_info[parsed[1]]=peer_socket
                    key_exchange(parsed[1])
            msg=read_file(parsed[2])
            msg=pad_file(msg)
            send_client(msg,parsed[1],parsed[2],"FILE")
            
        elif parsed[0]=="send_grp_file":
            groups=parsed[1]
            res=req_nonce(groups)
            msg=read_file(parsed[2])
            msg=pad_file(msg)
            if(len(msg)>0):
                grp_nonces=encryption.decrypt_des3(res.content,pass_word).decode('utf-8')
                grp_nonces=grp_nonces.rstrip(",")
                for nonce in grp_nonces.split(","):
                    grp_name=nonce.split(":")[0]
                    grp_nonce=nonce.split(":")[1]
                    if(grp_nonce=="NAN1"):
                        print(grp_name+" does not exist")
                    elif(grp_nonce=="NAN2"):
                        print("You are not a member of "+grp_name)
                    else:
                        send_group(msg,grp_nonce,grp_name,parsed[2],"FILE")
    else:
        print('please signup or if you have signedup signin')
            
            
            
            
        
        
        
        
        
        
        
    
        
        
    
