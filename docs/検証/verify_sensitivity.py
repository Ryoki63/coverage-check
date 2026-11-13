from fractions import Fraction as Fr
import random
ROC=[Fr(25,48),Fr(13,48),Fr(7,48),Fr(3,48)]
RS=[Fr(4,10),Fr(3,10),Fr(2,10),Fr(1,10)]
EQ=[Fr(1,4)]*4
def N(t): return Fr(t[1]+t[2],2)
def sc(w,t): return w[0]*t[0]+w[1]*N(t)+w[2]*t[3]+w[3]*t[4]
def hur(t): return t[0]>=3 and N(t)>=3 and t[3]>=3
rows=[('H 測定前',(3,3,1,4,3)),('H-lite 上限',(3,3,3,3,4)),("C' V=3",(3,3,2,4,4)),('A 厳格',(3,3,1,5,5)),("C' V=3,n2=3",(3,3,3,4,4)),('A n2=2',(3,3,2,5,5)),('H V=3',(3,4,4,4,3)),('A',(3,3,3,5,5)),("C' V=4",(4,3,2,4,4)),("C' V=4,n2=3",(4,3,3,4,4)),('H R=3',(4,4,4,3,3)),('H F=2',(4,4,4,4,2)),('H',(4,4,4,4,3)),('A V=4',(4,3,3,5,5))]
for name,t in rows:
    print(name,t,'N=%.1f'%float(N(t)),'○' if hur(t) else '×','%.4f %.4f %.4f'%(float(sc(ROC,t)),float(sc(RS,t)),float(sc(EQ,t))))
print('--- 公表基準 ROC ソート順の確認 ---')
print([r[0] for r in sorted(rows,key=lambda r:float(sc(ROC,r[1])))])
print('--- 厳密解 ---')
print('A勝ち 3/175 =',3/175,' H勝ち 172/175 =',172/175)
try:
    import numpy as np
    rng=np.random.default_rng(20261103)
    tot=0;aw=0
    for _ in range(10):
        e=rng.exponential(size=(2_000_000,4))
        w=-np.sort(-e,axis=1); w=w/w.sum(axis=1,keepdims=True)
        d=w[:,0]+w[:,1]-w[:,2]-2*w[:,3]
        aw+=int((d<0).sum()); tot+=len(d)
    print('numpy 20M回 A勝ち',aw/tot,' H勝ち',1-aw/tot)
    # Renyi 表現の検算
    rng=np.random.default_rng(1)
    E=rng.exponential(size=(5_000_000,4))
    cond=E[:,0]>(4/3)*E[:,1]+4*E[:,2]+4*E[:,3]
    print('Renyi 条件 5M回',cond.mean())
except Exception as ex:
    print('numpy 不可',ex)
