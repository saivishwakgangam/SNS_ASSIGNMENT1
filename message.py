class message:
    message_from=""
    message_type=""
    content_type=""
    content=bytes()
    file_name=""
    file_type=""
    client_name=""
    group_name=""
    def __init__(self,message_from,message_type,content_type,content,file_name="",file_type="",client_name="",group_name=""):
        self.message_from=message_from
        self.message_type=message_type
        self.content_type=content_type
        self.content=content
        self.file_name=file_name
        self.file_type=file_type
        self.client_name=client_name
        self.group_name=group_name
"""
 message_from:
    CLI:this message is from client to the receiver
    SERV:this mesage is from server to the receiver
    
 message_type:
    REQ_SOCK: this is a request from client to server to give the socket of other client(to whom data is sent) content of this type is name of the receiver,
    SOCK_RES: this is a response from server to client sending the socket of client
        encrypted by password of user client should decrypt this using his password
    KEY_EX_REQ:this is a request from client to client/server to intimate the start of a key content_type:(key type)exchange the content of this message is the shared key
    KEY_EX_RESP:the reciever has computed the shared key and sent his public key
    
    REQ_NONCE:
        
        this is a request from client to server requesting nonce,the content of this message is a comma seperated value(to be parsed by sever) each value representing the group name
    NONCE_RESP: this is a response from server to client encrypted with password of the client_name
                content:group_name1:nonce1,group_name2:nonce2
                encrypted with password of sender
    GRP_MSG:
        (i): if the sender is client ,this message should be sent to server
             encryption should be done using nonce
             group_names must be mentioned in group_list
             server decrypts the object and checks the group names in group list
             and sends a message of same message_type GRP_MSG to all clients of the
             groups mentioned except the sender
        (ii): if the sender is server ,this message should be sent to client
              encryption is done using password of client
              client should decrypt the message using his password
    CREATE_GRP_REQ:
        this message is request from client to server requesting creation of group
    CREATE_GRP_RES:
        this message is request from server to client response
    JOIN_GRP_REQ:
        
    JOIN_GRP_RES:
    NORMAL_MSG:
        this message is a client to client message of any type
    SIGN_UP:a sign up message from client to server
        content is of the form username:password
    SIGN_IN:a sign in message from client to server
        content is of the form username:password
    SIGN_UP_RES: self explanatory serv to client content represents the success message
    SIGN_IN_RES: self explanatory server to client content represents the success message

content_type:
        text: for text messages
        key: for KEY_EX
        file: for files
content: byte representation of the data to be sent
file_name: string representing the file name
file_type: format of the file
client_name: username of the sender
group_list: used in GRP_MSG

ENCRYPTION SHOULD BE DONE FOR THE FOLLOWING MESSAGE_TYPES:
    GRP_MSG
    NONCE_RESP
    NORMAL_MSG
    SOCK_RES
    
client::peers={reciever_name:[shared_key,listening_port_of_client]}
server::client_info:{user_name:[password,listening_port_of_client,rollno]}
server::group_info:{group_name:[nonce,[user_names],admin_name]]}
username=""
password=""
"""

"""msg=message("CLI","GRP_MSG","text","abcd",client_name="ABC",group_list=["group1","group2"])
print(msg.message_from)
print(msg.message_type)
print(msg.content_type)
print(msg.content)
print(msg.client_name)
print(msg.group_list)
import pickle
msg_in_bytes=pickle.dumps(msg) //convert object to bytes
print(msg_in_bytes)
msg_received=pickle.loads(msg_in_bytes)
print(type(msg_received))
print(msg_received.message_from) //convert bytes to object
print(msg_received.message_type)
print(msg_received.content_type)
print(msg_received.content)
print(msg_received.client_name)
print(msg_received.group_list)
class client:
    peers={}
    username=""
    password=""
    roll_no=""
    logged_in=False
    
    
    def __init__(self,uname,pword):
        self.username=uname
        self.uname=pword
    
    def sign_up():
        msg=message("CLI","SIGN_UP","text",password,client_name=self.username)
        send_to_serv(msg)
        
    def sign_in(username,password):
        create_shared_key()
        msg=message("CLI","SIGN_IN","text",password,client_name=self.username)
        send_to_serv(msg)
        
        
    def send_client(reciever_name,message,type,file_name,file_type):
        if client_name not in peers:
            msg=message("CLI","SOCK_REQ",type,bytes(receievr_name),client_name=self.username)
            send_to_serv(msg)
        msg=message("CLI","NORMAL_MSG",type,bytes(message,"utf-8"),client_name=username)
        cipher_text=des3.encrypt(msg,peers[reciver_name][0])
        send_to_recv(peers[receiver_name][1],cipher_text)
        
    def send_nonce_req(group_list=[],message,type):
        msg=message("CLI","NONCE_REQ","text","",client_name=self.username,group_list)
        
    def send_grp_msg(group_list=[],message,type,file_name,file_type,nonce):
        cipher_text=des3.encrypt(msg,nonce)
        msg=message("CLI","GRP_MSG",type,cipher_text,file_name,file_type,self.username,group_list)
        send_to_serv(msg)
        
    def parse_input(input_statement):
        
        
    def parse_response(recieved_msg):
        recieved=pickle.loads(recived_msg)
        if(recieved.message_type=="SIGN_UP_RES"):
            print(recieved.message_content)
            return
        if(recieved.message_type=="SIGN_IN_RES"):
            print(recieved.message_content)
            return
        if(recieved.message_type=="NORMAL_MSG"):
            if(recieved.content_type=="text")
                ans=des3.decrypt_(recieved.content,peers[recieved.client_name][1])
            #convert ans in bytes to string
                print(ans)
            else:
                #decrypt and write to a file
        if(recieved.message_type=="KEY_EX"):
            shared_key=diffie_generate_shared_key(recived_msg.content)
            peers[recieved.client_name].append(shared_key)
            public_key=diffie_generate_public_key()
            msg=message("CLI","KEY_EX_RESP","text",public_key,"","",self.username,[])
            send(msg)
        if(recieved.message_type=="KEY_EX_RESP"):
            shared_key=diffie_generate_shared_key(recieved_msg.content)
            peers[recieved.client_name].append(shared_key)
            
        if(recieved.message_type=="SOCK_RES"):
            peers[recieved.client_name]=[recieved.content]
        if(recieved.message_type=="GRP_MSG"):
            if(recieved.content_type=="text"):
                ans=des3.decrypt(recieved.content,password)
                #convert ans in bytes to string
            else:
                #decrypt and write to a file
            
        if(recieved.message_type=="NONCE_RESP"):
            nonce=des3.decrypt(recieved.content,)
            
            
            
            
        
    def listen_on_port():"""
        
        
        
        
        
        
        
        
        
    
    
