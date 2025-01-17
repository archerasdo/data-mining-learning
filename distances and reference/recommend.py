# -*- coding: UTF-8 -*-

import codecs 
from math import sqrt
import random

class recommender:

    def __init__(self, data, k=1, metric='pearson', n=5):
        # """ 初始化推荐模块
        # data   训练数据
        # k      K邻近算法中的值
        # metric 使用何种距离计算方式
        # n      推荐结果的数量
        # """
        self.k = k
        self.n = n
        self.username2id = {}
        self.userid2name = {}
        self.productid2name = {}
        # 将距离计算方式保存下来
        self.fn = self.manhattan
        if metric == 'pearson':
            self.fn = self.pearson
        elif metric == 'cos':
            self.fn = self.cosAngle
        #
        # 如果data是一个字典类型，则保存下来，否则忽略
        #
        if type(data).__name__ == 'dict':
            self.data = data

    def convertProductID2name(self, id):
        """通过产品ID获取名称"""
        if id in self.productid2name:
            return self.productid2name[id]
        else:
            return id

    def userRatings(self, id, n):
        # """返回该用户评分最高的物品"""
        print ("Ratings for " + self.userid2name[id])
        ratings = self.data[id]
        print(len(ratings))
        ratings = list(ratings.items())
        ratings = [(self.convertProductID2name(k), v)
                   for (k, v) in ratings]
        # 排序并返回结果
        ratings.sort(key=lambda artistTuple: artistTuple[1],
                     reverse = True)
        ratings = ratings[:n]
        for rating in ratings:
            print("%s\t%i" % (rating[0], rating[1]))

    def loadBookDB(self, path=''):
        # """加载BX数据集，path是数据文件位置"""
        self.data = {}
        i = 0
        #
        # 将书籍评分数据放入self.data
        #
        f = codecs.open(path + "BX-Book-Ratings.csv", 'r', 'utf8')
        for line in f:
            i += 1
            #separate line into fields
            fields = line.split(';')
            user = fields[0].strip('"')
            book = fields[1].strip('"')
            rating = int(fields[2].strip().strip('"'))
            if user in self.data:
                currentRatings = self.data[user]
            else:
                currentRatings = {}
            currentRatings[book] = rating
            self.data[user] = currentRatings
        f.close()
        #
        # 将书籍信息存入self.productid2name
        # 包括isbn号、书名、作者等
        #
        f = codecs.open(path + "BX-Books.csv", 'r', 'utf8')
        for line in f:
            i += 1
            #separate line into fields
            fields = line.split(';')
            isbn = fields[0].strip('"')
            title = fields[1].strip('"')
            author = fields[2].strip().strip('"')
            title = title + ' by ' + author
            self.productid2name[isbn] = title
        f.close()
        #
        #  将用户信息存入self.userid2name和self.username2id
        #
        f = codecs.open(path + "BX-Users.csv", 'r', 'utf8')
        for line in f:
            i += 1
            #print(line)
            #separate line into fields
            fields = line.split(';')
            userid = fields[0].strip('"')
            location = fields[1].strip('"')
            if len(fields) > 3:
                age = fields[2].strip().strip('"')
            else:
                age = 'NULL'
            if age != 'NULL':
                value = location + '  (age: ' + age + ')'
            else:
                value = location
            self.userid2name[userid] = value
            self.username2id[location] = userid
        f.close()
        print(i)

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
        print (denominator, sum_xy, sum_x2, sum_y2, sqrt(sum_x2), sqrt(sum_y2), sum_xy / denominator)
        return sum_xy / denominator


    def pearson(self, rating1, rating2):
        sum_xy = 0
        sum_x = 0
        sum_y = 0
        sum_x2 = 0
        sum_y2 = 0
        n = 0
        for key in rating1:
            if key in rating2:
                n += 1
                x = rating1[key]
                y = rating2[key]
                sum_xy += x * y
                sum_x += x
                sum_y += y
                sum_x2 += pow(x, 2)
                sum_y2 += pow(y, 2)
        if n == 0:
            return 0
        # 计算分母
        denominator = (sqrt(sum_x2 - pow(sum_x, 2) / n)
                       * sqrt(sum_y2 - pow(sum_y, 2) / n))
        if denominator == 0:
            return 0
        else:
            return float((sum_xy - (sum_x * sum_y) / n) / denominator)

    def computeNearestNeighbor(self, username):
        # """获取邻近用户"""
        distances = []
        for instance in self.data:
            if instance != username:
                distance = self.fn(self.data[username],
                                   self.data[instance])
                distances.append((instance, distance))
        # 按距离排序，距离近的排在前面
        
        distances.sort(key=lambda artistTuple: artistTuple[1],
                       reverse=True)
        return distances

    def recommend(self, user):
       # """返回推荐列表"""
       recommendations = {}
       # 首先，获取邻近用户
       nearest = self.computeNearestNeighbor(user)
       #
       # 获取用户评价过的商品
       #
       userRatings = self.data[user]
       #
       # 计算总距离
       totalDistance = 0.0
       for i in range(self.k):
          totalDistance += nearest[i][1]
       # 汇总K邻近用户的评分
       for i in range(self.k):
          # 计算饼图的每个分片
          weight = nearest[i][1] / totalDistance
          # 获取用户名称
          name = nearest[i][0]
          # 获取用户评分
          neighborRatings = self.data[name]
          # 获得没有评价过的商品
          for artist in neighborRatings:
             if not artist in userRatings:
                if artist not in recommendations:
                   recommendations[artist] = (neighborRatings[artist]
                                              * weight)
                else:
                   recommendations[artist] = (recommendations[artist]
                                              + neighborRatings[artist]
                                              * weight)
       # 开始推荐
       recommendations = list(recommendations.items())
       recommendations = [(self.convertProductID2name(k), v)
                          for (k, v) in recommendations]
       # 排序并返回
       recommendations.sort(key=lambda artistTuple: artistTuple[1],
                            reverse = True)
       # 返回前n个结果
       return recommendations[:self.n]


if __name__ == '__main__':  
    r = recommender('', 1, 'cos')
    r.loadBookDB()
    keys = r.data.keys()
    length = len(keys)
    index = random.randint(1, length)

    nb = r.computeNearestNeighbor(keys[index])
    print (filter(lambda x: x[1] != 0, nb))
    print ('random seed', index, keys[index], r.data[keys[index]])
