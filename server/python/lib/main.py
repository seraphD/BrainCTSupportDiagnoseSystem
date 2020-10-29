# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 17:07:38 2020

@author: 张立辉
"""

from findBrain import extractBrain
import matplotlib.pyplot as plt
from axis import findAxis, Line, Point, drawAxis, calcu, findStartEnd
import numpy as np
import math
import cv2
import os
envpath = "/home/lihui/medical-support/server/python/"
stages = np.load("{}/constant/stages.npy".format(envpath))
stage1, stage2, stage3, stage4, stage5, stage6, stage7, stage8, stage9 = stages

FrontalData = []
ParietalData = []
OccitalData = []
TemporalData = []

FrontalPData = []
ParietalPData = []
OccipitalPData = []
TemporalPData = []

def calcuArea(pic, IMGSIZE, half):
    area_left = 0
    area_right = 0
    
    for i in range(IMGSIZE):
        start_f_left = False
        start_f_right = False
        l_left = 0
        r_left = 0
        
        for j in range(half):
            if pic[i][j] > 0:
                r_left = j + 1
                
                if not start_f_left:
                    start_f_left = True
                    l_left = j
                    r_left = j + 1
        
        l_right = 0
        r_right = 0
        for j in range(half, IMGSIZE):
            if pic[i][j] > 0:
                r_right = j
                
                if not start_f_right:
                    start_f_right = True
                    l_right = j
                    r_right = j + 1
    
        area_left += r_left - l_left
        area_right += r_right - l_right
    return (area_left if area_left > 0 else area_left + 1, 
            area_right if area_right > 0 else area_right + 1)

def convertK2Degree(k):
    arc = math.atan(k)
    degree = math.degrees(arc)
    return degree

def convertK2Bios(k):
    return abs(math.cos(math.atan(k)))

def seperate(x, y, line):
    if convertK2Degree(line.k) != 90:
        if y - line.k * x - line.b > 0:
            return True
        else:
            return False

def printIMG(img1, img2, x, y, line, IMGSIZE):
    originalP = Point()
    originalP.change(x, y)
    oppositeP = calcu(originalP, line)
    ox = oppositeP.x
    oy = oppositeP.y
    
    img1[x][y] = img2[x][y]
    
    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE:
        img1[ox][oy] = img2[ox][oy]
    
    return (ox, oy)

def findSeperateLine(ratio, k, start, end, line, pic):
    x = int(round((start.x + (end.x - start.x) * ratio)) * convertK2Bios(line.k))
    y = int(round(line.k * x + line.b))
    p = Point()
    p.change(x, y)
    edgePoint = Point()
    degree = convertK2Degree(k)
    seperateLine = None
    
    if line.k != 0: 
        l = Line(convertK2Degree(-1/line.k), p)
        
        for i in range(0, y, 1):
            j = (i - l.b)/l.k
            
            if pic[round(j)][i] > 0:
                edgePoint.change(j, i)
                break
    else:
        for i in range(0, y, 1):
            if pic[x][i] > 0:
                edgePoint.change(x, i)
                break
    
    seperateLine = Line(degree, edgePoint)
    return seperateLine

def findEdgePoint(ratio, k, start, end, line, pic, IMGSIZE = 200):
    x = int(round((start.x + (end.x - start.x) * ratio)) * convertK2Bios(line.k))
    y = int(round(line.k * x + line.b))
    p = Point()
    p.change(x, y)
    edgePoint = Point()
    
    if line.k != 0: 
        l = Line(convertK2Degree(-1/line.k), p)
        
        for i in range(0, y, 1):
            j = round((i - l.b)/l.k)
            
            if j < IMGSIZE and pic[j][i] > 0:
                edgePoint.change(j, i)
                break
    else:
        for i in range(0, y, 1):
            if pic[x][i] > 0:
                edgePoint.change(x, i)
                break
    return edgePoint

def transferImg(imgs, axis, IMGSIZE):
    temp = []
    
    for img in imgs:
        p = axis.pivot
        matRotate = cv2.getRotationMatrix2D((p.x, p.y), -1 * axis.degree, 1)
        dst = cv2.warpAffine(img, matRotate, (IMGSIZE, IMGSIZE))
        temp.append(dst)
    
    return temp
    
def structureStage3(stage, line, pic, start, end, IMGSIZE):
    FrontalLobe = np.zeros((IMGSIZE, IMGSIZE),  dtype=np.uint16)
    ParietalLobe = np.zeros((IMGSIZE, IMGSIZE),  dtype=np.uint16)
    K_arr = np.load("{}/constant/stage3/K.npy".format(envpath))
    ratio_arr = np.load("{}/constant/stage3/Ratio.npy".format(envpath))

    index = int(round((stage - stage2) * 114))
    
    if index == len(K_arr):
        index -= 1
    
    k = K_arr[index]
    ratio = ratio_arr[index]
    degree = convertK2Degree(k)
    
    edgePoint = findEdgePoint(ratio, k, start, end, line, pic)
    seperateLine = Line(degree, edgePoint)
    
    leftFrontalCnt = 0
    leftFrontalSum = 0
    rightFroantalCnt = 0
    rightFrontalSum = 0
    areaF = 0
    
    leftParietalCnt = 0
    leftParietalSum = 0
    rightParietalCnt = 0
    rightParietalSum = 0
    areaP = 0
#    drawAxis([seperateLine], pic, IMGSIZE)
    for i in range(0, IMGSIZE):
        start_f = False
        left = 0
        right = 0
        start_p = False
        leftP = 0
        rightP = 0
        for j in range(0, IMGSIZE):
            if j - line.k * i - line.b > 0:
                break
            else:
                originalP = Point()
                originalP.change(i, j)
                oppositeP = calcu(originalP, line)
                ox = oppositeP.x
                oy = oppositeP.y
                
                if j - seperateLine.k*i - seperateLine.b > 0:
                    FrontalLobe[i][j] = pic[i][j]
                    
                    if pic[i][j] > 0:
                        leftFrontalCnt += 1
                        leftFrontalSum += FrontalLobe[i][j]
                        
                        if not start_f:
                            start_f = True
                            left = j
                            right = oy
                    
                    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE:
                        FrontalLobe[ox][oy] = pic[ox][oy]
                        
                        if pic[ox][oy] > 0:
                            rightFroantalCnt += 1
                            rightFrontalSum += FrontalLobe[ox][oy]
                else:
                    ParietalLobe[i][j] = pic[i][j]
                    if pic[i][j] > 0:
                        leftParietalCnt += 1
                        leftParietalSum += ParietalLobe[i][j]
                        
                        if not start_p:
                            start_p = True
                            leftP = j
                            rightP = oy
                    
                    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE:
                        ParietalLobe[ox][oy] = pic[ox][oy]
                        
                        if pic[ox][oy] > 0:
                            rightParietalCnt += 1
                            rightParietalSum += ParietalLobe[ox][oy]
    FrontalArea_l, FrontalArea_r = calcuArea(FrontalLobe, IMGSIZE, line.pivot.y)
    ParietalArea_l, ParietalArea_r = calcuArea(ParietalLobe, IMGSIZE, line.pivot.y)
    if leftFrontalCnt == 0: leftFrontalCnt += 1
    if rightFroantalCnt == 0: rightFroantalCnt += 1
    if leftParietalCnt == 0: leftParietalCnt += 1
    if rightParietalCnt == 0: rightParietalCnt += 1
#    drawAxis([], ParietalLobe, IMGSIZE)
    return [[FrontalLobe, ParietalLobe], 
            [(leftFrontalSum / FrontalArea_l, rightFrontalSum / FrontalArea_r), 
            (leftParietalSum / ParietalArea_l, rightParietalSum / ParietalArea_r)],
             [(leftFrontalSum / leftFrontalCnt, rightFrontalSum / rightFroantalCnt),
              (leftParietalSum / leftParietalCnt, rightParietalSum / rightParietalCnt)]]

def structureStage4(stage, line, pic, start, end, IMGSIZE):
    FrontalLobe = np.zeros((IMGSIZE, IMGSIZE),  dtype=np.uint16)
    ParietalLobe = np.zeros((IMGSIZE, IMGSIZE),  dtype=np.uint16)
    OccipitalLobe = np.zeros((IMGSIZE, IMGSIZE), dtype=np.uint16)
    
    K_arr = np.load("{}/constant/stage4/K.npy".format(envpath))
    ratio_arr = np.load("{}/constant/stage4/Ratio.npy".format(envpath))
    
    index = int(round((stage - stage3) * 114))
    r1, r2 = ratio_arr[index]
    k1, k2 = K_arr[index]
    degree1 = convertK2Degree(k1)
    degree2 = convertK2Degree(k2)
    
    edgePoint = findEdgePoint(r1, k1, start, end, line, pic)
    seperateLine1 = Line(degree1, edgePoint)
    
    p = Point()
    x = int(round((start.x + (end.x - start.x) * r2)) * convertK2Bios(line.k))
    y = int(round(line.k * x + line.b))
    p.change(x, y)
    
    seperateLine2 = Line(degree2, p)
    
    leftFrontalCnt = 0
    leftFrontalSum = 0
    rightFrontalCnt = 0
    rightFrontalSum = 0
    
    leftParietalCnt = 0
    leftParietalSum = 0
    rightParietalCnt = 0
    rightParietalSum = 0
    
    leftOccipitalCnt = 0
    leftOccipitalSum = 0
    rightOccipitalCnt = 0
    rightOccipitalSum = 0
    
    for i in range(0, IMGSIZE):
        for j in range(0, IMGSIZE):
            if j - line.k * i - line.b > 0:
                break
            else:
                originalP = Point()
                originalP.change(i, j)
                oppositeP = calcu(originalP, line)
                ox = oppositeP.x
                oy = oppositeP.y
                
                if j - seperateLine1.k * i - seperateLine1.b > 0:
                    FrontalLobe[i][j] = pic[i][j]
                    
                    if pic[i][j] > 0:
                        leftFrontalCnt += 1
                        leftFrontalSum += FrontalLobe[i][j]
                    
                    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE:
                        FrontalLobe[ox][oy] = pic[ox][oy]
                        
                        if pic[ox][oy]:
                            rightFrontalCnt += 1
                            rightFrontalSum += FrontalLobe[ox][oy]
                elif j - seperateLine2.k * i - seperateLine2.b < 0:
                    ParietalLobe[i][j] = pic[i][j]
                    if pic[i][j] > 0:
                        leftParietalCnt += 1
                        leftParietalSum += ParietalLobe[i][j]
                    
                    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE:
                        ParietalLobe[ox][oy] = pic[ox][oy]
                        if pic[ox][oy] > 0:
                            rightParietalCnt += 1
                            rightParietalSum += ParietalLobe[ox][oy]
                else:
                    OccipitalLobe[i][j] = pic[i][j]
                    if pic[i][j] > 0:
                        leftOccipitalCnt += 1
                        leftOccipitalSum += OccipitalLobe[i][j]
                    
                    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE:
                        OccipitalLobe[ox][oy] = pic[ox][oy]
                        if pic[ox][oy] > 0:
                            rightOccipitalCnt += 1
                            rightOccipitalSum += OccipitalLobe[ox][oy]        
                        
#    drawAxis([seperateLine1, seperateLine2], pic, IMGSIZE)
    FrontalArea_l, FrontalArea_r = calcuArea(FrontalLobe, IMGSIZE, line.pivot.y)
    ParietalArea_l, ParietalArea_r = calcuArea(ParietalLobe, IMGSIZE, line.pivot.y)
    OccipitalArea_l, OccipitalArea_r = calcuArea(OccipitalLobe, IMGSIZE, line.pivot.y)
    
    if leftFrontalCnt == 0: leftFrontalCnt += 1
    if rightFrontalCnt == 0: rightFrontalCnt += 1
    if leftParietalCnt == 0: leftParietalCnt += 1
    if rightParietalCnt == 0: rightParietalCnt += 1
    if leftOccipitalCnt == 0: leftOccipitalCnt += 1
    if rightOccipitalCnt == 0: rightOccipitalCnt += 1
    return [[FrontalLobe, ParietalLobe, OccipitalLobe], 
            [(leftFrontalSum / FrontalArea_l, rightFrontalSum / FrontalArea_r),
            (leftOccipitalSum / OccipitalArea_l, rightOccipitalSum / OccipitalArea_r),
            (leftParietalSum / ParietalArea_l, rightParietalSum / ParietalArea_r)],
             [(leftFrontalSum / leftFrontalCnt, rightFrontalSum / rightFrontalCnt),
              (leftOccipitalSum / leftOccipitalCnt, rightOccipitalSum / rightOccipitalCnt),
              (leftParietalSum / leftParietalCnt, rightParietalSum / rightParietalCnt)]]

def structureStage5(stage, line, pic, start, end, IMGSIZE):
    FrontalLobe = np.zeros((IMGSIZE, IMGSIZE),  dtype=np.uint16)
    TemporalLobe = np.zeros((IMGSIZE, IMGSIZE), dtype=np.uint16)
    ParietalLobe = np.zeros((IMGSIZE, IMGSIZE),  dtype=np.uint16)
    OccipitalLobe = np.zeros((IMGSIZE, IMGSIZE), dtype=np.uint16)
    
    K_arr = np.load("{}/constant/stage5/K.npy".format(envpath))
    ratio_arr = np.load("{}/constant/stage5/Ratio.npy".format(envpath))
    
    index = int(round((stage - stage4) * 114))
    r1, r2, r3 = ratio_arr[index]
    k1, k2, k3, k4 = K_arr[index]
    
    edgePoint1 = findEdgePoint(r1, k1, start, end, line, pic)
    seperateLine1 = Line(convertK2Degree(k1) , edgePoint1)
    seperateLine2 = Line(convertK2Degree(k2), edgePoint1)
    
    edgePoint2 = findEdgePoint(r2, k3, start, end, line, pic)
    seperateLine3 = Line(convertK2Degree(k3), edgePoint2)
    
    linePoint = Point()
    x = int(round((start.x + (end.x - start.x) * r3)) * convertK2Bios(line.k))
    y = int(round(line.k * x + line.b))
    linePoint.change(x, y)
    seperateLine4 = Line(convertK2Degree(k4), linePoint)
    
    leftFrontalCnt = 0
    leftFrontalSum = 0
    rightFrontalCnt = 0
    rightFrontalSum = 0
    
    leftParietalCnt = 0
    leftParietalSum = 0
    rightParietalCnt = 0
    rightParietalSum = 0
    
    leftOccipitalCnt = 0
    leftOccipitalSum = 0
    rightOccipitalCnt = 0
    rightOccipitalSum = 0
    
    leftTemporalCnt = 0
    leftTemporalSum = 0
    rightTemporalCnt = 0
    rightTemporalSum = 0
    for i in range(0, IMGSIZE):
        for j in range(0, IMGSIZE):
            if j - line.k * i - line.b < 0:
                
                if seperateLine1.isRight(i, j):
                    ox, oy = printIMG(FrontalLobe, pic, i, j, line, IMGSIZE)
                    if pic[i][j] > 0:
                        leftFrontalCnt += 1
                        leftFrontalSum += pic[i][j]
                    
                    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE and pic[ox][oy] > 0:
                        rightFrontalCnt += 1
                        rightFrontalSum += pic[ox][oy]
                elif seperateLine2.isLeft(i, j) and seperateLine3.isLeft(i, j):
                    ox, oy = printIMG(TemporalLobe, pic, i, j, line, IMGSIZE)
                    if pic[i][j] > 0:
                        leftTemporalCnt += 1
                        leftTemporalSum += pic[i][j]
                    
                    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE and pic[ox][oy] > 0:
                        rightTemporalCnt += 1
                        rightTemporalSum += pic[ox][oy]
                elif seperateLine3.isRight(i, j) and seperateLine4.isLeft(i, j):
                    ox, oy = printIMG(ParietalLobe, pic, i, j, line, IMGSIZE)
                    if pic[i][j] > 0:
                        leftParietalCnt += 1
                        leftParietalSum += pic[i][j]
                    
                    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE and pic[ox][oy] > 0:
                        rightParietalCnt += 1
                        rightParietalSum += pic[ox][oy]
                elif seperateLine4.isRight(i, j) and seperateLine3.isRight(i, j):
                    ox, oy = printIMG(OccipitalLobe, pic, i, j, line, IMGSIZE)
                    if pic[i][j] > 0:
                        leftOccipitalCnt += 1
                        leftOccipitalSum += pic[i][j]
                    
                    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE and pic[ox][oy] > 0:
                        rightOccipitalCnt += 1
                        rightOccipitalSum += pic[ox][oy]
    FrontalArea_l, FrontalArea_r = calcuArea(FrontalLobe, IMGSIZE, line.pivot.y)
    TemporalArea_l, TemporalArea_r = calcuArea(TemporalLobe, IMGSIZE, line.pivot.y)
    ParietalArea_l, ParietalArea_r = calcuArea(ParietalLobe, IMGSIZE, line.pivot.y)
    OccipialArea_l, OccipitalArea_r = calcuArea(OccipitalLobe, IMGSIZE, line.pivot.y)
    
    if leftFrontalCnt == 0: leftFrontalCnt += 1
    if rightFrontalCnt == 0: rightFrontalCnt += 1
    if leftParietalCnt == 0: leftParietalCnt += 1
    if rightParietalCnt == 0: rightParietalCnt += 1
    if leftOccipitalCnt == 0: leftOccipitalCnt += 1
    if rightOccipitalCnt == 0: rightOccipitalCnt += 1
    if leftTemporalCnt == 0: leftTemporalCnt += 1
    if rightTemporalCnt == 0: rightTemporalCnt += 1
    
    return [[FrontalLobe, TemporalLobe, ParietalLobe, OccipitalLobe],
            [(leftFrontalSum / FrontalArea_l, rightFrontalSum / FrontalArea_r),
            (leftTemporalSum / TemporalArea_l, rightTemporalSum / TemporalArea_r),
            (leftParietalSum / ParietalArea_l, rightParietalSum / ParietalArea_r),
            (leftOccipitalSum / OccipialArea_l, rightOccipitalSum / OccipitalArea_r)],
             [(leftFrontalSum / leftFrontalCnt, rightFrontalSum / rightFrontalCnt),
              (leftTemporalSum / leftTemporalCnt, rightTemporalSum / rightTemporalCnt),
              (leftParietalSum / leftParietalCnt, rightParietalSum / rightParietalCnt),
              (leftOccipitalSum / leftOccipitalCnt, rightOccipitalSum / rightOccipitalCnt)]]

def structureStage6(stage, line, pic, start, end, IMGSIZE):
    FrontalLobe = np.zeros((IMGSIZE, IMGSIZE),  dtype=np.uint16)
    TemporalLobe = np.zeros((IMGSIZE, IMGSIZE), dtype=np.uint16)
    ParietalLobe = np.zeros((IMGSIZE, IMGSIZE),  dtype=np.uint16)
    OccipitalLobe = np.zeros((IMGSIZE, IMGSIZE), dtype=np.uint16)
    
    K_arr = np.load("{}/constant/stage6/K.npy".format(envpath))
    ratio_arr = np.load("{}/constant/stage6/Ratio.npy".format(envpath))
    
    index = int(round((stage - stage5) * 114))
    if index == len(ratio_arr):
        index -= 1
    
    ratios = ratio_arr[index]
    ks = K_arr[index]
    edgePoints = []
    seperateLines = []
    
    for r, k in zip(ratios, ks):
        edgePoint = findEdgePoint(r, k, start, end, line, pic)
        seperateLine = Line(convertK2Degree(k), edgePoint)
        
        edgePoints.append(edgePoint)
        seperateLines.append(seperateLine)
        
#    drawAxis(seperateLines, pic, IMGSIZE)
    leftFrontalCnt = 0
    leftFrontalSum = 0
    rightFrontalCnt = 0
    rightFrontalSum = 0
    
    leftParietalCnt = 0
    leftParietalSum = 0
    rightParietalCnt = 0
    rightParietalSum = 0
    
    leftOccipitalCnt = 0
    leftOccipitalSum = 0
    rightOccipitalCnt = 0
    rightOccipitalSum = 0
    
    leftTemporalCnt = 0
    leftTemporalSum = 0
    rightTemporalCnt = 0
    rightTemporalSum = 0
    for i in range(0, IMGSIZE):
        for j in range(0, IMGSIZE):
            seperateLine1, seperateLine2, seperateLine3 = seperateLines
            
            if j - line.k * i - line.b < 0:
                if seperateLine1.isRight(i, j):
                    ox, oy = printIMG(FrontalLobe, pic, i, j, line, IMGSIZE)
                    if pic[i][j] > 0:
                        leftFrontalCnt += 1
                        leftFrontalSum += pic[i][j]
                    
                    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE and pic[ox][oy] > 0:
                        rightFrontalCnt += 1
                        rightFrontalSum += pic[ox][oy]
                elif seperateLine2.isLeft(i, j) and seperateLine3.isLeft(i, j):
                    ox, oy = printIMG(TemporalLobe, pic, i, j, line, IMGSIZE)
                    if pic[i][j] > 0:
                        leftTemporalCnt += 1
                        leftTemporalSum += pic[i][j]
                    
                    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE and pic[ox][oy] > 0:
                        rightTemporalCnt += 1
                        rightTemporalSum += pic[ox][oy]
                elif seperateLine2.isRight(i, j) and seperateLine3.isLeft(i, j):
                    ox, oy = printIMG(ParietalLobe, pic, i, j, line, IMGSIZE)
                    if pic[i][j] > 0:
                        leftParietalCnt += 1
                        leftParietalSum += pic[i][j]
                    
                    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE and pic[ox][oy] > 0:
                        rightParietalCnt += 1
                        rightParietalSum += pic[ox][oy]
                elif seperateLine2.isRight(i, j) and seperateLine3.isRight(i, j):
                    ox, oy = printIMG(OccipitalLobe, pic, i, j, line, IMGSIZE)
                    if pic[i][j] > 0:
                        leftOccipitalCnt += 1
                        leftOccipitalSum += pic[i][j]
                    
                    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE and pic[ox][oy] > 0:
                        rightOccipitalCnt += 1
                        rightOccipitalSum += pic[ox][oy]
    FrontalArea_l, FrontalArea_r = calcuArea(FrontalLobe, IMGSIZE, line.pivot.y)
    TemporalArea_l, TemporalArea_r = calcuArea(TemporalLobe, IMGSIZE, line.pivot.y)
    ParietalArea_l, ParietalArea_r = calcuArea(ParietalLobe, IMGSIZE, line.pivot.y)
    OccipialArea_l, OccipitalArea_r = calcuArea(OccipitalLobe, IMGSIZE, line.pivot.y)
    
    if leftFrontalCnt == 0: leftFrontalCnt += 1
    if rightFrontalCnt == 0: rightFrontalCnt += 1
    if leftParietalCnt == 0: leftParietalCnt += 1
    if rightParietalCnt == 0: rightParietalCnt += 1
    if leftOccipitalCnt == 0: leftOccipitalCnt += 1
    if rightOccipitalCnt == 0: rightOccipitalCnt += 1
    if leftTemporalCnt == 0: leftTemporalCnt += 1
    if rightTemporalCnt == 0: rightTemporalCnt += 1
    
    return [[FrontalLobe, TemporalLobe, ParietalLobe, OccipitalLobe],
            [(leftFrontalSum / FrontalArea_l, rightFrontalSum / FrontalArea_r),
            (leftTemporalSum / TemporalArea_l, rightTemporalSum / TemporalArea_r),
            (leftParietalSum / ParietalArea_l, rightParietalSum / ParietalArea_r),
            (leftOccipitalSum / OccipialArea_l, rightOccipitalSum / OccipitalArea_r)],
             [(leftFrontalSum / leftFrontalCnt, rightFrontalSum / rightFrontalCnt),
              (leftTemporalSum / leftTemporalCnt, rightTemporalSum / rightTemporalCnt),
              (leftParietalSum / leftParietalCnt, rightParietalSum / rightParietalCnt),
              (leftOccipitalSum / leftOccipitalCnt, rightOccipitalSum / rightOccipitalCnt)]]

def structureStage7(stage, line, pic, start, end, IMGSIZE):
    FrontalLobe = np.zeros((IMGSIZE, IMGSIZE),  dtype=np.uint16)
    TemporalLobe = np.zeros((IMGSIZE, IMGSIZE),  dtype=np.uint16)
    OccipitalLobe = np.zeros((IMGSIZE, IMGSIZE),  dtype=np.uint16)
    
    K_arr = np.load("{}/constant/stage7/K.npy".format(envpath))
    ratio_arr = np.load("{}/constant/stage7/Ratio.npy".format(envpath))
    
    index = int(round((stage - stage6) * 114))
    ratios = ratio_arr[index]
    ks = K_arr[index]
    edgePoints = []
    seperateLines = []
    
    for r, k in zip(ratios, ks):
        edgePoint = findEdgePoint(r, k, start, end, line, pic)
        seperateLine = Line(convertK2Degree(k), edgePoint)
        
        edgePoints.append(edgePoint)
        seperateLines.append(seperateLine)
        
#    drawAxis(seperateLines, pic, IMGSIZE)
    leftFrontalCnt = 0
    leftFrontalSum = 0
    rightFrontalCnt = 0
    rightFrontalSum = 0
    
    leftOccipitalCnt = 0
    leftOccipitalSum = 0
    rightOccipitalCnt = 0
    rightOccipitalSum = 0
    
    leftTemporalCnt = 0
    leftTemporalSum = 0
    rightTemporalCnt = 0
    rightTemporalSum = 0
    for i in range(0, IMGSIZE):
        for j in range(0, IMGSIZE):
            seperateLine1, seperateLine2 = seperateLines
            if j - line.k * i - line.b < 0:
                if seperateLine1.isRight(i, j):
                    ox, oy = printIMG(FrontalLobe, pic, i, j, line, IMGSIZE)
                    if pic[i][j] > 0:
                        leftFrontalCnt += 1
                        leftFrontalSum += pic[i][j]
                    
                    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE and pic[ox][oy] > 0:
                        rightFrontalCnt += 1
                        rightFrontalSum += pic[ox][oy]
                elif seperateLine2.isLeft(i, j):
                    ox, oy = printIMG(TemporalLobe, pic, i, j, line, IMGSIZE)
                    if pic[i][j] > 0:
                        leftTemporalCnt += 1
                        leftTemporalSum += pic[i][j]
                    
                    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE and pic[ox][oy] > 0:
                        rightTemporalCnt += 1
                        rightTemporalSum += pic[ox][oy]
                elif seperateLine2.isRight(i, j):
                    ox, oy = printIMG(OccipitalLobe, pic, i, j, line, IMGSIZE)
                    if pic[i][j] > 0:
                        leftOccipitalCnt += 1
                        leftOccipitalSum += pic[i][j]
                    
                    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE and pic[ox][oy] > 0:
                        rightOccipitalCnt += 1
                        rightOccipitalSum += pic[ox][oy]
                        
    FrontalArea_l, FrontalArea_r = calcuArea(FrontalLobe, IMGSIZE, line.pivot.y)
    TemporalArea_l, TemporalArea_r = calcuArea(TemporalLobe, IMGSIZE, line.pivot.y)
    OccipialArea_l, OccipitalArea_r = calcuArea(OccipitalLobe, IMGSIZE, line.pivot.y)
    
    if leftFrontalCnt == 0: leftFrontalCnt += 1
    if rightFrontalCnt == 0: rightFrontalCnt += 1
    if leftOccipitalCnt == 0: leftOccipitalCnt += 1
    if rightOccipitalCnt == 0: rightOccipitalCnt += 1
    if leftTemporalCnt == 0: leftTemporalCnt += 1
    if rightTemporalCnt == 0: rightTemporalCnt += 1
    
    return [[FrontalLobe, TemporalLobe, OccipitalLobe],
            [(leftFrontalSum / FrontalArea_l, rightFrontalSum / FrontalArea_r),
            (leftTemporalSum / TemporalArea_l, rightTemporalSum / TemporalArea_r),
            (leftOccipitalSum / OccipialArea_l, rightOccipitalSum / OccipitalArea_r)],
             [(leftFrontalSum / leftFrontalCnt, rightFrontalSum / rightFrontalCnt),
              (leftTemporalSum / leftTemporalCnt, rightTemporalSum / rightTemporalCnt),
              (leftOccipitalSum / leftOccipitalCnt, rightOccipitalSum / rightOccipitalCnt)]]
    
def structureStage8(stage, line, pic, start, end, IMGSIZE):
    TemporalLobe = np.zeros((IMGSIZE, IMGSIZE),  dtype=np.uint16)
    OccipitalLobe = np.zeros((IMGSIZE, IMGSIZE),  dtype=np.uint16)
    
    K_arr = np.load("{}/constant/stage8/K.npy".format(envpath))
    ratio_arr = np.load("{}/constant/stage8/Ratio.npy".format(envpath))
    
    index = int(round((stage - stage7) * 114))
    r = ratio_arr[index]
    k = K_arr[index]
    
    edgePoint = findEdgePoint(r, k, start, end, line, pic)
    seperateLine = Line(convertK2Degree(k), edgePoint)
    
#    drawAxis([seperateLine], pic, IMGSIZE)    
    leftOccipitalCnt = 0
    leftOccipitalSum = 0
    rightOccipitalCnt = 0
    rightOccipitalSum = 0
    
    leftTemporalCnt = 0
    leftTemporalSum = 0
    rightTemporalCnt = 0
    rightTemporalSum = 0
    for i in range(0, IMGSIZE):
        for j in range(0, IMGSIZE):
            if line.isLeft(i, j):
                if seperateLine.isLeft(i, j):
                    ox, oy = printIMG(TemporalLobe, pic, i, j, line, IMGSIZE)
                    if pic[i][j] > 0:
                        leftTemporalCnt += 1
                        leftTemporalSum += pic[i][j]
                    
                    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE and pic[ox][oy] > 0:
                        rightTemporalCnt += 1
                        rightTemporalSum += pic[ox][oy]
                else:
                    ox, oy = printIMG(OccipitalLobe, pic, i, j, line, IMGSIZE)
                    if pic[i][j] > 0:
                        leftOccipitalCnt += 1
                        leftOccipitalSum += pic[i][j]
                    
                    if ox > 0 and ox < IMGSIZE and oy > 0 and oy < IMGSIZE and pic[ox][oy] > 0:
                        rightOccipitalCnt += 1
                        rightOccipitalSum += pic[ox][oy]
    
    TemporalArea_l, TemporalArea_r = calcuArea(TemporalLobe, IMGSIZE, line.pivot.y)
    OccipialArea_l, OccipitalArea_r = calcuArea(OccipitalLobe, IMGSIZE, line.pivot.y)
    
    if leftOccipitalCnt == 0: leftOccipitalCnt += 1
    if rightOccipitalCnt == 0: rightOccipitalCnt += 1
    if leftTemporalCnt == 0: leftTemporalCnt += 1
    if rightTemporalCnt == 0: rightTemporalCnt += 1
    
    return [[TemporalLobe, OccipitalLobe],
            [(leftTemporalSum / TemporalArea_l, rightTemporalSum / TemporalArea_r),
            (leftOccipitalSum / OccipialArea_l, rightOccipitalSum / OccipitalArea_r)],
              [(leftTemporalSum / leftTemporalCnt, rightTemporalSum / rightTemporalCnt),
              (leftOccipitalSum / leftOccipitalCnt, rightOccipitalSum / rightOccipitalCnt)]]

def identifyStructure(line, pic, picWithBone,start, end, num, count, IMGSIZE):
    stage = num / count
    
    if stage < stage1:
        return (1, pic, None, None)
    elif stage < stage2:                
        area_left, area_right = calcuArea(pic, IMGSIZE, line.pivot.y)
        left = 0
        right = 0
        leftCnt = 0
        rightCnt = 0
        for i in range(IMGSIZE):
            for j in range(IMGSIZE):
                if pic[i][j] > 0:
                    if line.isLeft(i, j):
                        left += pic[i][j]
                        leftCnt += 1
                    else:
                        right += pic[i][j]
                        rightCnt += 1
        
        if leftCnt == 0: leftCnt += 1
        if rightCnt == 0: rightCnt += 1
        return (2, [pic], ((left / area_left, right / area_right)), [left / leftCnt, right / rightCnt])
    elif stage < stage3:
        tissue, data, pdata = structureStage3(stage, line, pic, start, end, IMGSIZE)
        return (3, tissue, data, pdata)
    elif stage < stage4:
        tissue, data, pdata = structureStage4(stage, line, pic, start, end, IMGSIZE)
        return (4, tissue, data, pdata)
    elif stage < stage5:
        tissue, data, pdata = structureStage5(stage, line, pic, start, end, IMGSIZE)
        return (5, tissue, data, pdata)
    elif stage < stage6:
        tissue, data, pdata = structureStage6(stage, line, pic, start, end, IMGSIZE)
        return (6, tissue, data, pdata)
    elif stage < stage7:
        tissue, data, pdata = structureStage7(stage, line, pic, start, end, IMGSIZE)
        return (7, tissue, data, pdata)
    elif stage < stage8:
        tissue, data, pdata = structureStage8(stage, line, pic, start, end, IMGSIZE)
        return (8, tissue, data, pdata)
    elif stage < stage9:
        tissue = pic
        return (9, tissue, None, None)
    else:
        return (10, None, None, None)
    
def saveIMG(img, path):
    if not os.path.exists(path):
        os.makedirs(path)
        
    picSet = os.listdir(path)
    size = len(picSet)
    cv2.imwrite("{}/{}.JPG".format(path, size), img)

def saveTissues(stage, index, tissue, data, pdata, path):
    if stage == 2:
        FrontalLobe = tissue[0]
        saveIMG(FrontalLobe, "{}/FrontalLobe".format(path))
        if data != None:
            FrontalData.append([data, stage, index])
        if pdata != None:
            FrontalPData.append([pdata, stage, index])
    elif stage == 3:
        FrontalLobe, ParietalLobe = tissue
        if data != None:
            FrontalAvg, ParietalAvg = data
            FrontalData.append([FrontalAvg, stage, index])
            ParietalData.append([ParietalAvg, stage, index])
        
        if pdata != None:
            FrontalPAvg, ParietalPAvg = pdata
            FrontalPData.append([FrontalPAvg, stage, index])
            ParietalPData.append([ParietalPAvg, stage, index])
            
        saveIMG(FrontalLobe, "{}/FrontalLobe".format(path))
        saveIMG(ParietalLobe, "{}/ParietalLobe".format(path))
    elif stage == 4:
        FrontalLobe, ParietalLobe, OccipitalLobe = tissue
        if data != None:
            FrontalAvg, ParietalAvg, OccipitalAvg = data
            FrontalData.append([FrontalAvg, stage, index])
            ParietalData.append([ParietalAvg, stage, index])
            OccitalData.append([OccipitalAvg, stage, index])
        
        if pdata != None:
            FrontalPAvg, ParietalPAvg, OccipitalPAvg = pdata
            FrontalPData.append([FrontalPAvg, stage, index])
            ParietalPData.append([ParietalPAvg, stage, index])
            OccipitalPData.append([OccipitalPAvg, stage, index])
            
        saveIMG(FrontalLobe, "{}/FrontalLobe".format(path))
        saveIMG(ParietalLobe, "{}/ParietalLobe".format(path))
        saveIMG(OccipitalLobe, "{}/OccipitalLobe".format(path))
    elif stage == 5:
        FrontalLobe, TemporalLobe, ParietalLobe, OccipitalLobe = tissue
        if data != None:
            FrontalAvg, TemporalAvg, ParietalAvg, OccipitalAvg = data
            FrontalData.append([FrontalAvg, stage, index])
            ParietalData.append([ParietalAvg, stage, index])
            OccitalData.append([OccipitalAvg, stage, index])
            TemporalData.append([TemporalAvg, stage, index])
        
        if pdata != None:
            FrontalPAvg, TemporalPAvg, ParietalPAvg, OccipitalPAvg = pdata
            FrontalPData.append([FrontalPAvg, stage, index])
            ParietalPData.append([ParietalPAvg, stage, index])
            OccipitalPData.append([OccipitalPAvg, stage, index])
            TemporalPData.append([TemporalPAvg, stage, index])
            
        saveIMG(FrontalLobe, "{}/FrontalLobe".format(path))
        saveIMG(ParietalLobe, "{}/ParietalLobe".format(path))
        saveIMG(OccipitalLobe, "{}/OccipitalLobe".format(path))
        saveIMG(TemporalLobe, "{}/TemporalLobe".format(path))
    elif stage == 6:
        FrontalLobe, TemporalLobe, ParietalLobe, OccipitalLobe = tissue
        if data != None:
            FrontalAvg, TemporalAvg, ParietalAvg, OccipitalAvg = data
            FrontalData.append([FrontalAvg, stage, index])
            ParietalData.append([ParietalAvg, stage, index])
            OccitalData.append([OccipitalAvg, stage, index])
            TemporalData.append([TemporalAvg, stage, index])
        
        if pdata != None:
            FrontalPAvg, TemporalPAvg, ParietalPAvg, OccipitalPAvg = pdata
            FrontalPData.append([FrontalPAvg, stage, index])
            ParietalPData.append([ParietalPAvg, stage, index])
            OccipitalPData.append([OccipitalPAvg, stage, index])
            TemporalPData.append([TemporalPAvg, stage, index])
            
        saveIMG(FrontalLobe, "{}/FrontalLobe".format(path))
        saveIMG(ParietalLobe, "{}/ParietalLobe".format(path))
        saveIMG(OccipitalLobe, "{}/OccipitalLobe".format(path))
        saveIMG(TemporalLobe, "{}/TemporalLobe".format(path))
    elif stage == 7:
        FrontalLobe, TemporalLobe, OccipitalLobe = tissue
        if data != None:
            FrontalAvg, TemporalAvg, OccipitalAvg = data
            FrontalData.append([FrontalAvg, stage, index])
            OccitalData.append([OccipitalAvg, stage, index])
            TemporalData.append([TemporalAvg, stage, index])
        
        if pdata != None:
            FrontalPAvg, TemporalPAvg, OccipitalPAvg = pdata
            FrontalPData.append([FrontalPAvg, stage, index])
            OccipitalPData.append([OccipitalPAvg, stage, index])
            TemporalPData.append([TemporalPAvg, stage, index])
            
        saveIMG(FrontalLobe, "{}/FrontalLobe".format(path))
        saveIMG(OccipitalLobe, "{}/OccipitalLobe".format(path))
        saveIMG(TemporalLobe, "{}/TemporalLobe".format(path))
    elif stage == 8:
        TemporalLobe, OccipitalLobe = tissue
        TemporalAvg, OccipitalAvg = data
        saveIMG(OccipitalLobe, "{}/OccipitalLobe".format(path))
        saveIMG(TemporalLobe, "{}/TemporalLobe".format(path))
        OccitalData.append([OccipitalAvg, stage, index])
        TemporalData.append([TemporalAvg, stage, index])
        
        if pdata != None:
            TemporalPAvg, OccipitalPAvg = pdata
            OccipitalPData.append([OccipitalPAvg, stage, index])
            TemporalPData.append([TemporalPAvg, stage, index])
        
    elif stage == 9:
        Cerebellum = tissue
        saveIMG(Cerebellum, "{}/Cerebellum".format(path))

def main(path, savepath):
    picSet = os.listdir(path)
    picSet.sort(key = lambda x: int(x[:-4]))
    size = len(picSet)
    IMGSIZE = 200
    
    index = round(size/5)
    img = cv2.imread(path+ "/" +picSet[index], 0)
    img = cv2.resize(img, (IMGSIZE,IMGSIZE))
    imgWithBone, imgWithoutBone, boneOnly = extractBrain(img, IMGSIZE)
    axis = findAxis(boneOnly, IMGSIZE)
    drawAxis([axis], imgWithBone, IMGSIZE)
    
    ch = input()
    if ch != "e":
        while not ch == "y":
            num = int(ch)
            axis.changeK(num)
            drawAxis([axis], imgWithBone, IMGSIZE)
            ch = input()
    else:
        return
    
    tempAxis = Line(axis.degree, axis.pivot)
    axis.changeK(- axis.degree)
    for index in range(size):
        img = cv2.imread(path+ "/" +picSet[index], 0)
        img = cv2.resize(img, (IMGSIZE,IMGSIZE))
        
        imgWithBone, imgWithoutBone, boneOnly = extractBrain(img, IMGSIZE)
#        axis, start, end = findAxis(boneOnly, IMGSIZE)
        imgWithBone, imgWithoutBone, boneOnly = transferImg([imgWithBone, imgWithoutBone, boneOnly], tempAxis, IMGSIZE)
        start, end = findStartEnd(imgWithBone, axis, IMGSIZE)
        
        try:
            stage, tissue, data, pdata = identifyStructure(axis, imgWithoutBone, imgWithBone, start, end, index, size, IMGSIZE)
        
            saveTissues(stage, index, tissue, data, pdata, savepath)
            print(stage)
        except Exception as e:
            print("fatal error!")
            print(e)
            pass
    
    if not os.path.exists(savepath):
        os.mkdir(savepath)
    
    if not os.path.exists(savepath + "/datas"):
        os.mkdir(savepath + "/datas")
    if not os.path.exists(savepath + "/pdatas"):
        os.mkdir(savepath + "/pdatas")
        
    np.save(savepath + "/datas/size.npy", size)
    if not os.path.exists(savepath + "/datas/FrontalData/"):
        os.mkdir(savepath + "/datas/FrontalData/")
    if not os.path.exists(savepath + "/pdatas/FrontalData/"):
        os.mkdir(savepath + "/pdatas/FrontalData/")
    for i in range(len(FrontalData)):
        data, stage, index = FrontalData[i]
        np.save(savepath + "/datas/FrontalData/{}.npy".format(index), FrontalData[i])
        np.save(savepath + "/pdatas/FrontalData/{}.npy".format(index), FrontalPData[i])
    
    if not os.path.exists(savepath + "/datas/ParietalData"):
        os.mkdir(savepath + "/datas/ParietalData")
    if not os.path.exists(savepath + "/pdatas/ParietalData"):
        os.mkdir(savepath + "/pdatas/ParietalData")
    for i in range(len(ParietalData)):
        data, stage, index = ParietalData[i]
        np.save(savepath + "/datas/ParietalData/{}.npy".format(index), ParietalData[i])
        np.save(savepath + "/pdatas/ParietalData/{}.npy".format(index), ParietalPData[i])
    
    if not os.path.exists(savepath + "/datas/TemporalData"):
        os.mkdir(savepath + "/datas/TemporalData")
    if not os.path.exists(savepath + "/pdatas/TemporalData"):
        os.mkdir(savepath + "/pdatas/TemporalData")
    for i in range(len(TemporalData)):
        data, stage, index = TemporalData[i]
        np.save(savepath + "/datas/TemporalData/{}.npy".format(index), TemporalData[i])
        np.save(savepath + "/pdatas/TemporalData/{}.npy".format(index), TemporalPData[i])
    
    if not os.path.exists(savepath + "/datas/OccipitalData"):
        os.mkdir(savepath + "/datas/OccipitalData")
    if not os.path.exists(savepath + "/pdatas/OccipitalData"):
        os.mkdir(savepath + "/pdatas/OccipitalData")
    for i in range(len(OccitalData)):
        data, stage, index = OccitalData[i]
        np.save(savepath + "/datas/OccipitalData/{}.npy".format(index), OccitalData[i])
        np.save(savepath + "/pdatas/OccipitalData/{}.npy".format(index), OccipitalPData[i])
        
def normolize(path):
    picSet = os.listdir(path)
    size = len(picSet)
    
    for i in range(size):
        originalName = picSet[i]
        newName = "{}.JPG".format(size - i)
        
        os.rename("{}/{}".format(path, originalName), "{}/{}".format(path, newName))
        
#path = "regulardata/normal/datas"
#picNameSet = os.listdir(path)
#
#for i in picNameSet:
#    FrontalData = []
#    ParietalData = []
#    OccitalData = []
#    TemporalData = []
#    
#    FrontalPData = []
#    ParietalPData = []
#    OccitalPData = []
#    TemporalPData = []
#    
#    picPath = path + "/" + i
#    main(picPath, "testresultsNormal/{}".format(i))

#path = "regulardata/normal/datas/"
#picNameSet = os.listdir(path)
#
#for i in picNameSet:
#    FrontalData = []
#    ParietalData = []
#    OccitalData = []
#    TemporalData = []
#    picPath = path + i
#    try:
#        normolize(picPath)
#    except Exception as e:
#        pass
#    main(picPath, "testresultsNormal/" + i)
    
#normolize("test")
#main("test", "testresults")