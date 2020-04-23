import matplotlib.pyplot as plt
from math import pow
import numpy
import pandas as pd
import pickle

def matrix_factorization(R,P,Q,K,steps=5000,alpha=0.0002,beta=0.02):
    Q=Q.T  # .T操作表示矩阵的转置
    result=[]
    for step in range(steps):
        for i in range(len(R)):
            for j in range(len(R[i])):
                if R[i][j]>0:
                    eij=R[i][j]-numpy.dot(P[i,:],Q[:,j]) # .dot(P,Q) 表示矩阵内积
                    for k in range(K):
                        P[i][k]=P[i][k]+alpha*(2*eij*Q[k][j]-beta*P[i][k])
                        Q[k][j]=Q[k][j]+alpha*(2*eij*P[i][k]-beta*Q[k][j])
        eR=numpy.dot(P,Q)
        e=0
        for i in range(len(R)):
            for j in range(len(R[i])):
                if R[i][j]>0:
                    e=e+pow(R[i][j]-numpy.dot(P[i,:],Q[:,j]),2)
                    for k in range(K):
                        e=e+(beta/2)*(pow(P[i][k],2)+pow(Q[k][j],2))
        result.append(e)
        if e<0.1:
            break
    return P,Q.T,result

if __name__ == '__main__':

    csv = pd.read_csv("train.csv")
    users = pd.read_table(
        "users.dat",
        header=None,
        sep="::",
        names=["userId", "gender", "age", "Occupation", "zip-code"]
    )["userId"].tolist()
    items = pd.read_table(
        "movies.dat",
        header=None,
        sep="::",
        names=["movieID", "Title", "Genres"]
    )["movieID"].tolist()
    R = numpy.zeros([max(users)+1, max(items)+1], dtype=float, order='C')
    print(R.shape)
    for user in users:
        for item in items:
            # print(csv[(csv.userId == user) & (csv.movieID == item)]["rate"])
            if(csv[(csv.userId == user) & (csv.movieID == item)].empty):
                continue
            R[user][item] = 1

    N = len(R)
    M = len(R[0])
    K = 2

    P = numpy.random.rand(N, K)  # 随机生成一个 N行 K列的矩阵
    Q = numpy.random.rand(M, K)  # 随机生成一个 M行 K列的矩阵

    nP, nQ, result = matrix_factorization(R, P, Q, K)
    print("原始的评分矩阵R为：\n", R)
    R_MF = numpy.dot(nP, nQ.T)
    f = open('lfm.model','wb')
    pickle.dump(R_MF,f)

    # print("经过MF算法填充0处评分值后的评分矩阵R_MF为：\n", R_MF)

    #-------------损失函数的收敛曲线图---------------

    n = len(result)
    x = range(n)
    # plt.plot(x, result, color='r', linewidth=3)
    # plt.title("Convergence curve")
    # plt.xlabel("generation")
    # plt.ylabel("loss")
    # plt.show()
