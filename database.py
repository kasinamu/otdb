# from sqlite3.dbapi2 import Timestamp
import pymysql
from datetime import datetime, timedelta
import re



class Database():
    def __init__ (self):
        conn = None
        cur = None
        sql = ""
        # self.host = '211.54.212.66'
        self.host = '127.0.0.1'
        # self.host = '192.168.0.102'
        self.user = 'kasinamu'
        self.pw = 'dew30217'
        self.db = 'otdb'
        

    def connect(self):
        conn = pymysql.connect(host=f'{self.host}', user=f'{self.user}', password=f'{self.pw}', db=f'{self.db}', charset='utf8')
        return conn

    
    def createOrderTemp(self):
        conn = self.connect()
        cur = conn.cursor()
        sql = f'''
            CREATE TABLE IF NOT EXISTS orderTemp(
                no int not null,
                site varchar(10) not null,
                rcverName varchar(20) not null,
                qty int,
                goodsName varchar(100) not null,
                goodsCode varchar(10) not null,
            )
            '''        
        cur.execute(sql)
        conn.commit()
        conn.close()

    def insertOrderTemp(self):
        pass


    def dropTable(self,table):
        conn = self.connect()
        cur = conn.cursor()
        sql = f"drop table {table}"
        cur.execute(sql)
        conn.commit()
        conn.close()
        return 'OK'

    def getMaxNo(self,table):
        conn = self.connect()
        cur = conn.cursor()
        sql = f'select max(no) from {table}'
        cur.execute(sql)
        res = cur.fetchone()
        conn.close()
        
        if res[0] == None:
            return 0
        else:
            return res[0]

    def cpGetStatus(self,status):
        if status == 'ACCEPT':
            return '결제완료'
        elif status == 'INSTRUCT':
            return '상품준비중'
        elif status == 'DEPARTURE':
            return '배송지시'
        elif status == 'DELIVERING':
            return '배송중'
        elif status == 'FINAL_DELIVERY':
            return '배송완료'
        
    def naGetStatus(self,status):
        if status == 'WAITING_DISPATCH':
            return '신규주문'
        elif status == 'DELIVERED':
            return '배송완료'

    def naGetFeeType(self,str):
        if str=='CHARGE':
            return '선불'

    def insertProduct(self,data):
        pass

    def convertNull(self,str):
        if str == None:
            str = ''
        return str

    def getLogis(self,shop,code):
        if shop == '옥션':
            if code == 10005:
                return '우체국택배'
            elif code == 10003:
                return '로젠택배'
            elif code == 10014:
                return '대신택배'
            elif code == 10016:
                return '경동택배'

    def deleteTable(self,table):
        conn = self.connect()
        cur = conn.cursor()
        sql = f"delete from {table}"
        cur.execute(sql)
        conn.commit()
        conn.close()

    def getSummary(self):
        conn = self.connect()
        cur = conn.cursor()
        sql = "select sum(orderAmnt) from orderlist"
        cur.execute(sql)
        rows = cur.fetchone()
        print(rows)

        conn.commit()
        conn.close()
        


    def insertOrder(self,shop,menu,data):
        p = re.compile(r"([-]?)(\s?)[a-zA-Z{1}]\s?\s?[-]?\s?(\d{4,5}$)")
        table = 'orderlist'
        sqlContent = ""
        no = self.getMaxNo(table) + 1
        for i in data:
            if shop=='쿠팡':
                site = "쿠팡"
                status = self.cpGetStatus(i['status'])
                orderNo = i['orderId']
                orderDate = i['orderedAt']
                rcverName = i['receiver']['name']
                
                               
                serviceFee = 0
                settleAmnt = 0
                rcverTel1 =  self.convertNull(i['receiver']['safeNumber'])
                rcverTel2 = self.convertNull(i['receiver']['receiverNumber'])
                zipCode = i['receiver']['postCode']
                adress = i['receiver']['addr1'] + ' ' + i['receiver']['addr2']
                memo = i['parcelPrintMessage']
                feeType = '선불'
                feeAmnt = i['shippingPrice']
                logis = i['deliveryCompanyName']
                buyerName = i['orderer']['name']
                buyerID = self.convertNull(i['orderer']['email'])
                buyerTel1 = self.convertNull(i['orderer']['ordererNumber'])

                # orderItems Loop
                for item in i['orderItems']:
                    goodsNo = item['vendorItemId']
                    goodsName = item['vendorItemName']

                    m = p.search(goodsName)
                    index = len(m.group())
                    goodsCode = m.group().replace(' ','').replace('-','')
                    goodsName = goodsName[0:len(goodsName)-index]


                    qty = item['shippingCount']
                    goodsPrice = item['salesPrice']
                    orderAmnt = item['orderPrice']
                    goodsDc = item['discountPrice']

                    sql = f"({no},'{site}','{status}','{orderNo}','{orderDate}','{rcverName}','{goodsNo}','{goodsName}','{goodsCode}',{qty},{goodsPrice},{orderAmnt},{goodsDc},{serviceFee},{settleAmnt},'{rcverTel1}','{rcverTel2}','{zipCode}','{adress}','{memo}','{feeType}',{feeAmnt},'{logis}','{buyerName}','{buyerID}','{buyerTel1}'),\n"
                    sqlContent += sql
                    no += 1

            elif shop == '네이버':
                site = "네이버"
                status = self.naGetStatus(i['orderStatus'])
                orderNo = i['orderNo']
                if status == '배송완료':
                    orderDate = self.tstamp(i['payDateTime'])
                    memo = ''
                elif status is None:
                    orderDate = self.tstamp(i['payDateTime'])
                    memo = ''
                else:
                    memo = self.convertNull(i['productOrderMemo'])
                    orderDate = self.tstamp(i['orderDateTime'])
                rcverName = i['receiverName']

                serviceFee = 0
                settleAmnt = 0
                rcverTel1 = i['receiverTelNo1']
                rcverTel2 = self.convertNull(i['receiverTelNo2'])
                zipCode = i['receiverZipCode']
                adress = i['receiverAddress']
                feeType = self.naGetFeeType(i['deliveryFeeClass'])
                feeAmnt = i['deliveryFeeAmt']
                logis = self.convertNull(i['deliveryCompanyName'])
                buyerName = i['orderMemberName']
                buyerID = i['orderMemberId']
                buyerTel1 = i['orderMemberTelNo']
                goodsNo = i['productNo']

                goodsName = i['productName']

                m = p.search(goodsName)
                index = len(m.group())
                goodsCode = m.group().replace(' ','').replace('-','')
                goodsName = goodsName[0:len(goodsName)-index]
                
                qty = i['orderQuantity']
                goodsPrice = i['productUnitPrice']
                orderAmnt = i['productPayAmt']
                goodsDc = int(i['totalDiscountAmt']) + int(i['sellerDiscountAmt'])

                sql = f"({no},'{site}','{status}','{orderNo}','{orderDate}','{rcverName}','{goodsNo}','{goodsName}','{goodsCode}',{qty},{goodsPrice},{orderAmnt},{goodsDc},{serviceFee},{settleAmnt},'{rcverTel1}','{rcverTel2}','{zipCode}','{adress}','{memo}','{feeType}',{feeAmnt},'{logis}','{buyerName}','{buyerID}','{buyerTel1}'),\n"
                sqlContent += sql
                no += 1                 


            elif shop == '옥션':
                # 옥션은 정산예정,완료 메뉴의 주소,배송메모,우편번호,배송구분 항목의 NONE으로 잡힌다. 
                site = "옥션"
                status = menu
                orderNo = i['OrderNo']
                orderDate = i['OrderDate']
                rcverName = i['RcverName']
                
                serviceFee = self.removeComma(i['ServiceUseAmnt'])
                settleAmnt = self.removeComma(i['SttlExpectedAmnt'])
                rcverTel1 = i['RcverInfoCp']
                rcverTel2 = self.convertNull(i['RcverInfoHt'])
                zipCode = self.convertNull(i['ZipCode'])
                adress = self.convertNull(self.remove_tag(i['RcverInfoAd']))
                memo = self.convertNull(self.remove_tag(i['DeliveryMemo']))
                feeType = self.convertNull(i['DeliveryFeeType'])
                feeAmnt = 0
                logis = self.getLogis('옥션',(i['DeliveryComp']))
                buyerName = i['BuyerName']
                buyerID = i['BuyerID']
                buyerTel1 = i['BuyerCp']
                goodsNo = i['GoodsNo']
                goodsName = self.remove_tag(i['GoodsName'])
                
                m = p.search(goodsName)
                if m is None:
                    goodsCode = ''
                    goodsName = i['GoodsName']
                else:
                    index = len(m.group())
                    goodsCode = m.group().replace(' ','').replace('-','')
                    goodsName = goodsName[0:len(goodsName)-index]


                # goodsCode = self.remove_tag(i['SellerMngCode'])

                qty = (i['OrderQty'])
                goodsPrice = self.removeComma(i['SellPrice'])
                orderAmnt = self.removeComma(i['OrderAmnt'])
                goodsDc = self.getACDC('옥션',i['SellerCouponDcAmnt'],i['SellerPointDcAmnt'])

                sql = f"({no},'{site}','{status}','{orderNo}','{orderDate}','{rcverName}','{goodsNo}','{goodsName}','{goodsCode}',{qty},{goodsPrice},{orderAmnt},{goodsDc},{serviceFee},{settleAmnt},'{rcverTel1}','{rcverTel2}','{zipCode}','{adress}','{memo}','{feeType}',{feeAmnt},'{logis}','{buyerName}','{buyerID}','{buyerTel1}'),\n"
                sqlContent += sql
                # print(sql)
                no += 1                         
        sql = f"insert into {table} values" + sqlContent[0:len(sqlContent)-2]
        self.excute(sql)

    def getACDC(self,shop,SellCoupon,SellPoint):
        if shop == '옥션':
            if SellCoupon is None:
                SellCoupon = 0
            else:
                SellCoupon = SellCoupon.replace(',','')

            if SellPoint is None:
                SellPoint = 0
            else:
                SellPoint = SellPoint.replace(',','')

            return int(SellCoupon) + int(SellPoint)

    def getCount(self):
        conn = self.connect()
        cur = conn.cursor()        
        sql = 'select site,count(orderNo) from orderlist group by site'
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()
        return rows
        

    def getOrderSummary(self):
        conn = self.connect()
        cur = conn.cursor()
        sql = "delete from orderSummary"
        cur.execute(sql)

        sql = f'''
            CREATE TABLE IF NOT EXISTS orderSummary(
                no int not null,
                site varchar(10) not null,
                rcverName varchar(20) not null,
                orderCount int,
                goodsCode varchar(100) not null,
                orderAmnt int not null default 0,
                rcverTel1 varchar(15) not null,
                rcverTel2 varchar(15),
                zipCode char(10) not null,
                adress varchar(150) not null,
                memo varchar(300),
                feeType varchar(10),
                feeAmnt int default 0,
                logis varchar(15)
            )
            '''
        # cur.execute(sql)
        # conn.commit()
        # quit()


        sql = f'''
        select site, rcverName, count(*)as cnt, rcverTel1, rcverTel2, zipCode, adress, memo, feeType, sum(orderAmnt)as orderAmnt, feeAmnt, logis from orderlist group
        by rcverName, adress, rcverTel1 order by cnt Desc, site Desc
        '''
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(sql)
        rows = cur.fetchall()
        no = 1
        for r in rows:
            rcv = r['rcverName']
            # print(f"{row['rcverName']}")
            
            # 서브쿼리
            sql = "select goodsCode, qty from orderlist where rcverName=%s and adress=%s"
            cur.execute(sql,(r['rcverName'],r['adress']))
            goods = cur.fetchall()
            strGoods = ""
            for n,good in enumerate(goods):
                if n != 0:
                    strGoods += ', '
                strGoods += f"{good['goodsCode']} {good['qty']}ea"
            # print(f"{rcv} [{r['cnt']}건], {strGoods}")
            ad = r['adress'].split(' ')
            주소 = f"{ad[0]} {ad[1]} {ad[2]}"

            sql = "insert into orderSummary values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(sql,(no,r['site'],r['rcverName'],r['cnt'],strGoods,r['orderAmnt'],r['rcverTel1'],r['rcverTel2'],r['zipCode'],주소,r['memo'],r['feeType'],r['feeAmnt'],r['logis']))
            conn.commit()
            # print(sql)
            no+=1

        return 'OK'




    def removeComma(self,money):
        return int(money.replace(',',''))

    def remove_tag(self,content):
        cleanr =re.compile('<.*?>')
        try:
            cleantext = re.sub(cleanr, '', content)
            return cleantext
        except:
            pass

    def tstamp(self,now):
        if now is None:
            return None

        if 'Date' in now:
            now = now[6:16]
        return datetime.fromtimestamp(int(now[0:10])).strftime('%Y-%m-%d %H:%M:%S')

    def excute(self,sql):
        conn = self.connect()
        cur = conn.cursor()        
        cur.execute(sql)
        conn.commit()
        conn.close()

    def convertDate(self,now):
        if now != None:
            # now = now[6:16]
            _date = datetime.datetime.fromtimestamp(int(now)).strftime('%Y-%m-%d %H:%M:%S')
            return _date
        else:
            return ''

    def createTable(self,table):
        try:
            conn = self.connect()
            cur = conn.cursor()
            sql = f'''
                CREATE TABLE IF NOT EXISTS {table}(
                    no int not null,
                    site varchar(10) not null,
                    status varchar(20) not null,
                    orderNo varchar(20) not null,
                    orderDate datetime not null,
                    rcverName varchar(20) not null,
                    goodsNo varchar(15) not null,
                    goodsName varchar(100) not null,
                    goodsCode varchar(10) not null,
                    qty tinyint not null default 1,
                    goodsPrice int not null default 0,
                    orderAmnt int not null default 0,
                    goodsDc int default 0,
                    serviceFee int default 0,
                    settleAmnt int default 0,
                    rcverTel1 varchar(15) not null,
                    rcverTel2 varchar(15),
                    zipCode char(10) not null,
                    adress varchar(150) not null,
                    memo varchar(300),
                    feeType varchar(10),
                    feeAmnt int default 0,
                    logis varchar(15),
                    buyerName varchar(25) not null,
                    buyerID varchar(15) not null,
                    buyerTel1 varchar(15)
                )
                '''
            cur.execute(sql)
            conn.commit()
            conn.close()
            return 'OK'
        except:
            return 'Fail'
        

    def insertProduct(self,pd):
        p = re.compile(r"([-]?)(\s?)[a-zA-Z{1}]\s?\s?[-]?\s?(\d{4,5}$)")
        conn = self.connect()
        cur = conn.cursor()

        acCode = pd['CategoryCodeIAC']
        Category = pd['CategoryLNameIAC']+">"+pd['CategoryMNameIAC']+">"+pd['CategorySNameIAC']
        dcType = pd['DcTypeIAC']
        dcValue = pd['DcValueIAC']
        deliveryFee = pd['DeliveryFee']
        deliveryTemplateNo = pd['DeliveryTemplateNo']
        dispEndDate = self.tstamp(pd['DispEndDate'])
        dispStopDate = self.tstamp(pd['DispStopDateIAC'])
        goodsName = pd['GoodsName']

        try:
            
            m = p.search(goodsName)
            index = len(m.group())
            goodsCode = m.group().replace(' ','').replace('-','')
            goodsName = goodsName[0:len(goodsName)-index]
        except:
            goodsCode = ''

        price = pd['SellPriceIAC']
        listImgUrl = pd['ListImgUrl']
        esmCode = pd['SDCategoryCode']
        esm1 = pd['SDCategoryLevel1Name']
        esm2 = pd['SDCategoryLevel2Name']
        esm3 = pd['SDCategoryLevel3Name']
        esm4 = pd['SDCategoryLevel4Name']
        esm5 = pd['SDCategoryName']
        mpdNo = pd['SingleGoodsNo']
        pdNo = pd['SiteGoodsNoIAC']
        regDate = self.tstamp(pd['SiteRegDate'])
        updDate = self.tstamp(pd['SiteUpdDate'])
        status = self.getPDStatus(pd['StatusCodeIAC'])
        stockQty = pd['StockQty']
        stockManage = pd['StockQtyManageYn']
        transCloseTime = pd['TransCloseTimeIac']
        transPolicy = pd['TransPolicyNameIac']

        sql = '''
        Insert into product values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        '''
        data=(mpdNo,goodsName,goodsCode,pdNo,status,price,dcType,dcValue,transPolicy,stockQty,stockManage,ac1,ac2,ac3,esm1,esm2,esm3,esm4,deliveryFee,deliveryTemplateNo,regDate,updDate,dispEndDate,dispStopDate,url)


        cur.execute(sql,data)
        conn.commit()

    # 상품 status를 입력받아 한글로 돌려줌
    def getPDStatus(self,status):
        if status == '11':
            status = '판매가능'
        elif status == '21':
            status = '판매중지'
        elif status == '22':
            status = '판매불가'
        elif status == '31':
            status = 'SKU품절'
        elif status == '01':
            status = '등록대기'
        return status


    def createPDTabel(self):
        # 제품테이블 생성
        conn = self.connect()
        cur = conn.cursor()

        sql = '''
        CREATE TABLE IF NOT EXISTS product(
            mpdNo varchar(20),
            goodsName varchar(100),
            goodsCode varchar(7),
            pdNo varchar(20),
            status varchar(10),
            price int,
            dcType int,
            dcValue int,
            transPolicy varchar(20),
            stockQty int,
            stockManage varchar(2),
            ac1 varchar(20),
            ac2 varchar(20),
            ac3 varchar(20),
            esm1 varchar(20),
            esm2 varchar(20),
            esm3 varchar(20),
            esm4 varchar(20),
            deliveryFee int,
            deliveryTemplateNo varchar(10),
            regDate datetime,
            updDate datetime,
            dispEndDate datetime,
            dispStopDate datetime,
            url varchar(150)
        );
        '''        
        cur.execute(sql)
        conn.commit()


    def orderSummaryPrint(self,mode=''):
        conn = self.connect()
        cur = conn.cursor()

        sql = f'''
        select rcverName, count(*)as cnt, rcverTel1, rcverTel2, zipCode, adress, memo, feeType, sum(orderAmnt)as Amnt, site, goodsNo, feeAmnt from orderlist group
        by rcverName, adress, rcverTel1 order by feeType Desc, No Desc
        '''
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(sql)
        rows = cur.fetchall()

        if mode != 'check':
            print('\n\n')

        ######### 주문정보 루프
        for row in rows:
            print("="*60)
            print(f"수취인: {row['rcverName']}")
            
            if mode != 'check':
                # 전화 1,2가 같으면 1개만 출력
                if row['rcverTel2'] == '':
                    print(f"휴대폰: {row['rcverTel1']}")
                else:
                    if row['rcverTel2'] == row['rcverTel1']:
                        print(f"전화: {row['rcverTel1']}")
                    else:
                        print(f"전화: {row['rcverTel1']} 전화2: {row['rcverTel2']}")

                print(f"우편번호: {row['zipCode']}")
                print(f"주소: {row['adress']}")
                if row['memo'] != '':
                    print("배송메모: "+row['memo'])

                # 택배비추출 / 옥션이면 제품테이블에서 상품배송비를 긁어온다.
                if row['site'] == '옥션':
                    sql = "select deliveryFee from product where pdNo=%s"
                    cur.execute(sql,row['goodsNo'])
                    i = cur.fetchone()
                    if i is None: #상품이 1.0등록
                        배송비 = ''

                    if i['deliveryFee'] is None:
                        배송비 = ''
                    else:
                        배송비 = i['deliveryFee']
                else:
                    배송비 = row['feeAmnt']

                # 묶음배송 선불확인
                sql = "select count(feetype)as cnt from orderlist where rcverName=%s and rcverTel1=%s and feeType=%s"
                cur.execute(sql,(row['rcverName'],row['rcverTel1'],'선불'))
                var = cur.fetchone()
                if var['cnt'] != 0:
                    print(f"택배: 선불 / 배송비: {배송비}")
                else:
                    print(f"택배: 착불")

            if mode == "Full" or mode == "check":
                print(f"{row['site']} / 주문건수: {str(row['cnt'])} / 주문합계: {str(row['Amnt'])}")
                # 제품코드,제품명, 수취정보
                sql = 'select goodsCode, qty, orderAmnt, goodsName from orderlist where rcverName = %s'
                cur.execute(sql,row['rcverName'])
                goods = cur.fetchall()
                for g in goods:
                    if mode == 'check':
                        print(f"{g['goodsCode']} {g['qty']}ea / {g['goodsName']}")
                    else:
                        print("코드: "+g['goodsCode'],"수량: "+str(g['qty']),"주문금액: "+str(g['orderAmnt']),"상품명: "+g['goodsName'])

                if mode != 'check':
                    print('\n')


        ############# 요약정보 표시
        site = self.getCount() # 사이트별 카운트
        cur = conn.cursor(pymysql.cursors.DictCursor)
        sqlsum = "select sum(orderAmnt)as 주문합계 from orderlist" 
        sqlcnt = "select count(*)as cnt from orderlist"
        cur.execute(sqlcnt)
        cnt = cur.fetchone()
        cur.execute(sqlsum)
        sum = cur.fetchone()
        amnt = str(sum['주문합계'])
        bb=format(int(amnt),',d')

        sitecnt = len(site)

        print('\n')
        print('='*60)
        if sitecnt == 1:
            print(f"{site[0][0]}:{site[0][1]}건 / 총주문건수:{cnt['cnt']}건 / 총주문합계:{bb}원")
        elif sitecnt == 2:
            print(f"{site[0][0]}:{site[0][1]}건 / {site[1][0]}:{site[1][1]}건 / 총주문건수:{cnt['cnt']}건 / 총주문합계:{bb}원")
        elif sitecnt == 3:
            print(f"{site[0][0]}:{site[0][1]}건 / {site[1][0]}:{site[1][1]}건 / {site[2][0]}:{site[2][1]}건 / 총주문건수:{cnt['cnt']}건 / 총주문합계:{bb}원")


   