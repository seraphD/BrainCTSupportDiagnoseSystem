# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 16:10:03 2020

@author: 张立辉
"""

import sys
import getopt
import cv2
import os
import numpy as np
sys.path.append("/home/lihui/medical-support/server/python/lib/")
from axis import findAxis
from findBrain import extractBrain

envpath = "/home/lihui/medical-support/server/python/"
def drawAxis(lines, pic, IMGSIZE):
    temp = pic.copy()
    for i in range(0, IMGSIZE):
        for line in lines:
            j = round(line.k * i + line.b)
        
            if j > 0 and j < IMGSIZE:
                temp[i][j] = 300
    return temp

options,args = getopt.getopt(sys.argv[1:],"",["path="])
path = ""
IMGSIZE = 200
for name, value in options:
    if name in ("--path"):
        path = value

path = path.split("CT")[1][1:]
picSet = os.listdir("{}/CT/{}".format(envpath, path))
index = round(len(picSet) * 1 / 5)
img = cv2.imread("{}/CT/{}/{}".format(envpath, path ,picSet[index]), 0)
img = cv2.resize(img, (IMGSIZE, IMGSIZE))
imgWithBone, imgWithoutBone, boneOnly = extractBrain(img, IMGSIZE)
axis = findAxis(boneOnly, IMGSIZE)
imgWithAxis = drawAxis([axis], imgWithBone, IMGSIZE)

saveData = [axis.degree, axis.pivot.getXY()]

if not os.path.exists("{}/axis/{}".format(envpath, path)):
    os.makedirs("{}/axis/{}".format(envpath, path))

cv2.imwrite("{}/axis/{}/imgWithAxis.JPG".format(envpath, path), imgWithAxis)
cv2.imwrite("{}/axis/{}/originalImg.JPG".format(envpath, path), imgWithBone)
np.save("{}/axis/{}/axis.npy".format(envpath, path), saveData)