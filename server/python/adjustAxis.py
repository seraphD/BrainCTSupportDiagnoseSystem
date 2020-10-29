# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 19:45:17 2020

@author: 张立辉
"""

import cv2
import getopt
import sys
import numpy as np
import matplotlib.pyplot as plt
sys.path.append("/home/lihui/medical-support/server/python/lib/")
from axis import Line, Point

envpath = "/home/lihui/medical-support/server/python"
def drawAxis(lines, pic, IMGSIZE):
    temp = pic.copy()
    for i in range(0, IMGSIZE):
        for line in lines:
            j = round(line.k * i + line.b)
        
            if j > 0 and j < IMGSIZE:
                temp[i][j] = 250
    showIMG(temp)
    return temp

def showIMG(img):
    plt.imshow(img)
    plt.show()

path = "0"
direction = "left"
scale = 0
IMGSIZE = 200
options,args = getopt.getopt(sys.argv[1:],"",["path=", "direction=", "scale="])
for name, value in options:
    if name == "--path":
        path = value
    elif name == "--direction":
        direction = value
    elif name == "--scale":
        scale = int(value)

path = path.split("CT")[1][1:]
img = cv2.imread("{}/axis/{}/originalImg.JPG".format(envpath, path), 0)
saveData = np.load("{}/axis/{}/axis.npy".format(envpath, path), allow_pickle=True)
p = Point()
degree, pivot = saveData
p.change(pivot[0], pivot[1])
axis = Line(degree, p)
print(axis.degree)

if direction == "left":
    axis.changeK(scale)
    print(axis.degree)
else:
    axis.changeK(-scale)
    print(axis.degree)

saveData = [axis.degree, axis.pivot.getXY()]
imgWithAxis = drawAxis([axis], img, IMGSIZE)
cv2.imwrite("{}/axis/{}/imgWithAxis.JPG".format(envpath, path), imgWithAxis)
np.save("{}/axis/{}/axis.npy".format(envpath, path), saveData)