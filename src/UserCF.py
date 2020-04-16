import pandas as pd
import math as math
import json
import os 

class UserCF:
    def __init__(self,train_rating_path,movie_path,user_file_path):
        self.train_rating = pd.read_csv(train_rating_path)
        self.movie = pd.read_table(
            movie_path,
            header = None,
            sep = "::",
            names = ["movieID","Title","Genres"]
        )
        self.users = pd.read_table(
            user_file_path,
            header = None,
            sep = "::",
            names = ["userId","gender","age","Occupation","zip-code"]
        )["userId"].tolist()
    def UserSimilarity(self):
        if os.path.exists("user_sim.json"):
            print("用户相似度从文件中加载")
            W = json.load(open("user_sim.json","r"))
        else:
        # 建立电影-用户倒序表
            t = self.train_rating
            item_users = dict()
            for movie_index, movie_row in self.movie.iterrows():
                print(movie_row["movieID"])
                item_users[movie_row["movieID"]] = set()
                for index,row in t.loc[t["movieID"] == movie_row["movieID"]].iterrows():                   
                    item_users[movie_row["movieID"]].add(row["userId"])
                
            
        
    
            C = dict()
            N = dict()
            for i, users in item_users.items():
                for user in users:
                    N.setdefault(user,0)

                    N[user] += 1
                    C.setdefault(user,{})
                    for v_user in users:
                        C[user].setdefault(v_user,0)
                        if v_user==user:
                            continue
                        C[user][v_user] += 1                     
                    
            # 用户相似
            W = dict()
       
            for u,related_users in C.items():
                W.setdefault(str(u),{})
                for v,cuv in related_users.items():

                    if u == v:
                        continue
                    W[str(u)].setdefault(str(v),0.0)
                    W[str(u)][str(v)] = cuv/math.sqrt(N[u] * N[v])
            json.dump(W, open('user_sim.json', 'w'))
            

        return W

# 推荐top-k个电影
    def recommendTopK(self,userId,sim_user,nitems):
        rank = dict()
        w = self.UserSimilarity()
        movies = self.movie["movieID"].tolist()
        had_score = self.train_rating[self.train_rating["userId"] == userId]["movieID"].tolist()
        for v, vuw in sorted(w[str(userId)].items(), key=lambda item: item[1], reverse=True)[0:sim_user]:
            for index , row in self.train_rating[self.train_rating["userId"] == int(v)].iterrows():
                if row["movieID"] in had_score:
                    continue
                rank.setdefault(row["movieID"], 0.0)
                rank[row["movieID"]] += row["rate"] * vuw
        #
        # for movieId in movies[0:nitems]:
        #     if movieId in had_score:
        #         continue
        #     rank.setdefault(movieId,0.0)
        #     for v,vuw in sorted(w[str(userId)].items(),key=lambda item:item[1],reverse=True)[:sim_user]:
        #         if userId != vuw:
        #             rank[movieId] += self.train_rating.loc[(self.train_rating.userId ==vuw)& (self.train_rating.movieID == movieId)]["rate"]* vuw
        return dict(sorted(rank.items(),key=lambda x: x[1],reverse=True)[0:nitems])

userCF = UserCF("train.csv","movies.dat","users.dat")
print(userCF.recommendTopK(8,20,50))
               




                



