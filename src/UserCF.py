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
        self.w = self.UserSimilarity()
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


    """推荐top-k个电影
    """    
    def recommendTopK(self,userId,sim_user,nitems):
        rank = dict()
        movies = self.movie["movieID"].tolist()
        had_score = self.train_rating[self.train_rating["userId"] == userId]["movieID"].tolist()
        for v, vuw in sorted(self.w[str(userId)].items(), key=lambda item: item[1], reverse=True)[0:sim_user]:
            for index , row in self.train_rating[self.train_rating["userId"] == int(v)].iterrows():
                if row["movieID"] in had_score:
                    continue
                rank.setdefault(row["movieID"], 0.0)
                rank[row["movieID"]] += row["rate"] * vuw
        return dict(sorted(rank.items(),key=lambda x: x[1],reverse=True)[0:nitems])
    """预测评分
    """    
    def preUserItemScore(self,userA,item,sumUserCount):
        score = 0.0
        item_id = str(int(item))
        sds =self.w[str(userA)].items()
        sum_users = sorted(sds, key=lambda x: x[1], reverse=True)[0:sumUserCount]
        # 被计算的相似用户的相似总和
        sum_users_sum = 0.0
        #被计算的相似用户的相似度 与 相应评分的乘积之和
        sum_users_score_sum = 0.0
        for sum_userId in sum_users:
            sum_user_rating = self.train_rating.loc[(self.train_rating["userId"] ==int(sum_userId[0]))&(self.train_rating["movieID"] == int(item)) ]
            if(sum_user_rating.empty):
                continue
            else:
                sum_users_sum += sum_userId[1]
                sum_users_score_sum += sum_userId[1]*sum_user_rating.iloc[0][3]

        score = sum_users_score_sum / sum_users_sum
        return score

userCF = UserCF("train.csv","movies.dat","users.dat")
test_rating = pd.read_csv('test.csv')
userIds = pd.read_table(
            'users.dat',
            header = None,
            sep = "::",
            names = ["userId","gender","age","Occupation","zip-code"]
        )["userId"].tolist()
mse = 0
for userid in userIds:
    # rate_count = test_rating[test_rating["userId"] == userid][""].str.len()
    test_items = test_rating[test_rating["userId"] == userid]
    for index , row in test_items.iterrows():
        score = userCF.preUserItemScore(userid,row["movieID"],400)
        mse +=math.pow(score-row["rate"],2)
        print("用户："+str(userid)+"--电影："+str(row["movieID"])+"-- 预测评分"+str(score)+"---真实评分"+str(row["rate"]))

MSE = mse/len(userIds)
print(MSE)


               




                



