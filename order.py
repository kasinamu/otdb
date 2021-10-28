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

def printDetail():
    var = input("\n\n1.세부내역전체 2.우체국용 3.제품찾기용 ENTER:종료\n")
    
    if var == '1':
        db.orderSummaryPrint()
    elif var == '2':
        db.orderSummaryPost()
    elif var == '3':
        db.orderFindItem()
    else:
        quit()
    printDetail()


start = f'2021-10-01'
end = f'2021-10-24'
start = ''
end = ''

try:
    mode = sys.argv[1]
except:
    mode = 'pay'
    # mode = 'all'

if mode == 'pay':
    CPmenus = ['ACCEPT','INSTRUCT']
    NAmenus = ['신규주문','배송준비']
    ACmenus = ['신규주문','발송예정']
elif mode == "all":
    CPmenus = ['ACCEPT','INSTRUCT','DEPARTURE','DELIVERING','FINAL_DELIVERY']
    NAmenus = ['신규주문','배송준비','배송중','배송완료']
    ACmenus = ['신규주문','발송예정','발송지연','배송중','배송완료']


## 쿠팡
cp = Coupang()
for menu in CPmenus:
    cpres = cp.getOrder(start,end,menu)
    if len(cpres['data']) > 0:
        print('쿠팡',menu,'...')
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
        print('네이버',menu,'...')
        db.insertOrder('네이버',menu,data)

## 옥션
ac = Auction()
for menu in ACmenus:
    acres = ac.getOrder(menu)
    count = len(acres['data'])
    if count > 0:
        print('옥션',menu,'...')
        db.insertOrder('옥션',menu,acres['data'])
        
db.getOrderSummary()
db.makePayOrderTempTable()
print('데이터 조회가 완료되었습니다.')
printDetail()



# 전체적인 정보보기
# db.orderSummaryPrint()

# 우체국용 
# db.orderSummaryPost()

# 제품찾을때 축약형
# db.orderFindItem()

## 요약인서트



## 새주문 체크를 위해 비교하기 위한 테이블을 만든다.

