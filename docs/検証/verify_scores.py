import random, itertools
from fractions import Fraction as Fr
from collections import Counter

ROC=[Fr(25,48),Fr(13,48),Fr(7,48),Fr(3,48)]
RS=[Fr(4,10),Fr(3,10),Fr(2,10),Fr(1,10)]
EQ=[Fr(1,4)]*4
S={
 'H':(4,4,4,4,3),'A':(3,3,3,5,5),'H-lite':(3,3,3,3,4),'B':(3,3,3,3,3),
 'D':(3,2,2,3,3),"C'":(2,3,2,4,4),'G':(2,2,2,4,4),'F':(3,1,1,3,2),'E':(2,2,1,3,4)}
def N(t): return Fr(t[1]+t[2],2)
def sc(w,t):
    V,n1,n2,R,F=t
    return w[0]*V+w[1]*N(t)+w[2]*R+w[3]*F
def hur(t): return t[0]>=3 and N(t)>=3 and t[3]>=3
f=lambda x: '%.4f'%float(x)
print('== 9案 ==')
for k,t in S.items():
    print(k,t,'N=',float(N(t)),'hurdle',hur(t),'ROC',f(sc(ROC,t)),'RS',f(sc(RS,t)),'EQ',f(sc(EQ,t)))
for nm,w in (('ROC',ROC),('RS',RS),('EQ',EQ)):
    r=sorted(S,key=lambda k:-sc(w,S[k])); print(nm,'順位',r)
print('ROC weights',[float(x) for x in ROC],'sum',sum(ROC))

print('\n== H-A 式と極端な4方向 ==')
for r in [(1,0,0,0),(1,1,0,0),(1,1,1,0),(1,1,1,1)]:
    s=sum(r); w=[Fr(x,s) for x in r]
    print(r,'H-A=',f(sc(w,S['H'])-sc(w,S['A'])),'(式:',f(w[0]+w[1]-w[2]-2*w[3]),')')

print('\n== 感度 ==')
def var(b,**kw):
    V,n1,n2,R,F=S[b]; d=dict(V=V,n1=n1,n2=n2,R=R,F=F); d.update(kw); return (d['V'],d['n1'],d['n2'],d['R'],d['F'])
cases={
 'A V=4':var('A',V=4),
 "C' V=3":var("C'",V=3),
 "C' V=4":var("C'",V=4),
 "C' V=4,n2=3":var("C'",V=4,n2=3),
 "C' V=3,n2=3":var("C'",V=3,n2=3),
 'H F=2':var('H',F=2),
 'H R=3':var('H',R=3),
 'H V=3':var('H',V=3),
}
for k,t in cases.items():
    print(k,t,'N',float(N(t)),'hurdle',hur(t),'ROC',f(sc(ROC,t)),'RS',f(sc(RS,t)),'EQ',f(sc(EQ,t)),
          '| vsA ROC',f(sc(ROC,t)-sc(ROC,S['A'])),'RS',f(sc(RS,t)-sc(RS,S['A'])),'EQ',f(sc(EQ,t)-sc(EQ,S['A'])),
          '| vsH ROC',f(sc(ROC,t)-sc(ROC,S['H'])),'RS',f(sc(RS,t)-sc(RS,S['H'])),'EQ',f(sc(EQ,t)-sc(EQ,S['H'])))

print('\n== 乱数（優先順位つき重み） ==')
random.seed(20261103)
n=200000; wins=0; ranks=[]
for _ in range(n):
    x=sorted([random.expovariate(1) for _ in range(4)],reverse=True); s=sum(x); w=[v/s for v in x]
    scs={k:float(w[0]*t[0]+w[1]*(t[1]+t[2])/2+w[2]*t[3]+w[3]*t[4]) for k,t in S.items()}
    if scs['H']>scs['A']: wins+=1
    ranks.append(sorted(scs,key=lambda k:-scs[k]).index("C'")+1)
print('H>A',wins/n); print("C' 順位",{k:round(v/n,4) for k,v in sorted(Counter(ranks).items())})

print('\n== 16通りの切替表 ==')
rows=[]
for k in range(4):
    for k3 in (True,False):
        for k4 in (True,False):
            V=4 if k3 else 3; n1=4 if k4 else 3; n2=1+k
            t=(V,n1,n2,4,3); a=S['A']
            h=hur(t); roc=sc(ROC,t); rs=sc(RS,t); eq=sc(EQ,t)
            aroc=sc(ROC,a); ars=sc(RS,a)
            win = h and roc>aroc and rs>ars
            note = '' if not h else ('ROC>A' if roc>aroc else ('ROC=A' if roc==aroc else 'ROC<A'))+'/'+('RS>A' if rs>ars else ('RS=A' if rs==ars else 'RS<A'))
            rows.append((k,k3,k4,t,float(N(t)),h,f(roc),f(rs),f(eq),note,'H継続' if win else 'Aへ'))
for r in rows: print(r)
print('H継続:',sum(1 for r in rows if r[-1]=='H継続'),'/16')

print('\n== 工数 ==')
def man(p): return p*3/60
def auto(p,fr,P=1): return (6*P+5*fr*p)/60
for p in (100,200,400):
    for fr in (0.10,0.15,0.30):
        print('p',p,'f',fr,'手',man(p),'H',round(auto(p,fr),2),'削減h',round(man(p)-auto(p,fr),2),'削減%',round((1-auto(p,fr)/man(p))*100,1))
for p in (100,200,400): print('損益分岐f',p,round(0.6-1.2/p,4))
for fr in (0.10,0.15,0.30): print('3h削減に要る組数 f',fr,round(186/(3-5*fr),1))
print('--抜き取り20%--')
for p in (100,200,400):
    base=0.2*p*3/60
    print('p',p,'抜取',round(base,2),'|',[ (fr,round(auto(p,fr)-base,2)) for fr in (0.10,0.15,0.30)],'分岐f',round(0.12-1.2/p,4))
print('--ページ分割（15%）--')
for P in (10,20):
    for p in (200,):
        a=auto(p,0.15,P); print('P',P,'p',p,'H',round(a,2),'削減',round(man(p)-a,2))

print('\n== 工数（2段階の確認: COVERED も人が根拠を見る）==')
# H = (6P + c*p*(1-f) + 5*p*f)/60 。c は COVERED 1件の確認分（既定1分）
def auto2(p,fr,c=1.0,P=1): return (6*P+c*p*(1-fr)+5*fr*p)/60
for c in (1.0,0.5,2.0):
    for p in (100,200,400):
        print('c',c,'p',p,[(fr,'H',round(auto2(p,fr,c),2),'削減h',round(man(p)-auto2(p,fr,c),2),'削減%',round((1-auto2(p,fr,c)/man(p))*100,1)) for fr in (0.10,0.15,0.30)])
for fr in (0.10,0.15,0.30): print('3h削減に要る項目数 c 1 f',fr,round(186/(2-4*fr),1))
for p in (100,200,400): print('3h削減の上限f c 1 p',p,round((2-186/p)/4,4))
for p in (100,200,400): print('20%抜取',round(0.2*p*3/60,2),'f=0 でも H',round(auto2(p,0.0),2),'p',p)
print('P 10 p 200 f 0.15 H',round(auto2(200,0.15,1.0,10),2),'削減',round(man(200)-auto2(200,0.15,1.0,10),2))
print('\n基準確率',{N_:round(3/N_*100,1) for N_ in (20,50,100,200)})
print('台本合計',20+20+40+40+30+20+10)
