from auction import Auction
from naver import Naver
from coupang import Coupang
from database import Database
import pymysql
import re




def goodsSplit(goodsName):
    # 괄호삭제 (1개 혹은 2개의 경우)
    cnt = goodsName.count('(')
    if cnt == 2:
        goodsName = goodsName.replace('(','',1)
        goodsName = goodsName.replace(')','',1)
        s = goodsName.find('(')
        e = goodsName.find(')')
        str = goodsName[s:e+1]
        goodsName = goodsName.replace(str,'')

    elif cnt == 1:
        s = goodsName.find('(')
        e = goodsName.find(')')
        goodsName = goodsName.replace(goodsName[s:e+1],'')

    try:
        p = re.compile('[a-z]\s?[0-9]{4,5}\s?',re.I)
        res = p.findall(goodsName)
        i = len(res) - 1
        goodsCode = res[i]
        
        pos = goodsName.find(goodsCode) + len(goodsCode)
        dif = len(goodsName) - pos
        print(dif)

        if i == 0 and dif > 5:
            goodsCode = ''
        #코드 분리후 남은 하이픈과 공백제거
        goodsName = goodsName.replace(goodsCode,'').strip().strip('-').strip()     
        goodsCode = goodsCode.strip().replace(' ','')
        data = {'goodsName':goodsName, 'goodsCode':goodsCode}
    except:
        data = {'goodsName':goodsName, 'goodsCode':''}
    
    return data


goodsName = 'OMRON MY4678N AC220V 14V-핀 릴레이- G 25854( 묶음)'
# goodsName = 'OMRON MY467863 G42릴레이'
res = goodsSplit(goodsName)
print(res['goodsName'])
print(res['goodsCode'])

quit()





goodsName = 'OMRON MY4678N (AC220V 14V-핀 릴레이- G 25854(세트상품)'
cnt = goodsName.count('(')
print(cnt)

p = re.compile(r'\(|\)')
m = p.search(goodsName)
str = goodsName[m.regs[0][0]:m.endpos]
goodsName = goodsName.replace(str,'')

p = re.compile('[a-z]\s?[0-9]{4,5}\s?',re.I)
res = p.findall(goodsName)
i = len(res) - 1
goodsCode = res[i]
#코드 분리후 남은 하이픈과 공백제거
goodsName = goodsName.replace(goodsCode,'').strip().strip('-').strip() 
quit()






# ac = Auction()
# res = ac.getMainStatus()
# # print(res)


# res=ac.getOrder('신규주문')
# for i in res['data']:
#     print(i)
#     print('\n')


# cp = Coupang()
# res = cp.getOrder("","","ACCEPT")
# print(res)
# quit()


na = Naver()
res = na.getStatus()
print(res)