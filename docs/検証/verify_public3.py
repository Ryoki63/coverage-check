# 追加計算: 公表3基準（価値・新規性・再利用性）のみを等重みにした場合 と 3時間削減に要る要確認率
S = {"H":(4,4,4,4,3),"A":(3,3,3,5,5),"H-lite":(3,3,3,3,4),"B":(3,3,3,3,3),"D":(3,2,2,3,3),
     "C'":(2,3,2,4,4),"G":(2,2,2,4,4),"F":(3,1,1,3,2),"E":(2,2,1,3,4)}
def N(t): return (t[1]+t[2])/2
rows=[]
for k,t in S.items():
    V,R=t[0],t[3]; n=N(t)
    rows.append((k,(V+n+R)/3))
rows.sort(key=lambda x:-x[1])
print("== 公表3基準のみ等重み(V,N,R) ==")
for k,v in rows: print(k, f"{v:.4f}")
print()
print("== 3時間削減に要る要確認率の上限(P=1) ==")
for p in (100,200,400):
    man=p*3/60
    # man - (6+5*f*p)/60 >= 3  ->  f <= (60*(man-3)-6)/(5*p)
    f=(60*(man-3)-6)/(5*p)
    print("p",p,"man",man,"f<=",round(f,4))
print()
print("== 抜き取り20%を超える要確認率(P=1) ==")
for p in (100,200,400):
    f=(0.2*p*3-6)/(5*p)
    print("p",p,"f<",round(f,4))
