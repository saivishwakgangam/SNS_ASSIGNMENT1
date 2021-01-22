class Message:
    def __init__(self,message_from,message_type,content_type,content,file_name,file_type,client_rollnumber,client_name,client_password,client_portno,group_list,receiver_present):
        self.message_from=message_from
        self.message_type=message_type
        self.content_type=content_type
        self.content=content
        self.file_name=file_name
        self.file_type=file_type
        self.client_rollnumber=client_rollnumber
        self.client_name=client_name
        self.client_password=client_password
        self.client_portno=client_portno
        self.group_list=group_list.copy()
        self.receiver_present=receiver_present
    
    def empty(self):
        self.message_from=""
        self.message_type=""
        self.content_type=""
        self.content=b''
        self.file_name=""
        self.file_type=""
        self.client_rollnumber=""
        self.client_name=""
        self.client_password=""
        self.client_portno=""
        self.group_list=[]
        self.receiver_present=False