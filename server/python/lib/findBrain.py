# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 20:26:40 2019

@author: 张立辉
"""


import matplotlib.pyplot as plt
import numpy as np
from Stack import Stack
from axis import findAxis

def load_contigent_area_I(x0,y0,img,IMGSIZE):
    temp = []
    
    if x0 + 1 < IMGSIZE:
        temp.append(img[x0+1][y0])
        temp.append(img[x0+1][y0-1])
        temp.append(img[x0+1][y0+1])
    
    temp.append(img[x0][y0-1])
    temp.append(img[x0][y0+1])
    
    if x0 - 1 > 0:
        temp.append(img[x0-1][y0-1])
        temp.append(img[x0-1][y0])
        temp.append(img[x0-1][y0+1])
    
    return temp

def Is_In_Range(value, withBone=True):
    for i in value:
        if withBone:
            if i <= 0 or i > 200:
                return False
        else:
            if i <= 0:
                return False
    return True

def Print_Image(x0,y0,proto_image,new_image):
    new_image[x0+1][y0] = proto_image[x0+1][y0]
    new_image[x0+1][y0+1] = proto_image[x0+1][y0+1]
    new_image[x0+1][y0-1] = proto_image[x0+1][y0-1]
    
    new_image[x0][y0] = proto_image[x0][y0]
    new_image[x0][y0-1] = proto_image[x0][y0-1]
    new_image[x0][y0+1] = proto_image[x0][y0+1]
    
    new_image[x0-1][y0] = proto_image[x0-1][y0]
    new_image[x0-1][y0+1] = proto_image[x0-1][y0+1]
    new_image[x0-1][y0-1] = proto_image[x0-1][y0-1]
    
def Push(x0,y0,s: Stack,printed):
    if printed[x0+1][y0] != 1:
        s.push((x0+1,y0))
        printed[x0+1][y0] = 1
    if printed[x0+1][y0+1] != 1:
        s.push((x0+1,y0+1))
        printed[x0+1][y0+1] = 1
    if printed[x0+1][y0-1] != 1:
        s.push((x0+1,y0-1))
        printed[x0+1][y0-1] = 1
    
    if printed[x0][y0+1] != 1:
        s.push((x0,y0+1))
        printed[x0][y0+1] = 1
    if printed[x0][y0-1] != 1:
        s.push((x0,y0-1))
        printed[x0][y0-1] = 1
    
    if printed[x0-1][y0] != 1:
        s.push((x0-1,y0))
        printed[x0-1][y0] = 1
    if printed[x0-1][y0-1] != 1:
        s.push((x0-1,y0-1))
        printed[x0-1][y0-1] = 1 
    if printed[x0-1][y0+1] != 1:
        s.push((x0-1,y0+1))
        printed[x0-1][y0+1] = 1
        
def extractBrain(img, IMGSIZE):
    stackWithBone = Stack()
    stackWithoutBone = Stack()

#    img = cv2.imread(path,0)
#    img = cv2.resize(img, (IMGSIZE,IMGSIZE))
    
    new_img_withBone = np.zeros((IMGSIZE,IMGSIZE), dtype=np.uint16)
    new_img_withoutBone = np.zeros((IMGSIZE,IMGSIZE), dtype=np.uint16)
    printed_withBone = np.zeros((IMGSIZE,IMGSIZE), dtype=np.uint16)
    printed_withoutBone = np.zeros((IMGSIZE,IMGSIZE), dtype=np.uint16)
    new_img_boneOnly = np.zeros((IMGSIZE,IMGSIZE), dtype=np.uint16)
    
    x0 = None
    y0 = None
    flag = False
    half = round(IMGSIZE / 2)
    for i in range(half, IMGSIZE):
        for j in range(half, IMGSIZE):
            value = load_contigent_area_I(j, i, img, IMGSIZE)
            
            if img[j][i] > 0 and Is_In_Range(value):
                x0 = j
                y0 = i
                flag = True
                break
        if flag:
            break
    
    stackWithBone.push((x0,y0))
    stackWithoutBone.push((x0, y0))

    while not stackWithoutBone.isEmpty():
        (x0,y0) = stackWithoutBone.pop()
        
        if img[x0][y0] > 0 and img[x0][y0] < 200 and x0 > 5 and x0 < 195 and y0 > 5 and y0 < 195:
            new_img_withoutBone[x0][y0] = img[x0][y0]
            Push(x0, y0, stackWithoutBone, printed_withoutBone)
        
#        if x0 > 5 and x0 < 195 and y0 > 5 and y0 < 195:
#            value = load_contigent_area_I(x0,y0,img)
#            if Is_In_Range(value):
#                Print_Image(x0,y0,img,new_img_withoutBone)
#                Push(x0,y0,stackWithoutBone,printed_withoutBone)
    
    while not stackWithBone.isEmpty():
        (x0,y0) = stackWithBone.pop()
        
        if img[x0][y0] > 0 and x0 > 5 and x0 < 180 and y0 > 5 and y0 < 180:
            Print_Image(x0, y0, img, new_img_withBone)
            Push(x0, y0, stackWithBone, printed_withBone)
#        if x0 > 5 and x0 < 180 and y0 > 5 and y0 < 180:
#            value = load_contigent_area_I(x0,y0,img)
#            
#            if Is_In_Range(value, False):
#                Print_Image(x0,y0,img,new_img_withBone)
#                Push(x0,y0,stackWithBone,printed_withBone)
            
    for i in range(0, IMGSIZE):
        for j in range(0, IMGSIZE):
            if new_img_withBone[i][j] > 200:
                new_img_boneOnly[i][j] = new_img_withBone[i][j] 
    return (new_img_withBone, new_img_withoutBone, new_img_boneOnly)