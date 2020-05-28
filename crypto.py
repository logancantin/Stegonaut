import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass


def getPass():
    passphrase = getpass.getpass('Enter a passphrase: ')
    if passphrase == getpass.getpass('Verify your passphrase: '):
        return passphrase
    else:
        print("Passwords do not match. Try again.")
        return getPass()

def generateCustomKey(password, salt=None):
    if password == None:
        password = getPass()
    
    if salt == None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm= hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

    key = base64.urlsafe_b64encode(kdf.derive(password.encode('ascii')))


    return salt, key

def encryptData(data, password=None):
    salt, key = generateCustomKey(password)

    f = Fernet(key)
    token = f.encrypt(data)

    return salt, token

def decryptData(token, salt, password=None):
    _, key = generateCustomKey(password, salt)
    
    f = Fernet(key)
    data = f.decrypt(token)

    return data


