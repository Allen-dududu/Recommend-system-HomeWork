import pandas as pd
import math as math
import json
import os


class ItemCF:
    def __init__(self, train_rating_path, movie_path, user_file_path):
        self.train_rating = pd.read_csv(train_rating_path)
        self.movie = pd.read_table(
            movie_path,
            header=None,
            sep="::",
            names=["movieID", "Title", "Genres"]
        )
        self.users = pd.read_table(
            user_file_path,
            header=None,
            sep="::",
            names=["userId", "gender", "age", "Occupation", "zip-code"]
        )["userId"].tolist()
        self.itemSum = self.ItemSimilarity()

    def ItemSimilarity(self):
        if os.path.exists("item_sim.json"):
            print("物品相似度从文件中加载")
            itemSim = json.load(open("item_sim.json", "r"))
        else:
            # 建立用户-物品倒序表
            t = self.train_rating
            user_item = dict()
            for user in self.users:
                print(user)
                user_item[user] = set()
                for index, row in t.loc[t["userId"] == user].iterrows():
                    user_item[user].add(row["movieID"])
            # 同现矩阵
            count = dict()
            # 得到每个物品有多少用户产生行为
            item_user_count = dict()
            for i, items in user_item.items():
                for item in items:
                    item_user_count.setdefault(item, 0)

                    item_user_count[item] += 1
                    count.setdefault(item, {})
                    for v_item in items:
                        count[item].setdefault(v_item, 0)
                        if v_item == item:
                            continue
                        count[item][v_item] += 1

            # 物品相似相似
            itemSim = dict()

            for u, related_items in count.items():
                itemSim.setdefault(str(u), {})
                for v, cuv in related_items.items():

                    if u == v:
                        continue
                    itemSim[str(u)].setdefault(str(v), 0.0)
                    itemSim[str(u)][str(v)] = cuv / math.sqrt(item_user_count[u] * item_user_count[v])
            json.dump(itemSim, open('item_sim.json', 'w'))

        return itemSim

    # 推荐top-k个电影
    # neighbor_item :neighbor_item个临近物品
    # nitems：总返回n个物品
    def recommendTopK(self, userId, neighbor_item, nitems):
        rank = dict()

        had_score = self.train_rating[self.train_rating["userId"] == userId]
        for index,row in had_score.iterrows():
            for j,wj in sorted(self.itemSum[str(row["movieID"])].items(),key = lambda x:x[1], reverse = True)[0:neighbor_item]:
                if int(j) in had_score["movieID"]:
                    continue
                rank.setdefault(j,0)
                rank[j] += row["rate"] * wj
        return dict(sorted(rank.items(), key=lambda x: x[1], reverse=True)[0:nitems])

    """预测用户对物品的评分
    userA : 用户
    item ： 被预测电影ID
    k_end：
    """    
    def preUserItemScore(self,userA,item,k_end):
        score = 0.0
        sd = str(int(item))
        sds =self.itemSum[sd].items()
        item_sum = sorted(sds, key=lambda x: x[1], reverse=True)

        # 被计算的相似物品的相似总和
        sum_item_sum = 0.0
        #被计算的相似物品的相似度 与 相应评分的乘积之和
        sum_item_score_sum = 0.0

        # 这个用户之前评过分的电影与item的相似度，和它的评分
        d = dict()
        for index,row in self.train_rating[self.train_rating["userId"] == userA].iterrows():
            d.setdefault(row["movieID"],{})
            d[row["movieID"]].setdefault("相似度", 0)
            d[row["movieID"]].setdefault("评分", 0)
            # item_sum[0]
            s = list(filter(lambda x: x[0] ==str(row["movieID"] ),item_sum))
            if len(s)!=0:
                d[row["movieID"]]["相似度"] = s[0][1]
                d[row["movieID"]]["评分"] = row["rate"]
        # 按相似度取前k_end 个
        dr = sorted(d.items(), key=lambda x: x[1]["相似度"], reverse=True)[0:k_end]
        for key , value in dr:
            sum_item_sum += value["相似度"]
            sum_item_score_sum +=value["相似度"]*value["评分"]
        score = sum_item_score_sum/sum_item_sum
        return score


itemCF = ItemCF("train.csv", "movies.dat", "users.dat")
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
        score = itemCF.preUserItemScore(userid,row["movieID"],5)
        mse +=math.pow(score-row["rate"],2)
        print("用户："+str(userid)+"--电影："+str(row["movieID"])+"-- 预测评分"+str(score)+"---真实评分"+str(row["rate"]))

MSE = mse/len(userIds)
print(MSE)









