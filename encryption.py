import hashlib
from Crypto.Cipher import DES3
import os

prime_number=671998030559713968361666935769 #p
generator=2  #

def gen_public_key(roll_number):
    private_key=os.urandom(24)
    key=str(private_key)+roll_number
    final_key=hashlib.sha256(key.encode()).hexdigest()
    private_key=int(final_key,16)
    sender_pub_key=int(pow(generator,private_key,prime_number))
    public_key=str(sender_pub_key)
    return (private_key,public_key)

def gen_shared_key(sender_public_key,private_key):
    shared_key=int(pow(sender_public_key,private_key,prime_number)) #S^a mod p/S^b modp
    return shared_key
    
def encrypt_des3(msg,shared_key):
    shared_key=shared_key[:24]
    cipher=DES3.new(shared_key,DES3.MODE_ECB)
    encrypted_message=cipher.encrypt(msg)
    return encrypted_message
    
def decrypt_des3(msg,shared_key):
    shared_key=shared_key[:24]
    cipher=DES3.new(shared_key,DES3.MODE_ECB)
    org=cipher.decrypt(msg)
    return org
