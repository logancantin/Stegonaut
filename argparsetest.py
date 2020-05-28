import argparse
import imgsteg
from PIL import Image
from file import File


parser = argparse.ArgumentParser('stegonaut', description="Hide information in plain sight!")
group = parser.add_mutually_exclusive_group(required=True)

group.add_argument('-d', '--decode', action='store_const', dest='action', const='decode', help='Decode a steganographic file')
group.add_argument('-e', '--encode', action='store_const', dest='action', const='encode', help='Encode a steganographic file')

parser.add_argument('carrier', help='Carrier file')
parser.add_argument('secret_file', help='File to be hidden', nargs='?')

args = parser.parse_args()

if args.action == 'encode':
    if args.secret_file == None:
        print('Please provide a secret file to hide.')
        exit()
    
    carrier = Image.open(args.carrier)
    secret = File.open(args.secret_file)
    stegimg = imgsteg.encodeRGB(carrier, secret)

    stegimg.save('steg.png')

if args.action == 'decode':
    carrier = Image.open(args.carrier)
    secret = imgsteg.decodeRGB(carrier)
    secret.save('output')




