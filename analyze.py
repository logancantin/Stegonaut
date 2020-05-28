from PIL import Image
import numpy as np
from sys import argv

def analyzeLSB(image):
    image.show()
    d = np.uint8(image)

    for x in [2**y for y in range(8)]:
        Image.fromarray((d & x) * 255).show()

for file in argv[1:]:
    analyzeLSB(Image.open(file))
    