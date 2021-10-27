import datetime
# from PIL import Image, ImageDraw, ImageFont
from auction import Auction
from coupang import Coupang
from naver import Naver

import re
import datetime

from database import Database
import calendar
import pymysql
import sys

db = Database()

orderTable = 'orderlist' 
# db.createTable(orderTable)
db.deleteTable(orderTable)

start = f'2021-10-01'
end = f'2021-10-24'
start = ''
end = ''

try:
    dataRange = sys.argv[1]
    print(dataRange)
except:
    dataRange = 'PAY'
    # dataRange = 'ALL'

if dataRange == 'PAY':
    CPmenus = ['ACCEPT','INSTRUCT']
    NAmenus = ['신규주문','배송준비']
    ACmenus = ['입금대기','신규주문','발송예정']
elif dataRange == "ALL":
    CPmenus = ['ACCEPT','INSTRUCT','DEPARTURE','DELIVERING','FINAL_DELIVERY']
    NAmenus = ['신규주문','배송준비','배송중','배송완료']
    ACmenus = ['입금대기','신규주문','발송예정','발송지연','배송중','배송완료','정산예정','정산완료']


## 쿠팡
cp = Coupang()
for menu in CPmenus:
    cpres = cp.getOrder(start,end,menu)
    if len(cpres['data']) > 0:
        print('쿠팡',menu,'데이터입력')
        db.insertOrder('쿠팡',menu,cpres['data'])

## 네이버
na = Naver()
for menu in NAmenus:
    res = na.getOrder(menu)
    if menu == '신규주문' or menu == '배송준비':
        count = len(res['data']['deliveryList']['elements'])
        data = res['data']['deliveryList']['elements']
    if menu == '배송중' or menu == '배송완료':
        count = len(res['data']['deliveryStatusListMp']['elements'])
        data = res['data']['deliveryStatusListMp']['elements']
    
    if count > 0:
        print('네이버',menu,'데이터 입력중')
        db.insertOrder('네이버',menu,data)

## 옥션
ac = Auction()
for menu in ACmenus:
    acres = ac.getOrder(menu)
    count = len(acres['data'])
    if count > 0:
        print('옥션',menu,'데이터 입력중')
        db.insertOrder('옥션',menu,acres['data'])
        


db.orderSummaryPrint('Full')

## 요약인서트
db.getOrderSummary()
quit()

# ## DB처리
# viewMode = ""

# conn = db.connect()
# cur = conn.cursor()



# sql = f'''
# select rcverName, count(*)as cnt, rcverTel1, rcverTel2, zipCode, adress, memo, feeType, sum(orderAmnt)as Amnt, site, goodsNo, feeAmnt from orderlist group
# by rcverName, adress, rcverTel1 order by feeType Desc, No Desc
# '''

# cur = conn.cursor(pymysql.cursors.DictCursor)
# cur.execute(sql)
# rows = cur.fetchall()
# print('\n\n')
# ######### 주문정보 루프
# for row in rows:
#     print("="*60)
#     print(f"수취인: {row['rcverName']}")
    
#     # 전화 1,2가 같으면 1개만 출력
#     if row['rcverTel2'] == '':
#         print(f"휴대폰: {row['rcverTel1']}")
#     else:
#         if row['rcverTel2'] == row['rcverTel1']:
#             print(f"전화: {row['rcverTel1']}")
#         else:
#             print(f"전화: {row['rcverTel1']} 전화2: {row['rcverTel2']}")

#     print(f"우편번호: {row['zipCode']}")
#     print(f"주소: {row['adress']}")
#     if row['memo'] != '':
#         print("배송메모: "+row['memo'])

#     # 택배비추출 / 옥션이면 제품테이블에서 상품배송비를 긁어온다.
#     if row['site'] == '옥션':
#         sql = "select deliveryFee from product where pdNo=%s"
#         cur.execute(sql,row['goodsNo'])
#         i = cur.fetchone()

