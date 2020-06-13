from PIL import Image
import numpy as np
from sys import argv

def analyzeLSB(image):
    temp = (np.uint8(image) & 1) * 255
    Image.fromarray(temp).save('lsb.png')

def layers(image):
    for x in range(8):
        temp = (np.uint8(image) & (0b1 << x)) * 255
        Image.fromarray(temp).show()



for file in argv[1:]:
    analyzeLSB(Image.open(file))
    