# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 14:06:05 2020

@author: 张立辉
"""

from tensorflow.keras.models import load_model
import cv2
import os
import numpy as np
import sys
import getopt
sys.path.append("/home/lihui/medical-support/server/python/lib/")
from axis import findAxis, drawAxis, Line, findStartEnd, Point
from main import identifyStructure
from findBrain import extractBrain

envpath = "/home/lihui/medical-support/server/python"
CATEGORY = ['normal', 'abnormal']
model = load_model("{}/regularcheck-CNN.model".format(envpath))
IMGSIZE = 200

FrontalRegular = np.load("{}/regulardata/areaData/FrontalRegular.npy".format(envpath), allow_pickle=True)
ParietalRegualr = np.load("{}/regulardata/areaData/ParietalRegular.npy".format(envpath), allow_pickle=True)
TemporalRegular = np.load("{}/regulardata/areaData/TemporalRegular.npy".format(envpath), allow_pickle=True)
OccipitalRegular = np.load("{}/regulardata/areaData/OccipitalRegular.npy".format(envpath), allow_pickle=True)

pFrontalRegular = np.load("{}/regulardata/pointData/FrontalRegular.npy".format(envpath), allow_pickle=True)
pParietalRegualr = np.load("{}/regulardata/pointData/ParietalRegular.npy".format(envpath), allow_pickle=True)
pTemporalRegular = np.load("{}/regulardata/pointData/TemporalRegular.npy".format(envpath), allow_pickle=True)
pOccipitalRegular = np.load("{}/regulardata/pointData/OccipitalRegular.npy".format(envpath), allow_pickle=True)

accuracy = 0.2
paccuracy = 0.15
filepath = ""

def appendDiagnose(sentence, diagnose, img):
    if not sentence in diagnose:
        diagnose.append(sentence)

def check(datas, regularDatas, pregularDatas, tissues, diagnose, img):
    for data, regularData, pregularData, tissue in zip(datas, regularDatas, pregularDatas, tissues):
        rdata, pdata = data
        right, left = rdata
        pright, pleft = pdata
        rightRegular, leftRegular = regularData
        prightRegular, pleftRegular = pregularData
        sentence = ""
        
        if right < rightRegular * ( 1 - accuracy):
            if pright > prightRegular * (1 + paccuracy):
                sentence = "左侧" + tissue + "见高密度影"
                appendDiagnose(sentence, diagnose, img)
#                showImg(img)
            else:
                sentence = "左侧" + tissue + "见低密度影"
                appendDiagnose(sentence, diagnose, img)
#                showImg(img)
        
        if left < leftRegular * (1 - accuracy):
            if pleft > pleftRegular * (1 + paccuracy):
                sentence = "右侧" + tissue + "见高密度影"
                appendDiagnose(sentence, diagnose, img)
#                showImg(img)
            else:
                sentence = "右侧" + tissue + "见低密度影"
                appendDiagnose(sentence, diagnose. img)

def checkData(stage, data, pdata, diagnose, img):
    if stage == 2:
        check([data, pdata], [FrontalRegular], ["额叶"], diagnose, img)
    elif stage == 3:
        FrontalLobe, ParietalLobe = data
        check([data, pdata], [FrontalRegular, ParietalRegualr], [pFrontalRegular, pParietalRegualr],["额叶", "顶叶"], diagnose, img)
    elif stage == 4:
        FrontalLobe, ParietalLobe, OccipitalLobe = data
        check([data, pdata], [FrontalRegular, ParietalRegualr, OccipitalLobe], 
              [pFrontalRegular, pParietalRegualr, pOccipitalRegular]
              ["额叶", "顶叶", "枕叶"], diagnose, img)
    elif stage == 5:
        FrontalLobe, TemporalLobe, ParietalLobe, OccipitalLobe = data
        check([data, pdata], [FrontalRegular, TemporalRegular, ParietalRegualr, OccipitalLobe],
              [pFrontalRegular, pTemporalRegular,pParietalRegualr, pOccipitalRegular], 
              ["额叶", "颞叶","顶叶", "枕叶"], diagnose, img)
    elif stage == 6:
        FrontalLobe, TemporalLobe, ParietalLobe, OccipitalLobe = data
        check([data, pdata], [FrontalRegular, TemporalRegular, ParietalRegualr, OccipitalLobe],
              [pFrontalRegular, pTemporalRegular,pParietalRegualr, pOccipitalRegular], 
              ["额叶", "颞叶","顶叶", "枕叶"], diagnose, img)
    elif stage == 7:
        FrontalLobe, TemporalLobe, OccipitalLobe = data
        check([data, pdata], [FrontalRegular, TemporalRegular, OccipitalLobe],
              [pFrontalRegular, pParietalRegualr, pOccipitalRegular], 
              ["额叶", "颞叶", "枕叶"], diagnose, img)
    elif stage == 8:
        TemporalLobe, OccipitalLobe = data
        check([data, pdata], [TemporalRegular, OccipitalLobe], 
              [pTemporalRegular, pOccipitalRegular], 
              ["颞叶", "枕叶"], diagnose, img)
    else:
        pass
        

def transferImg(imgs, axis, IMGSIZE):
    temp = []
    
    for img in imgs:
        p = axis.pivot
        img = img.reshape(IMGSIZE, IMGSIZE)
        matRotate = cv2.getRotationMatrix2D((p.x, p.y), -1 * axis.degree, 1)
        dst = cv2.warpAffine(img, matRotate, (IMGSIZE, IMGSIZE))
        temp.append(dst)
    
    return temp

def prepare(filepath):
    pics = os.listdir(filepath)
    pics.reverse()
    array = []
    
    for i in pics:
        img = cv2.imread(filepath + "/{}".format(i), 0)
        img = cv2.resize(img, (200, 200))
        imgWithBone, imgWithoutBone, boneOnly = extractBrain(img, IMGSIZE)
        imgWithBone = imgWithBone / 255.0
        imgWithBone = imgWithBone.reshape(-1, IMGSIZE, IMGSIZE, 1)
        array.append([imgWithBone, imgWithoutBone, boneOnly])
    
    return array

options, args = getopt.getopt(sys.argv[1:],"",["path="])
for name, value in options:
    if name in ("--path"):
        filepath = value
path = filepath.split("CT")[1][1:]

saveData = np.load("{}/axis/{}/axis.npy".format(envpath, path), allow_pickle=True)
p = Point()
degree, pivot = saveData
p.change(pivot[0], pivot[1])
axis = Line(degree, p)

array = prepare("{}/CT/{}".format(envpath, path))
checkarr = np.concatenate([x[0] for x in array])
prediction = model.predict(checkarr, batch_size=1)
diagnose = []

for i in range(len(prediction)):
    try:
        p = prediction[i]
        if p[1] > 0.5:
            # abnormal
            imgWithBone, imgWithoutBone, boneOnly = transferImg(array[i], axis, IMGSIZE)

            line = Line(axis.degree, axis.pivot)
            line.changeK( - line.degree)
            start, end = findStartEnd(imgWithBone, line, IMGSIZE)
        
            stage, tissue, data, pdata = identifyStructure(line, imgWithoutBone, imgWithBone, start, end, i, len(prediction), IMGSIZE)
            checkData(stage, data, pdata, diagnose, imgWithoutBone)
    except Exception as e:
        pass

if len(diagnose) > 0:
    for i in diagnose:
        print(i)
else:
    print("未发现异常")