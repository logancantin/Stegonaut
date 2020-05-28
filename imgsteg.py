from PIL import Image
import numpy as np
import sys
from file import File

# Value must be 1 or 0
def setbit(num, index, value):
    mask = np.ones(num.size, dtype='uint8') << index
    num &= ~ mask #Clearing the bit
    num |= value #Setting the bit to the value
    return num


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


def encodeRGB(carrier, payload_file, password=None, encrypted=False):
    #Getting the image dimensions and data
    width, height = carrier.size
    data = np.uint8(carrier.getdata())

    #Putting pixel data into one straight line
    data.shape = width * height * 3

    #Getting file as a bitstring
    bitstring = payload_file.makeBitstring(password=password, encrypted=encrypted)

    #Getting the int values for each bit in the payload
    bits = np.uint8([int(c, 2) for c in bitstring])

    #Getting the same number of bytes from the image data
    modified_data = data[:len(bits)]

    #Setting the LSB to the payload data
    modified_data = setbit(modified_data, 0, bits)

    #Adding the new bits back into the image data
    data[:len(bits)] = modified_data

    #Reshaping the image data
    data.shape = (width, height, 3)
    
    #Generating the new image and returning it
    newImage = Image.fromarray(data)
    return newImage

def decodeRGB(image, password=None):
    #Getting the image size and data
    width, height = image.size
    imgdata = np.uint8(image.getdata())

    #Getting the important bytes from the data
    payload_imgdata = imgdata.reshape(width * height * 3)

    #Reading LSB and concatenating into one string
    payload_array = [str(x) for x in list(readbit(payload_imgdata, 0))]
    payload_bitstring = ''.join(payload_array)
    
    return File.fromBitstring(payload_bitstring)


'''
def encode(options):
    
    payload_raw_bytes = bytes()

    #Getting data to be concealed
    if options['stegtype'] == 'text':
        payload_raw_bytes = str2bits(options['payload_text'])
    else:
        with open(options['payload_path'], 'rb') as f:
            payload_raw_bytes = f.read()

    stegoimage = encodeRGB(albert, img2bits("cat-icon.png"))

    stegoimage.save("albert-cat-stego.png")

def decode():
    pass

'''





'''
process = input("(E)ncode or (D)ecode? ")

if process == 'E':
    payload = input("What message would you like to hide? ")

    image = Image.open("newalbert.png")

    stegimg = encodeRGB(image, str2bits(payload))

    stegimg.save("newalbert.png")

elif process == 'D':
    key = input("Decode: What is the key? ")
    decodeRGB(Image.open("newalbert.png"), int(key))
'''