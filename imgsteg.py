from PIL import Image
import numpy as np
import sys
from file import File

#Utility Functions

# Value must be 1 or 0
def setbit(num, index, value):
    mask = np.ones(num.size, dtype='uint8') << index
    temp = num & ~ mask #Clearing the bit
    return temp | value #Setting the bit to the value


def readbit(num, index):
    mask = np.ones(num.size, dtype='uint8')
    return num & (mask << index)

def str2bits(string):
    bytevalues = list(bytes(string, 'ascii')) #Encoding string to list of byte values
    bytestrings = [bin(x)[2:] for x in bytevalues] #Converting to binary string and removing '0b'
    bits = "" #String to hold the bits when complete
    
    i = 0 #current bit counter
    for byte in bytestrings:

        #Prepending a 0 to make sure the byte is 7 digits long
        while len(byte) < 7:
            byte = "0" + byte
        
        bits += byte
    
    #Return the bits
    return bits


def bits2str(bits):
    '''
    Converts from a bitstring to a string. Uses ascii encoding.
    '''

    #Take the bitstring and divide it into blocks of 7. Convert each block to an integer
    bytevalues = [int(x, 2) for x in [bits[i:i+7] for i in range(0, len(bits), 7)]]

    #Decode the byte information into a string
    message = bytes(bytevalues).decode('ascii')

    #Return the string
    return message

def img2bits(filename):
    image = open(filename, 'rb')
    data = list(image.read())
    bytestring = [bin(x)[2:] for x in data]

    bits = ""
    for byte in bytestring:
        while len(byte) < 8:
            byte = "0" + byte
        bits += byte

    return bits

def bits2img(bits, filename):

    #Take the bitstring and divide it into blocks of 7. Convert each block to an integer
    bytevalues = [int(x, 2) for x in [bits[i:i+8] for i in range(0, len(bits), 8)]]

    #Decode the byte information into a string
    payload = bytes(bytevalues)

    #Writes to the appropriate file name
    f = open(filename, 'wb')
    f.write(payload)
    f.close()


#Encoding functions
def encodeRGB(carrier, payload_file, password=None, encrypted=False):

    if type(carrier)==str:
        carrier = Image.open(carrier)
    if type(payload_file)==str:
        payload_file = File.open(payload_file)

    #Getting the image data in array form and its original shape
    data = np.asarray(carrier)
    original_shape = data.shape

    #Putting pixel data into one straight line
    data.shape = np.prod(original_shape)

    #Getting file as a bitstring
    bitstring = payload_file.makeBitstring(password=password, encrypted=encrypted)

    #Getting the int values for each bit in the payload
    bits = np.uint8([int(c, 2) for c in bitstring])

    #Making sure that the hidden data will fit in the carrier
    if len(bits) > len(data):
        print("Secret file is larger than the carrier! Pick a larger carrier or smaller secret.")
        exit()

    #Getting the same number of bytes from the image data
    modified_data = data[:len(bits)]

    #Setting the LSB to the payload data
    modified_data = setbit(modified_data, 0, bits)

    #Adding the new bits back into the image data
    data = np.concatenate((modified_data, data[len(bits):]))

    #Reshaping the image data
    data.shape = original_shape
    
    #Generating the new image and returning it
    newImage = Image.fromarray(data, mode='RGB')
    return newImage

def decodeRGB(image, password=None):

    if type(image)==str:
        image = Image.open(image)

    #Getting the image size and data
    width, height = image.size
    imgdata = np.uint8(image.getdata())

    #Getting the important bytes from the data
    payload_imgdata = imgdata.reshape(width * height * 3)

    #Reading LSB and concatenating into one string
    payload_array = [str(x) for x in list(readbit(payload_imgdata, 0))]
    payload_bitstring = ''.join(payload_array)
    
    return File.fromBitstring(payload_bitstring, password=password)

