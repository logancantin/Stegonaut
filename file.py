import binascii
import os
import math
from cryptography.fernet import Fernet
import getpass
import crypto
import _io

def binformat(binstring, length=-1):
    binstring = binstring[2:]
    while len(binstring) < length:
        binstring = '0' + binstring
    return binstring

def bytes2bin(b):
    binstring = ''
    for byte in b:
        binstring += binformat(bin(byte), 8)
    
    return binstring

def bin2bytes(b):
    bytez = bytearray()
    counter = 0
    while counter < len(b):
        bytez += bytes([int(b[counter:counter+8], 2)])
        counter += 8
    return bytes(bytez)

def str2bin(s):
    return bytes2bin(s.encode('ascii'))

def bin2str(b):
    return bin2bytes(b).decode('ascii')

def int2bytes(i, numBytes=-1):
    if numBytes == -1:
        numBytes = math.ceil(math.log(i, 256))
    
    return bytes(
        [(i & (0b11111111 << (x * 8))) >> (x * 8) for x in reversed(range(numBytes))]
    )

def bytes2int(b):
    sum = 0
    i = 0
    for byte in reversed(b):
        sum |= byte << (i * 8)
        i += 1
    return sum

class File:

    LENGTH_BYTES = 4
    CHKSUM_BYTES = 4
    SALT_BYTES = 16
    EXTENSION_LENGTH_BYTES = 1

    #File data, length, and extension.
    data = bytes()
    length = 0
    extension = ''


    #Initializing a File object from a local file
    @staticmethod
    def open(path):
        if os.path.exists(path):

            file = File()

            #Reading data
            with open(path, 'rb') as f:
                file.data = f.read()

            #Getting the length of the data
            file.length = len(file.data)

            #Checking to make sure file length is an appropriate size
            if file.length >= 2 ** (8 * File.LENGTH_BYTES):
                raise Exception("File is too large! Limit is 4.2GB")


            #Getting the extension
            filename = path.split('/')[-1]
            file.extension = '.'.join(filename.split('.')[1:])

            return file

        #Path is invalid, alert the user     
        else:
            raise Exception("Path is invalid!")
    
    #Converting the File object into a bitstring representation, which can then be used for steganography
    def makeBitstring(self, encrypted=False, password=None):
        
        payload = bytes()
        salt = bytes()

        #Here begins the data to be encrypted (if applicable)
        unencrypted_bytes = bytearray()

        #Adding the length of the file extension
        unencrypted_bytes += bytes([len(self.extension)])

        #Adding the file extension
        unencrypted_bytes += self.extension.encode('ascii')

        #Appending the data
        unencrypted_bytes += self.data

        #Appending the checksum
        chksum = int2bytes(binascii.crc32(self.data))
        unencrypted_bytes += bytes(File.CHKSUM_BYTES - len(chksum)) + chksum

        if encrypted:
            salt, payload = crypto.encryptData(bytes(unencrypted_bytes), password)
        else:
            payload = bytes(unencrypted_bytes)

        

        header_bytes = bytearray()
        
        #First byte: Whether there is encryption or not
        header_bytes += bytes([0b11111111]) if encrypted == True else bytes([0])

        #Next 16 bytes: Salt, if encrypted. Otherwise, nothing.
        if encrypted:
            header_bytes += salt

        #Next <LENGTH_BYTES> bytes: length of the payload
        payload_length = len(payload)
        len_bytes = int2bytes(payload_length)
        header_bytes += bytes(File.LENGTH_BYTES-len(len_bytes)) + len_bytes

        header_bytes += payload

        return bytes2bin(header_bytes)

    #Initializing a File object from a bitstring
    @staticmethod
    def fromBitstring(bitstring, password=None):

        #Creating new File object
        file = File()

        salt = bytes()

        #List of bytes
        bitstring_bytes = bin2bytes(bitstring)

        #Position placeholder
        position = 0
        

        #Encryption
        if bitstring_bytes[position] != 0 and bitstring_bytes[position] != 255:
            print('not steganographic')
        #Setting whether there is encryption or not
        file.encrypted = bool(bitstring_bytes[position] & 1)
        position += 1

        #Getting the salt, if applicable
        if file.encrypted:
            salt = bitstring_bytes[position:position+File.SALT_BYTES]
            position += File.SALT_BYTES

        #Length
        payload_length = bytes2int(bitstring_bytes[position:position + File.LENGTH_BYTES])
        position += File.LENGTH_BYTES

        #Decrypting payload (if encrypted)
        decrypted_payload = bytes()

        if file.encrypted:
            decrypted_payload = crypto.decryptData(bitstring_bytes[position:position+payload_length], salt, password)
        else:
            decrypted_payload = bitstring_bytes[position:position+payload_length]

        #Position placeholder
        decrypted_position = 0

        #Extension Length
        len_extension = decrypted_payload[decrypted_position]
        decrypted_position += 1

        #Extension
        extension = decrypted_payload[decrypted_position:decrypted_position+len_extension].decode('ascii')
        file.extension = extension
        decrypted_position += len_extension


        #Data
        data = decrypted_payload[decrypted_position : -4]
        file.data = data
        file.length = len(data)
        del(data)


        #CRC
        crc = bytes2int(decrypted_payload[-4:])

        
        if binascii.crc32(file.data) != crc:
            print("Corruption! CRCs don't match.")


        return file
    
    def save(self, name):
        with open(name + '.' + self.extension, 'wb') as f:
            f.write(self.data)
 