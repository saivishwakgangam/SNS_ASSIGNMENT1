import socket
import sys
import os
import hashlib
import pickle
from message import Message
from Crypto.Cipher import DES3
from _thread import start_new_thread
peer_info={}
message_object=Message("","","",b'',"","","","","","",[],False)
prime_number=671998030559713968361666935769
generator=2
roll_no=sys.argv[2]
listeningsocket=socket.socket()
def parse(message):
    list=message.split()
    return list[0]
#padding message
def pad(message):
    while len(message) % 8 != 0:
        message+=' '
    return message

def fill_the_object(message):
    initial=parse(message)
    if(initial=='signup'):
        global user_name
        global password
        list=message.split()
        message_object.empty()
        message_object.message_type="signup"
        message_object.client_name=list[2]
        user_name=list[2]
        message_object.client_rollnumber=list[1]
        password=list[3]
        message_object.client_password=password
        message_object.client_portno=str(sys.argv[1])
    elif(initial=='signin'):
        list=message.split()
        message_object.empty()
        message_object.message_type="signin"
        message_object.client_rollnumber=list[1]
        message_object.client_password=list[2]
    elif(initial=='create'):
        list=message.split(' ',2)
        message_object.empty()
        message_object.message_type="create"
        message_object.client_name=user_name
        group_names=list[2].split()
        message_object.group_list=group_names
    elif(initial=='join'):
        list=message.split(' ',2)
        message_object.empty()
        message_object.message_type="join"
        message_object.client_name=user_name
        group_names=list[2].split()
        message_object.group_list=group_names
    elif(initial=='list'):
        message_object.empty()
        message_object.message_type="list"
    elif(initial=='delete'):
        list=message.split(' ',2)
        message_object.empty()
        message_object.message_type="delete"
        message_object.client_name=user_name
        group_names=list[2].split()
        message_object.group_list=group_names
    elif(initial=='send'):
        global sending_message
        global receiver_name
        list=message.split(' ',2)
        message_object.empty()
        message_object.message_type="send"
        message_object.client_rollnumber=list[1]
        receiver_name=list[1]
        sending_message=user_name+':'+list[2]
        if list[1] in peer_info:
            message_object.receiver_present=True
            message_object.client_portno=peer_info[list[1]]['portno']
            message_object.content=peer_info[list[1]]['shared_key']
    elif(initial=='alice'):
        list=message.split()
        message_object.empty()
        message_object.message_from="CLIENT"
        message_object.message_type="KEY_EXCHANGE"
        message_object.content=list[1].encode('utf-8')
    elif(initial=='bob'):
        list=message.split()
        message_object.empty()
        message_object.message_from="CLIENT"
        message_object.message_type="KEY_EXCHANGE"
        message_object.content=list[1].encode('utf-8')

    return message_object


def sender_diffie_hellman():
    global private_key
    #generation of private key
    private_key_initial=os.urandom(24)
    key=str(private_key_initial)+roll_no
    final_key=hashlib.sha256(key.encode())
    private_key=int(final_key.hexdigest(),16)
    #generation of public key
    alice_public_key=int(pow(generator,private_key,prime_number))
    alice_public_key=str(alice_public_key)
    #send public key to bob
    messagesent='alice '+alice_public_key
    return messagesent


def receiver_diffie_hellman(response):
    global private_key
    global shared_key
    #generation of private key
    private_key_initial=os.urandom(24)
    key=str(private_key_initial)+roll_no
    final_key=hashlib.sha256(key.encode())
    private_key=int(final_key.hexdigest(),16)
    #generation of public key
    bob_public_key=int(pow(generator,private_key,prime_number))
    bob_public_key=str(bob_public_key)
    #generation of shared key
    alice_public_key=int(response)
    #print(alice_public_key)
    shared_key=int(pow(alice_public_key,private_key,prime_number))
    #print('shared key:'+str(shared_key))
    #send public key to bob
    messagesent='bob '+bob_public_key
    return messagesent
    
def generate_shared_key(response):
    #generation of shared key
    bob_public_key=int(response)
    shared_key=int(pow(bob_public_key,private_key,prime_number))
    return shared_key