#         if i['deliveryFee'] is None:
#             배송비 = ''
#         else:
#             배송비 = i['deliveryFee']
#     else:
#         배송비 = row['feeAmnt']

#     print(f"택배: {row['feeType']} / 배송비: {배송비}")

#     if viewMode == "Full":
#         print(f"{row['site']} / 주문건수: {str(row['cnt'])} / 주문합계: {str(row['Amnt'])}")
#         # 제품코드,제품명, 수취정보
#         sql = 'select goodsCode, qty, orderAmnt, goodsName from orderlist where rcverName = %s'
#         cur.execute(sql,row['rcverName'])
#         goods = cur.fetchall()
#         for g in goods:
#             print("코드: "+g['goodsCode'],"수량: "+str(g['qty']),"주문금액: "+str(g['orderAmnt']),"상품명: "+g['goodsName'])

#         print("="*60)
#         print('\n\n')


# ############# 요약정보 표시
# rows = db.getCount() # 사이트별 카운트
# cur = conn.cursor(pymysql.cursors.DictCursor)
# sqlsum = "select sum(orderAmnt)as 주문합계 from orderlist" 
# sqlcnt = "select count(*)as cnt from orderlist"
# cur.execute(sqlcnt)
# cnt = cur.fetchone()
# cur.execute(sqlsum)
# sum = cur.fetchone()
# amnt = str(sum['주문합계'])
# bb=format(int(amnt),',d')

# sitecnt = len(rows)

# print('\n')
# print('='*60)
# if sitecnt == 1:
#     print(f"{rows[0][0]}:{rows[0][1]}건 / 총주문건수:{cnt['cnt']}건 / 총주문합계:{bb}원")
# elif sitecnt == 2:
#     print(f"{rows[0][0]}:{rows[0][1]}건 / {rows[1][0]}:{rows[1][1]}건 / 총주문건수:{cnt['cnt']}건 / 총주문합계:{bb}원")
# elif sitecnt == 3:
#     print(f"{rows[0][0]}:{rows[0][1]}건 / {rows[1][0]}:{rows[1][1]}건 / {rows[2][0]}:{rows[2][1]}건 / 총주문건수:{cnt['cnt']}건 / 총주문합계:{bb}원")




########################################################################################################################################################

















sql = 'select count(*) from orderlist group by site'
cur.execute(sql)
res = cur.fetchall()


conn.close()
quit()




keys = res.keys()
val = res.values()
i = 1
for k,v in zip(keys,val):
    print(i,k,v)
    i = i + 1
for i in enumerate(res['data']):
    print(i['GoodsName'])
    


#함수 선언 시작###################################################################################################### 

base = Image.open("3107-150.jpg").convert("RGBA")
txt = Image.new("RGBA", base.size, (255,255,255,0))

def draw(item,r,c):
    d = ImageDraw.Draw(txt)
    x = item[1] + ((c-1) * labelW)
    y = item[2] + ((r-1) * labelH)
    fnt = ImageFont.truetype("NanumGothicExtraBold.ttf", item[3])
    d.text((x,y), item[0], font=fnt, fill=(0,0,0,255))

# 데이터베이스 연결함수
def connectDB(dbfile):
    conn = sqlite3.connect('ot.db', isolation_level = None)
    c = conn.cursor()
    return c

# 테이블 확인
def chkTable(table):
    sql = f'select name from sqlite_master where type = "table"'
    c.execute(sql)
    rows = c.fetchall()
    for row in rows:
        if row[0] == table:
            return True
    return False

