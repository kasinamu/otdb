import pymysql
from datetime import datetime, timedelta
import re


class Database():
    def __init__ (self):
        conn = None
        cur = None
        sql = ""
        self.host = '211.54.212.66'
        # self.host = '127.0.0.1'
        # self.host = '192.168.0.102'
        self.user = 'pc01'
        self.pw = 'qw970104'

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

    def excuteRow(self,sql,dict=False):
        conn = self.connect()
        if dict == False:
            cur = conn.cursor()
        else:
            cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(sql)
        res = cur.fetchall()
        conn.close()
        return res

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
        
    def excuteDict(self,sql):
        conn = self.connect()
        cur = conn.cursor()        
        cur.execute(sql)
        i = cur.fetchone()
        conn.commit()
        conn.close()
        return i[0]

    def checkNewOrder(self,orderNo):
        res = self.excuteDict(f'select count(*)as cnt from temp_orderlist where orderNo={orderNo}')
        # print(res)
        if res == 0:
            return "확인필요"
        elif res == 1:
            return "확인완료"


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
                check = self.checkNewOrder(orderNo)
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
                    # goodsName = item['vendorItemName']
                    res = self.goodsSplit(item['vendorItemName'])
                    goodsCode = res['goodsCode']
                    goodsName = res['goodsName']

                    qty = item['shippingCount']
                    goodsPrice = item['salesPrice']
                    orderAmnt = item['orderPrice']
                    goodsDc = item['discountPrice']

                    sql = f"({no},'{check}','{site}','{status}','{orderNo}','{orderDate}','{rcverName}','{goodsNo}','{goodsName}','{goodsCode}',{qty},{goodsPrice},{orderAmnt},{goodsDc},{serviceFee},{settleAmnt},'{rcverTel1}','{rcverTel2}','{zipCode}','{adress}','{memo}','{feeType}',{feeAmnt},'{logis}','{buyerName}','{buyerID}','{buyerTel1}'),\n"
                    sqlContent += sql
                    no += 1

            elif shop == '네이버':
                site = "네이버"
                status = self.naGetStatus(i['orderStatus'])
                orderNo = i['orderNo']

                check = self.checkNewOrder(orderNo)

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

                res = self.goodsSplit(i['productName'])
                goodsCode = res['goodsCode']
                goodsName = res['goodsName']
                
                qty = i['orderQuantity']
                goodsPrice = i['productUnitPrice']
                orderAmnt = i['productPayAmt']
                goodsDc = int(i['totalDiscountAmt']) + int(i['sellerDiscountAmt'])

                sql = f"({no},'{check}','{site}','{status}','{orderNo}','{orderDate}','{rcverName}','{goodsNo}','{goodsName}','{goodsCode}',{qty},{goodsPrice},{orderAmnt},{goodsDc},{serviceFee},{settleAmnt},'{rcverTel1}','{rcverTel2}','{zipCode}','{adress}','{memo}','{feeType}',{feeAmnt},'{logis}','{buyerName}','{buyerID}','{buyerTel1}'),\n"
                sqlContent += sql
                no += 1                 


            elif shop == '옥션':
                # 옥션은 정산예정,완료 메뉴의 주소,배송메모,우편번호,배송구분 항목의 NONE으로 잡힌다. 
                site = "옥션"
                status = menu
                orderNo = i['OrderNo']
                check = self.checkNewOrder(orderNo)

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

                res = self.goodsSplit(self.remove_tag(i['GoodsName']))
                goodsCode = res['goodsCode']
                goodsName = res['goodsName']

                qty = (i['OrderQty'])
                goodsPrice = self.removeComma(i['SellPrice'])
                orderAmnt = self.removeComma(i['OrderAmnt'])
                goodsDc = self.getACDC('옥션',i['SellerCouponDcAmnt'],i['SellerPointDcAmnt'])

                sql = f"({no},'{check}','{site}','{status}','{orderNo}','{orderDate}','{rcverName}','{goodsNo}','{goodsName}','{goodsCode}',{qty},{goodsPrice},{orderAmnt},{goodsDc},{serviceFee},{settleAmnt},'{rcverTel1}','{rcverTel2}','{zipCode}','{adress}','{memo}','{feeType}',{feeAmnt},'{logis}','{buyerName}','{buyerID}','{buyerTel1}'),\n"
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
            if len(ad) >= 3:
                주소 = f"{ad[0]} {ad[1]} {ad[2]}"
            elif len(ad) >= 2:
                주소 = f"{ad[0]} {ad[1]}"
            else:
                주소 = f"{ad[0]}"
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
                    check varchar(10),
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
        


    def goodsSplit(self,goodsName):
        # 괄호삭제 (1개 혹은 2개의 경우)
        goodsName = goodsName.replace("중고",'').strip()
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

            if i == 0 and dif > 5:
                goodsCode = ''
            #코드 분리후 남은 하이픈과 공백제거
            goodsName = goodsName.replace(goodsCode,'').strip().strip('-').strip()     
            goodsCode = goodsCode.strip().replace(' ','')
            data = {'goodsName':goodsName, 'goodsCode':goodsCode}
        except:
            data = {'goodsName':goodsName, 'goodsCode':''}
        
        return data


    def insertProduct_v2(self,pd):
        conn = self.connect()
        cur = conn.cursor()

        ac2 = pd['CategoryLNameIAC']
        ac3 = pd['CategoryMNameIAC']
        ac4 = pd['CategorySNameIAC']
        dcType = pd['DcTypeIAC']
        dcValue = pd['DcValueIAC']
        deliveryFee = pd['DeliveryFee']
        deliveryTemplateNo = pd['DeliveryTemplateNo']
        dispEndDate = self.tstamp(pd['DispEndDate'])
        dispStopDate = self.tstamp(pd['DispStopDateIAC'])
        goodsName = pd['GoodsName']

        # 제품명에서 코드와 상품명 분리
        res = self.goodsSplit(goodsName)
        goodsName = res['goodsName']
        goodsCode = res['goodsCode']

        price = pd['SellPriceIAC']
        listImgUrl = pd['ListImgUrl']
        esm1 = pd['SDCategoryLevel1Name']
        esm2 = pd['SDCategoryLevel2Name']
        esm3 = pd['SDCategoryLevel3Name']
        esm5 = pd['SDCategoryName']
        mpdNo = pd['SingleGoodsNo']
        pdNo = pd['SiteGoodsNoIAC']
        regDate = self.tstamp(pd['SiteRegDate'])
        updDate = self.tstamp(pd['SiteUpdDate'])
        status = self.getPDStatus(pd['StatusCodeIAC'])
        stockQty = pd['StockQty']
        stockManage = pd['StockQtyManageYn']
        transPolicy = pd['TransPolicyNameIac']
        transCloseTime = pd['TransCloseTimeIac']
        

        sql = '''
        Insert into products values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        '''
        data=(mpdNo,goodsName,goodsCode,pdNo,status,price,dcType,dcValue,transPolicy,transCloseTime,stockQty,stockManage,ac2,ac3,ac4,esm1,esm2,esm3,esm5,deliveryFee,deliveryTemplateNo,regDate,updDate,dispEndDate,dispStopDate,listImgUrl)


        cur.execute(sql,data)
        conn.commit()


    def insertProduct_v1(self,pd):
        conn = self.connect()
        cur = conn.cursor()

        ac2 = pd['CategoryLName']
        ac3 = pd['CategoryMName']
        ac4 = pd['CategorySName']
        dcType = pd['IacDcValueType']
        dcValue = pd['IacDcValue']
        deliveryFee = pd['DeliveryFee']
        deliveryTemplateNo = ''
        dispEndDate = self.tstamp(pd['DispEndDate'])
        dispStopDate = self.tstamp(pd['DispEndDate'])

        # 제품명에서 코드와 상품명 분리
        res = self.goodsSplit(pd['GoodsName'])
        goodsName = res['goodsName']
        goodsCode = res['goodsCode']

        price = pd['SellPrice']
        listImgUrl = pd['ListImgUrl']
        esm1 = ''
        esm2 = ''
        esm3 = ''
        esm5 = ''
        mpdNo = pd['GoodsNo']
        pdNo = pd['SiteGoodsNo']
        regDate = self.tstamp(pd['SiteRegDate'])
        updDate = self.tstamp(pd['SiteUpdDate'])
        status = self.getPDStatus(pd['StatusCode'])
        stockQty = pd['StockQty']
        stockManage = ''
        transPolicy = pd['TransPolicyName']
        transCloseTime = pd['TransCloseTime']
        

        sql = '''
        Insert into products values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        '''
        data=(mpdNo,goodsName,goodsCode,pdNo,status,price,dcType,dcValue,transPolicy,transCloseTime,stockQty,stockManage,ac2,ac3,ac4,esm1,esm2,esm3,esm5,deliveryFee,deliveryTemplateNo,regDate,updDate,dispEndDate,dispStopDate,listImgUrl)


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
        CREATE TABLE IF NOT EXISTS products(
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



    # 옥션 신버전(2.0) 상품전체 가져와서 DB에 인서트
    def insertAllProduct_V2(self):
        from auction import Auction
        ac = Auction()
        
        pdno = 1
        for p in range(1,100):
            res = ac.getProduct_V2_100(p) # 구상품
            cnt = len(res['data'])
            n=1
            for i in res['data']:
                print(pdno, i['SiteGoodsNoIAC'], i['GoodsName'])
                print(i,"\n\n")
                self.insertProduct_v2(i) # v.1 구상품
                pdno +=1
                n+=1
                
                # 종료캐치
                if cnt != 100 and (n-1)==cnt:
                    break


    # 옥션 구버전 상품전체 가져와서 DB에 인서트
    def insertAllProduct_V1(self):
        from auction import Auction
        ac = Auction()
        
        pdno = 1
        for p in range(1,100):
            res = ac.getProduct_V1_100(p) # 구상품
            cnt = len(res['data'])
            n=1
            for i in res['data']:
                print(pdno, i['SiteGoodsNo'], i['GoodsName'])
                print(i,"\n\n")
                self.insertProduct_v1(i) # v.1 구상품
                pdno +=1
                n+=1
                
                # 종료캐치
                if cnt != 100 and (n-1)==cnt:
                    break

    def orderFindItem(self):
        conn = self.connect()
        cur = conn.cursor()

        sql = f'''
        select rcverName, count(*)as cnt, rcverTel1, sum(orderAmnt)as Amnt, site, goodsNo,goodsCode,goodsName,goodsPrice,qty from orderlist group
        by rcverName, adress, rcverTel1 order by No Desc
        '''
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(sql)
        rows = cur.fetchall()
        no = 1
        for row in rows:
            name = row['rcverName']
            cnt = row['cnt']
            t1 = row['rcverTel1']
            site = row['site']
            goodsNo = row['goodsNo']

            print("\n")
            print(f"No.{str(no).zfill(2)} / {site} / {cnt}건 / {name}")
            sql = "select goodsCode,goodsName,qty from orderlist where rcverName=%s and rcverTel1=%s"
            cur = conn.cursor(pymysql.cursors.DictCursor)
            cur.execute(sql,(name,t1))
            items = cur.fetchall()
            n = 1
            for i in items:
                goods = i['goodsName']
                code = i['goodsCode']
                qty = i['qty']
                print(f"-{str(n).zfill(2)} / {code} / {qty}ea / {goods}")
                n+=1
            no+=1
            





    def orderSummaryPost(self):
        conn = self.connect()
        cur = conn.cursor()

        sql = f'''
        select rcverName, rcverTel1, rcverTel2, zipCode, adress, memo, feeType, feeAmnt, site, goodsNo from orderlist group
        by rcverName, adress, rcverTel1 order by feeType Desc, No Desc
        '''
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(sql)
        rows = cur.fetchall()

        ######### 주문정보 루프
        for row in rows:
            name = row['rcverName']
            t1 = row['rcverTel1']
            t2 = row['rcverTel2']
            zip = row['zipCode']
            adress = row['adress']
            memo = row['memo']
            site = row['site']
            fee = row['feeAmnt']

            print("\n")
            print(f"수취인: {name}")
            
            if t1 != t2:
                print(f"전화: {t1} 전화2: {t2}")
            else:
                print(f"전화: {t1}")                

            print(f"우편번호: {zip}")
            print(f"주소: {adress}")
            if memo != '':
                print(f"배송메모: {memo}")

            # 택배비추출 / 옥션이면 제품테이블에서 상품배송비를 긁어온다.
            if site == '옥션':
                sql = "select deliveryFee from products where pdNo=%s"
                cur.execute(sql,row['goodsNo'])
                i = cur.fetchone()
                if i is None: #상품이 1.0등록
                    fee = ''
                else:
                    fee = i['deliveryFee']
            else:
                fee = row['feeAmnt']

            if fee == 4500:
                fee = 4000
            fee = format(fee,',')
            

            # 묶음배송 선불확인
            sql = "select count(feetype)as cnt from orderlist where rcverName=%s and rcverTel1=%s and feeType=%s"
            cur.execute(sql,(name,t1,'선불'))
            var = cur.fetchone()
            if var['cnt'] != 0:
                print(f"택배: 선불({fee})")
            else:
                print(f"택배: 착불")



    def orderSummaryPrint(self):
        conn = self.connect()
        cur = conn.cursor()

        sql = f'''
        select rcverName, count(*)as cnt, rcverTel1, rcverTel2, zipCode, adress, memo, feeType, sum(orderAmnt)as Amnt, site, goodsNo, feeAmnt from orderlist group
        by rcverName, adress, rcverTel1 order by feeType Desc, No Desc
        '''
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(sql)
        rows = cur.fetchall()

        ######### 주문정보 루프
        no = 1
        for row in rows:
            rcv = row['rcverName']
            tel = row['rcverTel1']
            adress = row['adress']
            zip = row['zipCode']
            memo = row['memo']
            site = row['site']
            pdNo = row['goodsNo']
            cnt = row['cnt']
            amnt = format(row['Amnt'],',')

            print("\n")
            
            # 택배비추출 / 옥션이면 제품테이블에서 상품배송비를 긁어온다.
            if site == '옥션':
                sql = "select deliveryFee from products where pdNo=%s"
                cur.execute(sql,pdNo)
                i = cur.fetchone()
                if i is None: #상품이 1.0등록
                    배송비 = ''
                else:
                    배송비 = i['deliveryFee']
            else:
                배송비 = row['feeAmnt']

            # 묶음배송 선불확인
            sql = "select count(feetype)as cnt from orderlist where rcverName=%s and rcverTel1=%s and feeType=%s"
            cur.execute(sql,(rcv,tel,'선불'))
            var = cur.fetchone()
            if var['cnt'] != 0:
                배송구분 = f"선불({배송비})"
            else:
                배송구분 = "착불"

            print(f"No.{str(no).zfill(2)} | {rcv} | {tel} | {배송구분}")
            print(f"우){zip} / {adress}")
            if row['memo'] != '':
                print(f"메모: {memo}")

            print(f"{site} {cnt}건 / 주문합계: {amnt}원")

            # 제품코드,제품명, 수취정보
            sql = 'select goodsCode, qty, orderAmnt, goodsName from orderlist where rcverName = %s'
            cur.execute(sql,rcv)
            goods = cur.fetchall()
            for g in goods:
                print(f"-- {g['goodsCode']} {g['qty']}ea {format(g['orderAmnt'],',')}원 / {g['goodsName']}")
            
            no+=1


        ############# 요약정보 표시
        site = self.getCount() # 사이트별 카운트
        cur = conn.cursor(pymysql.cursors.DictCursor)
        sqlsum = "select sum(orderAmnt)as 주문합계 from orderlist" 
        sqlcnt = "select count(*)as cnt from orderlist"
        
        sqlplusship = "select count(*)as cnt from orderlist group by rcverName"
        cur.execute(sqlplusship)
        cnt = cur.fetchall()
        plusship = 0
        for c in cnt:
            if int(c['cnt']) > 1:
                plusship += 1


        cur.execute(sqlcnt)
        cnt = cur.fetchone()
        cur.execute(sqlsum)
        sum = cur.fetchone()
        amnt = str(sum['주문합계'])
        bb=format(int(amnt),',d')

        sitecnt = len(site)

        print('\n')
        print('='*60)

        print(f"단일포장 {no-plusship-1}건 / 묶음포장 {plusship}건 / 전체포장수 {no-1}건 / ")
        if sitecnt == 1:
            print(f"{site[0][0]}:{site[0][1]}건 / 총주문건수:{cnt['cnt']}건 / 총주문합계:{bb}원")
        elif sitecnt == 2:
            print(f"{site[0][0]}:{site[0][1]}건 / {site[1][0]}:{site[1][1]}건 / 총주문건수:{cnt['cnt']}건 / 총주문합계:{bb}원")
        elif sitecnt == 3:
            print(f"{site[0][0]}:{site[0][1]}건 / {site[1][0]}:{site[1][1]}건 / {site[2][0]}:{site[2][1]}건 / 총주문건수:{cnt['cnt']}건 / 총주문합계:{bb}원")



    def makePayOrderTempTable(self):
        self.excute("truncate temp_orderlist")
        self.excute("insert into temp_orderlist select * from orderlist")