def encrypt3des(messagesent,shared_key):
    messagesent=pad(messagesent)
    final_key=str(shared_key)
    final_key=final_key[:24]
    cipher=DES3.new(final_key,DES3.MODE_ECB)
    encrypted_message=cipher.encrypt(messagesent)
    return encrypted_message
    

def decrypt3des(messagesent):
    #print(shared_key)
    #print('i am decrypting the message!!!!')
    final_key=str(shared_key)
    final_key=final_key[:24]
    #print(messagesent)
    cipher=DES3.new(final_key,DES3.MODE_ECB)
    orginalmessage=cipher.decrypt(messagesent)
    display = str(orginalmessage.decode("utf-8"))     
    print(type(orginalmessage))
    print(display)
#   orginalmessage=str(orginalmessage)
#    print(orginalmessage.rstrip())

def send(portno,messagesent,flag,shared_key):
    newsocket=socket.socket()
    try:
        newsocket.connect((ipaddress,portno))
    except socket.error as e:
        print(str(e))
    if(flag==False):
        sender_public_key=sender_diffie_hellman()
        sending_object=fill_the_object(sender_public_key)
        sending_object_bytes=pickle.dumps(sending_object)
        newsocket.send(sending_object_bytes)
        recevi=newsocket.recv(2048)
        if recevi:
            recevi_object=pickle.loads(recevi)
            received_public_key=recevi_object.content.decode('utf-8')
            shared_key=generate_shared_key(received_public_key)
            peer_info[receiver_name]={'shared_key':shared_key,'portno':portno}
    messagesent=encrypt3des(messagesent,shared_key)
    message_object.empty()
    message_object.message_from="CLIENT"
    message_object.message_type="DECRYPT"
    message_object.content=messagesent
    newsocket.send(pickle.dumps(message_object))
    newsocket.close()


ipaddress='127.0.0.1'
portno=1234
def receivingdata(connection,port):
    while True:
        received=connection.recv(2048)
        if received:
            message_object=pickle.loads(received)
            initial=message_object.message_type
            source=message_object.message_from
            if(initial=='KEY_EXCHANGE'):
                received_public_key=message_object.content.decode('utf-8')
                message=receiver_diffie_hellman(received_public_key)
                sending_object=fill_the_object(message)
                sending_object_bytes=pickle.dumps(sending_object)
                connection.send(sending_object_bytes)
            elif(initial=='DECRYPT' and source=='CLIENT'):
                received_message=message_object.content
                decrypt3des(received_message)
            
        if not received:
            break
    connection.close()
    
def clientlistenthread():
    try:
        listeningsocket.bind((ipaddress,int(sys.argv[1])))
    except socket.error as e:
        print(str(e))
    print('client is listening on port no'+str(sys.argv[1]))
    listeningsocket.listen(5)
    while True:
        client, address =listeningsocket.accept()
        start_new_thread(receivingdata,(client,address[1]))

#connection with client is starting
start_new_thread(clientlistenthread,())

#connection with server is starting
clientsocket=socket.socket()
try:
    clientsocket.connect((ipaddress,portno))
except socket.error as e:
    print(str(e))
res=clientsocket.recv(1024)
print(res.decode('utf-8'))
while True:
    message=input()
    sending_object=fill_the_object(message)
    if(sending_object.message_type=="send" and sending_object.receiver_present==True):
        send(sending_object.client_portno,sending_message,True,sending_object.content)
    else:

        sending_bytes=pickle.dumps(sending_object)
        clientsocket.send(sending_bytes)
        resp=clientsocket.recv(1024)
        if resp:
            received_object=pickle.loads(resp)
            initial=received_object.message_type
            if initial=='general_response':
                print(received_object.content.decode('utf-8'))
            elif initial=='SOCK_RESPONSE':
                content_received=received_object.content.decode('utf-8')
                list=content_received.split()
                receiver_portno=int(list[1])
                #print(receiver_portno)
                send(receiver_portno,sending_message,False,"")
clientsocket.close()
