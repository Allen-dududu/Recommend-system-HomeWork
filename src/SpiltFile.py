# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import json
import random
import math
import pandas as pd
class FirstRec:
    def __init__(self,directory_path,seed,K,M):
        self.user_file_path = directory_path+"/users.dat"
        self.ratings_file_path = directory_path+"/ratings.dat"
        # 随机种子
        self.seed = seed
        # 总共多少份
        self.M = M
        # 测试集是第几分
        self.K = K
    def spilt_train_test(self):
        random.seed = self.seed
        users = pd.read_table(
            self.user_file_path,
            header = None,
            sep = "::",
            names = ["userId","gender","age","Occupation","zip-code"]
        )
        
        ratings = pd.read_table(
            self.ratings_file_path,
            header = None,
            sep = "::",
            names = ["userId","movieID","rate","timestamp"]
        )

        ratings_test = pd.DataFrame()
        ratings_train = pd.DataFrame([],columns=["userId","movieID","rate","timestamp"])
        print(ratings.head())
        i = 0
        for user_index, user_row in users.iterrows():
            print(user_index)
            for rating_index,rating_row in ratings.loc[ratings["userId"] == user_row["userId"]].iterrows():
                if random.randint(0,self.M) == self.K:
                    ratings_test = ratings_test.append(rating_row,ignore_index=True)
                else:
                    ratings_train = ratings_train.append(rating_row,ignore_index=True)
            

        
        ratings_test.to_csv("test.csv")
        ratings_train.to_csv("train.csv")
        print(ratings_test.head())



        
test = FirstRec(r"C:\Users\liu xinyu\Desktop\CODE",2,1,5)
test.spilt_train_test()  
