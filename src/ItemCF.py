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

    def ItemSimilarity(self):
        if os.path.exists("item_sim.json"):
            print("物品相似度从文件中加载")
            W = json.load(open("item_sim.json", "r"))
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
        itemSimilarity = self.ItemSimilarity()

        had_score = self.train_rating[self.train_rating["userId"] == userId]
        for index,row in had_score.iterrows():
            for j,wj in sorted(itemSimilarity[str(row["movieID"])].items(),key = lambda x:x[1], reverse = True)[0:neighbor_item]:
                if int(j) in had_score["movieID"]:
                    continue
                rank.setdefault(j,0)
                rank[j] += row["rate"] * wj

        #
        #
        #
        # for movieId in movies[0:neighbor_item]:
        #     if movieId in had_score:
        #         continue
        #     rank.setdefault(movieId, 0.0)
        #     for v, vuw in sorted(w[str(userId)].items(), key=lambda item: item[1], reverse=True)[:sim_user]:
        #         if userId != vuw:
        #             rank[movieId] += \
        #             self.train_rating.loc[(self.train_rating.userId == vuw) & (self.train_rating.movieID == movieId)][
        #                 "rate"] * vuw
        return dict(sorted(rank.items(), key=lambda x: x[1], reverse=True)[0:nitems])


itemCF = ItemCF("train.csv", "movies.dat", "users.dat")
print(itemCF.recommendTopK(8, 20, 50))









