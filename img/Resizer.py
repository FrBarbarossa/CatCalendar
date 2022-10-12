import os
from PIL import Image
from os import listdir
from os.path import isfile, join

files = [i for i in os.listdir() if i.endswith('jpg')]

for i in files:
    img = Image.open(i)
    img = img.resize((250, 250),  Image.Resampling.LANCZOS)
    img.save(i)
