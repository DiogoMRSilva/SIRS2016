import bluetooth
import os
import base64
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from bluetooth_rfcomm_client import connect_to_phone_service
from bluetooth_rfcomm_client import exchange_communication_key
from bluetooth_rfcomm_client import request_file_key
from Crypto.Cipher import AES


class SmartphoneProxy:

    def __init__(self, android_mac, android_uuid, keySize):
        self.android_mac = android_mac
        self.android_uuid = android_uuid
        self.socket = connect_to_phone_service(android_mac, android_uuid)
        self.communication_key = Random.new().read(keySize/8)
        self.iv = Random.new().read(AES.block_size)
        self.sendCommunicationKey()

    # mock that should be replaced
    def decrypt_key(self, encrypted_key):
        padded_text = encodePKCS7(encrypted_key)

        e = AES.new(self.communication_key, AES.MODE_CBC, self.iv)
        cipher_text = e.encrypt(padded_text)
        encrypted = request_file_key(self.socket, cipher_text)
        e = AES.new(self.communication_key, AES.MODE_CBC, self.iv)
        decrypted = e.decrypt(encrypted)
        print("file key before decode:" + base64.b64encode(decrypted))
        print("file key after decode:" + base64.b64encode(decodePKCS7(decrypted)))
        return decodePKCS7(decrypted)
        #path = os.environ['HOME'] + '/pythoncipher/'
        #private_key = RSA.importKey(open(path + 'private_key.txt').read(), passphrase='password')
        #cipher = PKCS1_OAEP.new(private_key)
        #decrypted = cipher.decrypt(encrypted_key)

        #return decrypted

    def sendCommunicationKey(self):
        public_key = RSA.importKey(open(os.environ['HOME'] + '/pythoncipher/' + 'cert/public_key.txt').read(), passphrase='password')
        print(" public key:"+str(public_key.key)+ "\nkeydata:"+str(public_key.keydata))
        asymmetric_cipher = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)
        #asymmetric_cipher = PKCS1_OAEP.new(public_key)
        print("iv:"+base64.b64encode(self.iv) +"\nkey:" +base64.b64encode(self.communication_key))
        print("communication key size:"+str(len(self.communication_key)))
        encrypted_message = asymmetric_cipher.encrypt(self.iv + self.communication_key)
        print("message:" + base64.b64encode(encrypted_message) + "len(message)" + str(len(encrypted_message)))
        exchange_communication_key(self.socket, encrypted_message)

"""
def connect_to_phone_service(server_address, uuid):
    service = bluetooth.find_service(address=server_address, uuid=uuid)
    service = service[0]

    socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    try:
        socket.connect((server_address, service["port"]))
        print("MAC: " + server_address + "\nPort: " + str(service["port"]))
    except bluetooth.BluetoothError as e:
        print("Got an error: " + e)
        return None

    return socket
"""


def encodePKCS7(text):
    text_length = len(text)
    amount_to_pad = AES.block_size - (text_length % AES.block_size)
    if amount_to_pad == 0:
        amount_to_pad = AES.block_size
    pad = chr(amount_to_pad)
    return text + pad * amount_to_pad


def decodePKCS7(text):
    pad = ord(text[-1])
    return text[:-pad]


