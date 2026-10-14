import json,re
O=[0,21.315813,21.315813+21.341938];SP=1.05
# (chunk, start, end, sentence)
S=[(0,0.0,2.27,"금융사 열여섯 곳이 뚫렸습니다."),
(0,2.67,5.52,"정부가 이번에 처음으로 공식 집계를 냈는데요."),
(0,5.78,12.84,"은행부터 저축은행, 캐피탈, 가상자산 거래소까지, 새어 나간 개인정보가 10만 건에 달합니다."),
(0,13.25,17.43,"이름이랑 연락처는 물론이고, 주민등록번호까지 들어 있었습니다."),
(0,18.0,21.3,"그나마 비밀번호랑 카드번호는 안전하다고 하네요."),
(1,0.0,2.91,"그런데요, 정작 더 놀라운 건 따로 있습니다."),
(1,3.15,7.21,"금융당국이 금융사 555곳을 들여다봤더니,"),
(1,7.42,10.35,"130곳이 기본조차 안 지키고 있었던 거죠."),
(1,10.68,14.89,"보안 업데이트는 미뤄 두고, 오래된 시스템은 그대로 쓰고,"),
(1,15.11,17.62,"24시간 지켜보는 사람도 없었습니다."),
(1,18.40,21.13,"심지어 2단계 인증조차 없는 곳도 있었고요."),
(2,0.0,1.68,"그럼 우리는 뭘 해야 할까요?"),
(2,2.21,3.74,"딱 세 가지만 기억하세요."),
(2,4.34,9.84,"금융사라며 걸려 온 전화나 문자는 일단 끊고, 대표번호로 직접 다시 거는 겁니다."),
(2,10.38,12.68,"명의도용 안심차단도 켜 두시고요."),
(2,13.11,17.9,"마지막으로, 지금 쓰는 금융 앱에 2단계 인증이 켜져 있는지 꼭 확인해 보세요."),
(2,18.0,21.4,"이 영상은 부모님께도 한번 보내 드리세요.")]
def wrap(s,n=14):
    out=[];cur=''
    for w in s.split(' '):
        if len(cur)+len(w)+(1 if cur else 0)>n and cur: out.append(cur);cur=w
        else: cur=(cur+' '+w).strip()
    if cur: out.append(cur)
    return out
caps=[]
for c,a,b,s in S:
    a=(O[c]+a)/SP;b=(O[c]+b)/SP
    parts=[p.strip() for p in re.split(r'(?<=,)\s',s)]
    # merge into caption units of <=2 lines
    units=[];
    for p in parts:
        L=wrap(p)
        for i in range(0,len(L),2): units.append(' '.join(L[i:i+2]) if False else '\n'.join(L[i:i+2]))
    tot=sum(len(u) for u in units);t=a
    for u in units:
        d=(b-a)*len(u)/tot;caps.append({'t0':round(t,2),'t1':round(t+d,2),'text':u});t+=d
json.dump(caps,open('caps.json','w'),ensure_ascii=False,indent=0)
print(len(caps),caps[-1])
for c in caps[:6]:print(c)
