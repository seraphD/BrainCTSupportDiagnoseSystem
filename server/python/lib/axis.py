# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 12:30:01 2019

@author: 张立辉
"""

import matplotlib.pyplot as plt
import math
import numpy as np

class Point:
    x = -1
    y = -1
    
    # 更改点的坐标
    def change(self, x, y):
        self.x = round(x)
        self.y = round(y)
    
    def printPoint(self):
        print((self.x, self.y))
        
    def getXY(self):
        return (self.x, self.y)
    
    # 判断点是否在图片的范围内
    def isInPic(self, IMGSIZE):
        x = self.x
        y = self.y
        
        return x > 0 and x < IMGSIZE and y > 0 and y < IMGSIZE
        
    def isEmpty(self):
        return self.x == -1 and self.y == -1
    
class Line:
    # y = kx + b
    k = None
    b = None
    degree = None
    pivot = None
    
    # 构造函数
    def __init__(self, degree, pivot):
        h = math.radians(degree)
        k = math.tan(h)
        
        b = pivot.y - pivot.x * k
        
        self.k = k
        self.b = b
        self.degree = degree
        self.pivot = pivot
    
    # 调整斜率
    def changeK(self, delta):
        p = self.pivot
        newD = self.degree + delta
        h = math.radians(newD)
        k = math.tan(h)
        b = p.y - p.x * k
        
        self.k = k
        self.degree = newD
        self.b = b
    
    def isEmpty(self):
        return self.k == None and self.b == None
    
    # 判断一个点是否在直线的右边
    def isRight(self, x, y):
        return y - self.k * x - self.b > 0
    
    def isLeft(self, x, y):
        return y - self.k * x - self.b < 0        
        
class ABCLine:
    a = 0
    b = 0
    c = 0
    
    def __init__(self, p1, p2):
        x1, y1 = p1.getXY()
        x2, y2 = p2.getXY()
        
        if x1 != x2 and y1 != y2:
            self.a = 1/(x2 - x1)
            self.b = -1/(y2 - y1)
            self.c = y1/(y2 - y1) - x1/(x2 - x1)
        elif x1 == x2:
            self.a = 1
            self.c = -1 * x1
        else:
            self.b = 1
            self.c = -1 * y2
# 寻找中心点
def findPivot(pic, IMGSIZE):
    top = Point()
    left = Point()
    right = Point()
    bottom = Point()
    pivot = Point()
    
    for i in range(0, int(IMGSIZE / 2)):
        if top.isEmpty():
            for j in range(0, IMGSIZE):
                if pic[i][j] > 0:
                    top.change(i, j)
                    break
        
        if bottom.isEmpty():
            for j in range(0, IMGSIZE):
                if pic[IMGSIZE - i - 1][j] > 0:
                    bottom.change(IMGSIZE - i, j)
                    break
        
        if left.isEmpty():
            for j in range(0, IMGSIZE):
                if pic[j][i] > 0:
                    left.change(j, i)
                    break
        
        if right.isEmpty():
            for j in range(0, IMGSIZE):
                if pic[j][IMGSIZE - i - 1] > 0:
                    right.change(j, IMGSIZE - i)
                    break
        
    pivot.change((top.x + bottom.x) / 2, (left.y + right.y) / 2)
    
    return pivot

def convertK2Degree(k):
    arc = math.atan(k)
    degree = math.degrees(arc)
    return degree

def scanEdge(pic, IMGSIZE):
    new_img = np.zeros((IMGSIZE, IMGSIZE), dtype=np.uint16)
    edge = []
    for i in range(0, IMGSIZE):
        left = 0
        for j in range(0, IMGSIZE):
            if pic[i][j] == 0:
                left = j
            else:
                new_img[i][j] = pic[i][j]
                p = Point()
                p.change(i, j)
                edge.append(p)
                break
        
        right = left
        for j in range(left, IMGSIZE):
            if pic[i][j] > 0:
                right = j
        new_img[i][right] = pic[i][right]
        p = Point()
        p.change(i, j)
        edge.append(p)
    
    return (edge, new_img)

def calcu(point, line):
    # 计算对称点
    p = point.x
    q = point.y
    
    k = line.k
    b = line.b
    
    x = 0
    y = 0
    if k != 0:
        y = (2*p - q/k + 2*b/k + k*q)/(1/k + k)
        x = -1 * k * (y - q) + p
    else:
        x = p
        y = b - (q - b)
    
    new_p = Point()
    new_p.change(x, y)
    return new_p
    
def match(edge, img, line, IMGSIZE):
    left = []
    right = []
    
    for i in range(0, IMGSIZE):
        for j in range(0, IMGSIZE):
            if img[i][j] > 0:
                temp = Point()
                temp.change(i, j)
                if j - line.k * i - line.b > 0:
                    right.append(temp)
                else:
                    left.append(temp)
    cnt = 0
    matchSet = left if len(left) > len(right) else right
    for i in matchSet:
        new_p = calcu(i, line)
        
        if new_p.isInPic(IMGSIZE) and img[new_p.x][new_p.y] > 0:
            cnt += 1

    diff = abs(len(left) - len(right))/len(matchSet)
    rate = cnt/len(matchSet)
    
    return (diff, rate)
# 绘制对称轴
def drawAxis(lines, pic, IMGSIZE):
    temp = pic.copy()
    for i in range(0, IMGSIZE):
        for line in lines:
            j = round(line.k * i + line.b)
        
            if j > 0 and j < IMGSIZE:
                temp[i][j] = 300
    
    plt.imshow(temp)
    plt.show()
    return temp
    
def findStartEnd(pic, axis, IMGSIZE):
    flag = False
    start = Point()
    end = Point()
    for i in range(0, IMGSIZE):
        j = round(axis.k * i + axis.b)
        
        if pic[i][j] > 0:
            end.change(i, j)
            
            if not flag:
                start.change(i, j)
                flag = True
    return (start, end)

# 暴力搜索
def findAxis(pic, IMGSIZE):
    rate_result = 0
    index = -1
    
    pivot = findPivot(pic, IMGSIZE)
    edge, new_image = scanEdge(pic, IMGSIZE)
    r = range(-35, 35)
        
    for i in r:
        line = Line(i, pivot)
        diff, rate= match(edge, pic, line, IMGSIZE)

        if rate > rate_result:
            rate_result = rate
            index = i
#    drawAxis(Line(index, pivot), pic, IMGSIZE)
    axis = Line(index, pivot)
    return axis