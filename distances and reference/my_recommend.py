# -*- coding: UTF-8 -*-

import codecs 
from math import sqrt
import random


class myRecommender:
    def __init__(self, k=1, metric='pearson', n=5):
        """ 初始化推荐模块
        data   训练数据
        k      K邻近算法中的值
        metric 使用何种距离计算方式
        n      推荐结果的数量
        """
        self.k = k
        self.n = n
        self.data = {}
        self.users = []
        # 将距离计算方式保存下来
        self.fn = self.manhattan
        # if metric == 'pearson':
        #     self.fn = self.pearson
        if metric == 'cos':
            self.fn = self.cosAngle
    def manhattan(self, rating1, rating2):
        distance = 0
        for key in rating1:
            if key in rating2:
                distance += abs(rating2[key] - rating1[key])
        return distance

    def cosAngle(self, rating1, rating2):
        sum_xy = 0
        sum_x2 = 0
        sum_y2 = 0
        avg_x = sum(map(lambda x: rating1[x], rating1.keys())) / len(rating1.keys())
        avg_y = sum(map(lambda x: rating2[x], rating2.keys())) / len(rating2.keys())
        
        for key in rating1:
            if key in rating2:
                x = rating1[key] - avg_x
                y = rating2[key] - avg_y
                sum_x2 += pow(x, 2)
                sum_y2 += pow(y, 2)
                sum_xy += x * y
        if sum_x2 == 0 or sum_y2 == 0:
            return 0
        denominator = sqrt(sum_x2) * sqrt(sum_y2)
        return sum_xy / denominator

    def computeNearestNeighbor(self, username):
        # """获取邻近用户"""
        distances = []
        for instance in self.data:
            if instance != username:
                distance = self.fn(self.data[username],
                                   self.data[instance])
                distances.append((instance, distance))
        # 按距离排序，距离近的排在前面
        
        distances.sort(key=lambda user: user[1])
        return distances

    def loadDb(self, path = ''):
        f = codecs.open(path + "Movie_Ratings.csv", 'r', 'utf8')
        for lineNum,line in enumerate(f):
            fields = line.split(',')
            if lineNum == 0:
                self.users = map(lambda x: x.strip().strip('"'), filter(lambda x: x.strip().strip('"'), fields))
                continue
            bookname = ''
            for index,field in enumerate(fields):
            	if index == 0:
            		bookname = field.strip('"')
            		continue
            	username = self.users[index - 1]
            	if username in self.data:
                	currentRatings = self.data[username]
                else:
                	currentRatings = {}
                print field
            	currentRatings[bookname] = int(field.strip()) if field.strip() else 0
            	self.data[username] = currentRatings
        f.close()

if __name__ == '__main__':  
    r = myRecommender(1, 'cos')
    r.loadDb()
    length = len(r.users)
    index = random.randint(1, length)
    user = r.users[index]
    print (user)
    print (r.computeNearestNeighbor(user))