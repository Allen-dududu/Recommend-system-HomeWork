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
    def __init__(self,directory_path,seed,trainRate):
        self.user_file_path = directory_path+"/users.dat"
        self.ratings_file_path = directory_path+"/ratings.dat"

        self.seed = seed
        self.trainRate = trainRate
    def spilt_train_test(self):
        
        user_train = pd.read_table(
            self.user_file_path,
            header = None,
            sep = "::",
            names = ["userId","gender","age","Occupation","zip-code"]
        )
        user_train_data = user_train.sample(frac=0.8)
        ratings_train = pd.read_table(
            self.ratings_file_path,
            header = None,
            sep = "::",
            names = ["userId","movieID","rate","timestamp"]
        )
        

        ratings_train_data = ratings_train[ratings_train["userId"].isin(user_train_data["userId"].tolist())]
        return user_train_data,ratings_train_data


        
test = FirstRec(r"C:\Users\liu xinyu\Desktop\CODE",2,2)
test.spilt_train_test()  