def createTable(table):
    sql = f'''
    create table if not exists {table} (
        "No" integer not null,
        "Site" text not null,
        "OrderDate" text not null,
        "OrderNo" int not null,
        "BuyerName" text not null,
        "BuyerID" text not null,
        "GoodsNo" text not null,
        "GoodsName" text not null,
        "OrderQty" int not null,
        "SellPrice" int not null,
        "OrderAmnt" int not null,
        "SellerMngCode" text not null,
        "BuyerCp" text not null,
        "BuyerHt" text,
        "RcverName" text not null,
        "RcverInfoCp" text not null,
        "RcverInfoHt"text not null,
        "ZipCode" text not null,
        "RcverInfoAd" text not null,
        "DeliveryMemo" text,
        "DeliveryFeeType" text not null,
        "TransNo" text not null,
        "TransType" text not null,
        "MarketType" text not null,
        "DistrType"  text not null,
        "CartNo" text not null,
        "PayDate" text not null,
        "TransDueDate" text not null,
        "SttlExpectedAmnt" int not null,
        "ServiceUseAmnt" int not null,
        "SellerCouponDcAmnt" int
    );
    '''
    c.execute(sql)


# 테이블에 데이터입력 함수
def insertData(res):
    for No,item in enumerate(res['data']):
        No +=1
        goods = remove_tag(item['GoodsName']).strip()
        var = chkCode(goods)

        Site = 'Auction'
        OrderDate = item['OrderDate'].strip()
        OrderNo = item['OrderNo']
        BuyerName = item['BuyerName'].strip()
        BuyerID = item['BuyerID'].strip()
        GoodsNo = item['GoodsNo'].strip()
        GoodsName = var[0]
        OrderQty = item['OrderQty']
        SellPrice = item['SellPrice'].replace(',','')
        OrderAmnt = item['OrderAmnt'].replace(',','')
        
        
        SellerMngCode = var[1].replace('낱개상품','').replace('개별상품','').replace('(','').replace(')','')
        BuyerCp = item['BuyerCp'].strip()

        BuyerHt = item['BuyerHt']
        if BuyerHt is None:
            BuyerHt = ''
        else:
            if BuyerCp == BuyerHt:
                BuyerHt = ''

            
        RcverName = item['RcverName'].strip()
        RcverInfoCp = item['RcverInfoCp'].strip()
        RcverInfoHt = item['RcverInfoHt'].strip()


        if RcverInfoHt == RcverInfoCp:
            RcverInfoHt = ''

        ZipCode = item['ZipCode']
        
        
        if item['RcverInfoAd'] is None:
            RcverInfoAd = ''
        else:
            RcverInfoAd = remove_tag(item['RcverInfoAd']).strip()

        if item['DeliveryMemo'] is None:
            DeliveryMemo = ''
        else:
            DeliveryMemo = remove_tag(item['DeliveryMemo']).strip()

        if item['DeliveryFeeType'] is None:
            DeliveryFeeType = ''
        else:
            DeliveryFeeType = remove_tag(item['DeliveryFeeType']).strip()



        TransNo = item['TransNo'].strip()
        TransType = item['TransType']
        MarketType = item['MarketType']
        DistrType = item['DistrType']
        CartNo = item['CartNo']
        PayDate = item['PayDate']
        TransDueDate = item['TransDueDate']
        SttlExpectedAmnt = item['SttlExpectedAmnt'].replace(',','')
        ServiceUseAmnt = item['ServiceUseAmnt'].replace(',','')
        SellerCouponDcAmnt = item['SellerCouponDcAmnt'].replace(',','')

        sql = f"insert into {menu} values({No},'{Site}','{OrderDate}','{OrderNo}','{BuyerName}','{BuyerID}','{GoodsNo}','{GoodsName}',{OrderQty},{SellPrice},{OrderAmnt},'{SellerMngCode}','{BuyerCp}','{BuyerHt}','{RcverName}','{RcverInfoCp}','{RcverInfoHt}','{ZipCode}','{RcverInfoAd}','{DeliveryMemo}','{DeliveryFeeType}','{TransNo}','{TransType}','{MarketType}','{DistrType}','{CartNo}','{PayDate}','{TransDueDate}',{SttlExpectedAmnt},{ServiceUseAmnt},{SellerCouponDcAmnt})"
        # print(sql)
        c.execute(sql)

