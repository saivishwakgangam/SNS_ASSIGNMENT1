import socket
import sys
import os
import hashlib
from Crypto.Cipher import DES3
from _thread import start_new_thread

prime_number=671998030559713968361666935769
generator=2
roll_no=sys.argv[2]
global user_name
user_name='h'
listeningsocket=socket.socket()
#padding message

def pad(message):
    while len(message) % 8 != 0:
        message+=' '
    return message

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
    messagesent='alice '+str(portno)+' '+alice_public_key
    return messagesent

def parse(message):
    list=message.split()
    return list[0]

def receiver_diffie_hellman(response):
    global private_key
    global shared_key
    list=response.split()
    #generation of private key
    private_key_initial=os.urandom(24)
    key=str(private_key_initial)+roll_no
    final_key=hashlib.sha256(key.encode())
    private_key=int(final_key.hexdigest(),16)
    #generation of public key
    bob_public_key=int(pow(generator,private_key,prime_number))
    bob_public_key=str(bob_public_key)
    #generation of shared key
    alice_public_key=int(list[2])
    #print(alice_public_key)
    shared_key=int(pow(alice_public_key,private_key,prime_number))
    #print('shared key:'+str(shared_key))
    #send public key to bob
    messagesent=bob_public_key
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


ipaddress='127.0.0.1'
portno=1234
def receivingdata(connection,port):
    while True:
        recevied=connection.recv(2048)
        if b'alice' in recevied:
            response=recevied.decode('utf-8')
            message=receiver_diffie_hellman(response)
            #print(message)
            connection.sendall(str.encode(message))
        else:
            decrypt3des(recevied)
            break
        if not recevied:
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
    
def send(received,messagesent):
    newsocket=socket.socket()
    list=recevied.split()
    try:
        newsocket.connect((ipaddress,int(list[1])))
    except socket.error as e:
        print(str(e))
    message=sender_diffie_hellman()
    #print('private key:'+message)
    newsocket.sendall(str.encode(message))
    recevi=newsocket.recv(2048)
    response=recevi.decode('utf-8')
    #print('receiver public key'+response)
    shared_key=generate_shared_key(response)
    #print(shared_key)
    messagesent=encrypt3des(messagesent,shared_key)
    #print(messagesent)
    newsocket.sendall(messagesent)
    newsocket.close()
    
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
    print("initial : ", initial)
    if(initial=='signup'):
        message+=" "
        message+=sys.argv[1]
    elif(initial=='send'):
        list=message.split(' ',2)
        sendingmessage=user_name+':'+list[2]
        message=list[0]+' '+list[1]

    elif(initial=='join'):
        message+= " "+user_name
    elif(initial=='create'):
        message+= " "+user_name
    elif(initial=='delete'):
        message+= " "+user_name

    clientsocket.send(str.encode(message))
    res=clientsocket.recv(1024)
    recevied=res.decode('utf-8')
    initial=parse(recevied)
    if(initial=='portno'):
        send(recevied,sendingmessage)
    elif(initial=='loggedin'):
        list=recevied.split()
        user_name=list[1]
    else:
        print(recevied)
clientsocket.close()