def txtStrip(str):
    if str is None:
        return ''
    else:
        return str.strip()

# 그리는 함수
def draw(item,r,c):
    d = ImageDraw.Draw(txt)
    x = item[1] + ((c-1) * labelW)
    y = item[2] + ((r-1) * labelH)
    fnt = ImageFont.truetype("NanumGothicExtraBold.ttf", item[3])
    d.text((x,y), item[0], font=fnt, fill=(0,0,0,255)) 




# 상품이름과 코드 분리
def chkCode(name):
    var = len(name)
    z = ''
    for i in range(1,var+1):
        t = name[-i]
        if t == '-':
            id = var - i
            for s in range(0,id):
                x = name[s]
                z = z + x
            상품 = z.strip()
            코드 = name[var-(var-id):].replace('-','').replace(' ','').strip()
            # print(코드, len(코드))
            return [상품,코드]
#함수 선언 끝###################################################################################################### 



# 상품명에서 상품코드 분리하는 패턴
# p = re.compile(r"([-]?)(\s?)[a-zA-Z{1}]\s?\s?[-]?\s?(\d{4,5}$)")
aid = "rmfrmffla"
apw = "qw970104@"
menu = input('메뉴명을 입력해주세요. : ')

menulst = ['신규주문','발송예정','배송중','배송완료']
c = connectDB('ot.db')
if menu not in menulst:
    print('조회불가능한 메뉴입니다. 종료합니다!')
    quit()
    
ac = Auction()
s = ac.login(aid,apw)
res = ac.getOrder(menu)

if len(res['data']) == 0:
    print('데이터가 0건입니다.')
    quit()
else:
    ##테이블이 없으면 생성, 있다면 테이블 데이터 초키화
    if not chkTable(menu):
        createTable(menu)
    else:
        sql = f'delete from {menu}'
        c.execute(sql)


## 데이터입력
insertData(res)

start = datetime.datetime.now()

# 데이터 정리
sql = f'''
select Rcvername,  count(*), RcverInfoCp, RcverInfoHt, ZipCode, RcverInfoAd, DeliveryMemo, DeliveryFeeType, sum(OrderAmnt) from {menu} 
group by Rcvername, RcverinfoAd, RcverinfoCp order by DeliveryfeeType Desc, No Desc
'''
c.execute(sql)
rows = c.fetchall()

######### 주문정보 루프
for row in rows:
    print("수취인:"+row[0]+" / ", str(row[1]) + "건===============================================")
    if row[3] == '':
        print("휴대폰:"+row[2])
    else:
        print("휴대폰:"+row[2],"전화:"+row[3])
    print("우편번호:"+row[4])
    print("주소:"+row[5])
    if row[6] != '':
        print("배송메모:"+row[6])

    print("택배:"+row[7])
    print("주문합계:"+str(row[8]))
    print("\n")

    # 제품코드,제품명, 수취정보
    sql = f'select SellerMngCode, OrderQty, OrderAmnt,GoodsName from {menu} where RcverName = "{row[0]}"'
    c.execute(sql)
    goods = c.fetchall()
    for g in goods:
        print("코드:"+g[0],"수량:"+str(g[1]),"주문금액:"+str(g[2]),"상품명:"+g[3])

    print("\n")


############# 요약정보 표시
sql = f'select distinct RcverName, count(*) from {menu} group by Rcvername, RcverinfoAd, RcverinfoCp'
c.execute(sql)
res = c.fetchall()
print('\n')
print('총주문인수: '+ str(len(res)))

sql = f'select count(*), sum(OrderAmnt) from {menu}'
c.execute(sql)
res = c.fetchall()

print('총주문건수: '+ str(res[0][0]))
print('총주문금액: ' + str(res[0][1]))

end = datetime.datetime.now()
print(end-start)


