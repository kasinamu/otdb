from urllib import parse
import requests
from requests import Session
from dateutil.relativedelta import relativedelta
from json import dumps
import json
from datetime import datetime, timedelta
import re


class Auction(Session):
    def __init__(self):
        super().__init__()
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.id = "rmfrmffla"
        self.pw = "qw970104@"
        self.Cookie = ""
        self.login()

    def login(self):
        login_info = dict()
        login_info['Password'] = self.pw
        login_info['Type'] = 'S'
        login_info['ReturnUrl'] = '/Home/Home'
        login_info['SiteType'] = 'IAC'
        login_info['Id'] = self.id
        login_info['RememberMe'] = 'false'        

        url = 'https://www.esmplus.com/SignIn/Authenticate'
        res = self.post(url, data=login_info)
        redirect_cookie = res.headers['Set-Cookie']
        headers = {"Cookie": redirect_cookie}
        self.Cookie = redirect_cookie


    def getDeliveryFee(self,OrderNo):
        url = 'http://escrow.auction.co.kr/Shipment/Shippingpaymentdetail.aspx'
        headers={
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'ko,en-US;q=0.9,en;q=0.8,fr;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
            'Host':'escrow.auction.co.kr',
            'Upgrade-Insecure-Requests': '1'
        }
        params = {
            'OrderNo':f'{OrderNo}'
        }
        res = self.get(url,params=params)
        print(res.text)
        input('엔터치시라우')
            

    def getimage(self,pdNo):
        url = 'https://www.esmplus.com/Sell/SingleGoodsMng/ImageModify?goodsNo=' + pdNo
        res = self.get(url)
        return res

    def getMainStatus(self):
        url = 'https://www.esmplus.com/Home/MainStatusData'
        headers={'Referer':'https://www.esmplus.com/Sell/Items/ItemsMng?menuCode=TDM100'}
        res = self.get(url,headers=headers).json()
        print(res['IACMainStatusData'])
        return res['IACMainStatusData']


    def getPd1(self, keyword="",page=0,limit=20,StatusCode="", time=10):
        url = 'https://www.esmplus.com/Sell/Items/GetItemMngList?_dc=1630915626578'
        headers = dict()
        headers['Referer'] = 'https://www.esmplus.com/Sell/Items/ItemsMng?menuCode=TDM100'

        data = dict()
        params = dict()
        params["keyword"] = keyword
        params["SiteId"] = "0"
        params["SellType"] = "0"
        params["CategoryCode"] = ""
        params["CustCategoryCode"] = "0"
        params["TransPolicyNo"] = "0"
        params["StatusCode"] = StatusCode
        params["SearchDateType"] = "0"
        params["StartDate"] = ""
        params["EndDate"] = ""
        params["SellerId"] = ""
        params["StockQty"] = "-1"
        params["SellPeriod"] = "0"
        params["DeliveryFeeApplyType"] = "0"
        params["OptAddDeliveryType"] = "0"
        params["SellMinPrice"] = "0"
        params["SellMaxPrice"] = "0"
        params["OptSelUseIs"] = "-1"
        params["PremiumEnd"] = "0"
        params["PremiumPlusEnd"] = "0"
        params["FocusEnd"] = "0"
        params["FocusPlusEnd"] = "0"
        params["GoodsIds"] = ""
        params["SellMngCode"] = ""
        params["OrderByType"] = "11"
        params["NotiItemReg"] = "-1"
        params["EpinMatch"] = "-1"
        params["UserEvaluate"] = ""
        params["SearchClause"] = ""
        params["ScoreRange"] = "0"
        params["ShopCateReg"] = "-1"
        params["IsTPLUse"] = ""
        params["GoodsName"] = ""
        params["SdBrandId"] = "0"
        params["SdBrandName"] = ""
        data['paramsData'] = f"{params}"
        data['page']=page
        data['start']='1'
        data['limit']=limit

        res = self.post(url,data=data,headers=headers, timeout=time).json()
        for no,i in enumerate(res['data']):
            print(no+1,i['GoodsName'])
        print(res['total'])          

    def getPd2(self, keyword="",page=1,limit=20,StatusCode=11, time=10):
        url = 'https://www.esmplus.com/Sell/SingleGoodsMng/GetSingleGoodsList'
        headers = dict()
        headers['Referer'] = 'https://www.esmplus.com/Sell/SingleGoodsMng?menuCode=TDM396'
        data = dict()
        params = dict()
        params["keyword"] = keyword
        params["StatusCode"] = StatusCode # ""전체 / 11:판매가능 / 21:판매중지 / 22:판매불가 / 31:SKU품절 / 01:등록대기
        params["SellPeriod"] = "" # 판매종료
        params["StockQty"] = -1 # 재고 / -1:전체 / 0:재고없음 / 99999:재고있음 / 
        params["SiteId"] = "0"
        params["CategorySiteId"] = "-1"
        params["CategoryCode"] = ""
        params["CategoryLevel"] = ""
        params["TransPolicyNo"] = "0"
        params["SearchDateType"] = "0"
        params["SearchStartDate"] = ""
        params["SearchEndDate"] = ""
        params["SellerId"] = ""
        params["SellerSiteId"] = ""
        params["DiscountUseIs"] = "-1"
        params["DeliveryFeeApplyType"] = "0"
        params["OptAddDeliveryType"] = "0"
        params["OptSelUseIs"] = "-1"
        params["PremiumEnd"] = "0"
        params["PremiumPlusEnd"] = "0"
        params["FocusEnd"] = "0"
        params["FocusPlusEnd"] = "0"
        params["GoodsIdType"] = "S"
        params["GoodsIds"] = ""
        params["ShopCateReg"] = "-1"
        params["IsTPLUse"] = ""
        params["SellMinPrice"] = "0"
        params["SellMaxPrice"] = "0"
        params["OrderByType"] = "11"
        params["GroupOrderByType"] = "1"
        params["IsGroupUse"] = ""
        params["IsApplyEpin"] = ""
        params["IsConvertSingleGoods"] = ""

        data['paramsData'] = f"{params}"
        data['page']=page
        data['start']='1'
        data['limit']=limit
        data['group'] = '[{"property":"SingleGoodsNo","direction":"ASC"}]'

        res = self.post(url,data=data,headers=headers, timeout = time).json()
        print(res['total'])
        for no,i in enumerate(res['data']):
            print(no+1,i['GoodsName'])
        print(res['total'])
        return res


    def getPdAll(self):
        url = 'https://www.esmplus.com/Sell/SingleGoodsMng/GetSingleGoodsList'
        headers = dict()
        headers['Referer'] = 'https://www.esmplus.com/Sell/SingleGoodsMng?menuCode=TDM396'
        data = dict()
        params = dict()
        params["keyword"] = ""
        params["StatusCode"] = "" # ""전체 / 11:판매가능 / 21:판매중지 / 22:판매불가 / 31:SKU품절 / 01:등록대기
        params["SellPeriod"] = "" # 판매종료
        params["StockQty"] = -1 # 재고 / -1:전체 / 0:재고없음 / 99999:재고있음 / 
        params["SiteId"] = "0"
        params["CategorySiteId"] = "-1"
        params["CategoryCode"] = ""
        params["CategoryLevel"] = ""
        params["TransPolicyNo"] = "0"
        params["SearchDateType"] = "0"
        params["SearchStartDate"] = ""
        params["SearchEndDate"] = ""
        params["SellerId"] = ""
        params["SellerSiteId"] = ""
        params["DiscountUseIs"] = "-1"
        params["DeliveryFeeApplyType"] = "0"
        params["OptAddDeliveryType"] = "0"
        params["OptSelUseIs"] = "-1"
        params["PremiumEnd"] = "0"
        params["PremiumPlusEnd"] = "0"
        params["FocusEnd"] = "0"
        params["FocusPlusEnd"] = "0"
        params["GoodsIdType"] = "S"
        params["GoodsIds"] = ""
        params["ShopCateReg"] = "-1"
        params["IsTPLUse"] = ""
        params["SellMinPrice"] = "0"
        params["SellMaxPrice"] = "0"
        params["OrderByType"] = "11"
        params["GroupOrderByType"] = "1"
        params["IsGroupUse"] = ""
        params["IsApplyEpin"] = ""
        params["IsConvertSingleGoods"] = ""

        data['paramsData'] = f"{params}"

        done = False
        page = 0
        while done == False:
            page += 1
            data['page']=page
            data['start']='1'
            data['limit']= 100
            data['group'] = '[{"property":"SingleGoodsNo","direction":"ASC"}]'

            res = self.post(url,data=data,headers=headers, timeout = 10).json()
            return res
            # print(res['total'])
            for no,i in enumerate(res['data']):
                print(no+1 + (page*100),i['GoodsName'])
            print(res['total'])
            
            if len(res['data']) < 100:
                break

    def convertDate(self,now):
        if now != None:
            now = now[6:16]
            _date = datetime.datetime.fromtimestamp(int(now)).strftime('%Y-%m-%d %H:%M:%S')
            return _date
        else:
            return ''

    def makePdTable(self):
        conn = sqlite3.connect('ot.db', isolation_level = None)
        c = conn.cursor()

        # 제품테이블 생성
        sql = '''
        create table product( 
            CategoryCodeIAC text,
            CategoryLNameIAC text,
            CategoryMNameIAC text,
            CategorySNameIAC text,
            DcTypeIAC integer,
            DcValueIAC integer,
            DeliveryFee integer,
            DispEndDate text,
            DispStopDateIAC text,
            GoodsName text,
            ListImgUrl text,
            SDCategoryCode text,
            SDCategoryLevel1Name text,
            SDCategoryLevel2Name text,
            SDCategoryLevel3Name text,
            SDCategoryName text,
            SellerManageCode text,
            SingleGoodsNo text,
            SiteGoodsNoIAC text,
            SiteRegDate text,
            SiteUpdDate text,
            StatusCodeIAC text,
            StockQty integer,
            StockQtyManageYn text,
            TransCloseTimeIac text,
            TransPolicyNameIac text
        );
        '''        
        c.execute(sql)   


    def makePdOldTable(self):
        conn = sqlite3.connect('ot.db', isolation_level = None)
        c = conn.cursor()

        # 제품테이블 생성
        sql = '''
        create table productOld( 
            CategoryLName text,
            CategoryMName text,
            CategorySName text,
            DeliveryFee integer,
            DeliveryFeeApplyType integer,
            DeliveryType integer,
            DispEndDate text,
            DispStartDate text,
            DisplayLimitYn text,
            DupExposeYn text,
            GoodsMasterNo integer,
            GoodsName text,
            GoodsNo text,
            GoodsType integer,
            IacDcValue integer,
            IacDcValueType integer,
            IacPointValue integer,
            IacPointValueType integer,
            InsDate text,
            LastUpd1Date text,
            LastUpd2Date text,
            ListImgUrl text,
            ReadyDurationDay text,
            SellCnt integer,
            SellManageCode text,
            SellPrice integer,
            SellType integer,
            SellerId text,
            SiteCategoryCode text,
            SiteGoodsNo text,
            SiteRegDate text,
            SiteUpdDate text,
            StatusCode text,
            StockQty integer,
            TransCloseTime text,
            TransPolicyName text,
            TransType text
        );
        '''        
        c.execute(sql)  


    def insertDB(self):
        url = 'https://www.esmplus.com/Sell/SingleGoodsMng/GetSingleGoodsList'
        headers = dict()
        headers['Referer'] = 'https://www.esmplus.com/Sell/SingleGoodsMng?menuCode=TDM396'
        data = dict()
        params = dict()
        params["keyword"] = ""
        params["StatusCode"] = "" # ""전체 / 11:판매가능 / 21:판매중지 / 22:판매불가 / 31:SKU품절 / 01:등록대기
        params["SellPeriod"] = "" # 판매종료
        params["StockQty"] = -1 # 재고 / -1:전체 / 0:재고없음 / 99999:재고있음 / 
        params["SiteId"] = "0"
        params["CategorySiteId"] = "-1"
        params["CategoryCode"] = ""
        params["CategoryLevel"] = ""
        params["TransPolicyNo"] = "0"
        params["SearchDateType"] = "0"
        params["SearchStartDate"] = ""
        params["SearchEndDate"] = ""
        params["SellerId"] = ""
        params["SellerSiteId"] = ""
        params["DiscountUseIs"] = "-1"
        params["DeliveryFeeApplyType"] = "0"
        params["OptAddDeliveryType"] = "0"
        params["OptSelUseIs"] = "-1"
        params["PremiumEnd"] = "0"
        params["PremiumPlusEnd"] = "0"
        params["FocusEnd"] = "0"
        params["FocusPlusEnd"] = "0"
        params["GoodsIdType"] = "S"
        params["GoodsIds"] = ""
        params["ShopCateReg"] = "-1"
        params["IsTPLUse"] = ""
        params["SellMinPrice"] = "0"
        params["SellMaxPrice"] = "0"
        params["OrderByType"] = "11"
        params["GroupOrderByType"] = "1"
        params["IsGroupUse"] = ""
        params["IsApplyEpin"] = ""
        params["IsConvertSingleGoods"] = ""

        data['paramsData'] = f"{params}"

        done = False
        page = 0
        
        conn = sqlite3.connect('ot.db', isolation_level = None)
        c = conn.cursor()

        while done == False:
            page += 1
            data['page']=page
            data['start']='1'
            data['limit']= 100
            data['group'] = '[{"property":"SingleGoodsNo","direction":"ASC"}]'

            res = self.post(url,data=data,headers=headers, timeout = 10).json()

            for no,i in enumerate(res['data']):
                DispEndDate = self.convertDate(i['DispEndDate'])
                DispStopDateIAC = self.convertDate(i['DispStopDateIAC'])
                SiteRegDate = self.convertDate(i['SiteRegDate'])
                SiteUpdDate = self.convertDate(i['SiteUpdDate'])
                GoodsName = i['GoodsName'].strip()
                
                if i['SDCategoryLevel2Name'] == None:
                    SDCategoryLevel2Name = ''
                else:
                    SDCategoryLevel2Name = i['SDCategoryLevel2Name']

                if i['SDCategoryLevel3Name'] == None:
                    SDCategoryLevel3Name = ''       
                else:
                    SDCategoryLevel3Name = i['SDCategoryLevel3Name']    

                if i['StockQtyManageYn'] == None:
                    StockQtyManageYn = ''       
                else:
                    StockQtyManageYn = i['StockQtyManageYn']

                print(no+1 + (page*100),i['GoodsName'])
                sql = f'''
                insert into product values( 
                    '{i['CategoryCodeIAC']}',
                    '{i['CategoryLNameIAC']}',
                    '{i['CategoryMNameIAC']}',
                    '{i['CategorySNameIAC']}',
                    {i['DcTypeIAC']},
                    {i['DcValueIAC']},
                    {i['DeliveryFee']},
                    '{DispEndDate}',
                    '{DispStopDateIAC}',
                    '{GoodsName}',
                    '{i['ListImgUrl']}',
                    '{i['SDCategoryCode']}',
                    '{i['SDCategoryLevel1Name']}',
                    '{SDCategoryLevel2Name}',
                    '{SDCategoryLevel3Name}',
                    '{i['SDCategoryName']}',
                    '{i['SellerManageCode']}',
                    '{i['SingleGoodsNo']}',
                    '{i['SiteGoodsNoIAC']}',
                    '{SiteRegDate}',
                    '{SiteUpdDate}',
                    '{i['StatusCodeIAC']}',
                    {i['StockQty']},
                    '{StockQtyManageYn}',
                    '{i['TransCloseTimeIac']}',
                    '{i['TransPolicyNameIac']}'
                );
                '''

                c.execute(sql)                
                



            print(res['total'])
            
            if len(res['data']) < 100:
                break

    def insertProductOld(self):
        url = 'https://www.esmplus.com/Sell/Items/GetItemMngList?_dc=1630915626578'
        headers = dict()
        headers['Referer'] = 'https://www.esmplus.com/Sell/Items/ItemsMng?menuCode=TDM100'

        data = dict()
        params = dict()
        params["keyword"] = ""
        params["SiteId"] = "0"
        params["SellType"] = "0"
        params["CategoryCode"] = ""
        params["CustCategoryCode"] = "0"
        params["TransPolicyNo"] = "0"
        params["StatusCode"] = ""
        params["SearchDateType"] = "0"
        params["StartDate"] = ""
        params["EndDate"] = ""
        params["SellerId"] = ""
        params["StockQty"] = "-1"
        params["SellPeriod"] = "0"
        params["DeliveryFeeApplyType"] = "0"
        params["OptAddDeliveryType"] = "0"
        params["SellMinPrice"] = "0"
        params["SellMaxPrice"] = "0"
        params["OptSelUseIs"] = "-1"
        params["PremiumEnd"] = "0"
        params["PremiumPlusEnd"] = "0"
        params["FocusEnd"] = "0"
        params["FocusPlusEnd"] = "0"
        params["GoodsIds"] = ""
        params["SellMngCode"] = ""
        params["OrderByType"] = "11"
        params["NotiItemReg"] = "-1"
        params["EpinMatch"] = "-1"
        params["UserEvaluate"] = ""
        params["SearchClause"] = ""
        params["ScoreRange"] = "0"
        params["ShopCateReg"] = "-1"
        params["IsTPLUse"] = ""
        params["GoodsName"] = ""
        params["SdBrandId"] = "0"
        params["SdBrandName"] = ""
        data['paramsData'] = f"{params}"

        done = False
        page = 0
        
        conn = sqlite3.connect('ot.db', isolation_level = None)
        c = conn.cursor()
        while done == False:
            page += 1
            data['page']=page
            data['start']='1'
            data['limit']= 100
            data['group'] = '[{"property":"SingleGoodsNo","direction":"ASC"}]'

            res = self.post(url,data=data,headers=headers, timeout = 10).json()

            for no,i in enumerate(res['data']):
                DispEndDate = self.convertDate(i['DispEndDate'])
                DispStartDate = self.convertDate(i['DispStartDate'])
                SiteRegDate = self.convertDate(i['SiteRegDate'])
                SiteUpdDate = self.convertDate(i['SiteUpdDate'])
                InsDate = self.convertDate(i['InsDate'])
                LastUpd1Date = self.convertDate(i['LastUpd1Date'])
                LastUpd2Date = self.convertDate(i['LastUpd2Date'])

                GoodsName = i['GoodsName'].strip()

                print(no+1 + (page*100),i['GoodsName'])
                sql = f'''
                insert into productOld values( 
                    '{i['CategoryLName']}',
                    '{i['CategoryMName']}',
                    '{i['CategorySName']}',
                    {i['DeliveryFee']},
                    {i['DeliveryFeeApplyType']},
                    {i['DeliveryType']},
                    '{DispEndDate}',
                    '{DispStartDate}',
                    
                    '{GoodsName}',
                    '{i['ListImgUrl']}',
                    '{i['SDCategoryCode']}',
                    '{i['SDCategoryLevel1Name']}',
                    '{SDCategoryLevel2Name}',
                    '{SDCategoryLevel3Name}',
                    '{i['SDCategoryName']}',
                    '{i['SellerManageCode']}',
                    '{i['SingleGoodsNo']}',
                    '{i['SiteGoodsNoIAC']}',
                    '{SiteRegDate}',
                    '{SiteUpdDate}',
                    '{i['StatusCodeIAC']}',
                    {i['StockQty']},
                    '{StockQtyManageYn}',
                    '{i['TransCloseTimeIac']}',
                    '{i['TransPolicyNameIac']}'
                );
                '''

                c.execute(sql)                
                



            print(res['total'])
            
            if len(res['data']) < 100:
                break


    def getAllData(self):
        r입금대기 = self.getOrder('입금대기')
        r신규주문 = self.getOrder('신규주문')
        r발송예정 = self.getOrder('발송예정')
        r발송지연 = self.getOrder('발송지연')
        r배송중 = self.getOrder('배송중')
        r배송완료 = self.getOrder('배송완료')
        r정산예정 = self.getOrder('정산예정')
        r정산완료 = self.getOrder('정산완료')
        r취소요청 = self.getOrder('취소요청')
        r반품요청 = self.getOrder('반품요청')
        r교환요청 = self.getOrder('교환요청')
        r미수령신고 = self.getOrder('미수령신고')
        data = [r입금대기,r신규주문,r발송예정,r발송지연,r배송중,r배송완료,r정산예정,r정산완료,r취소요청,r반품요청,r교환요청,r미수령신고]
        print('입금대기:'+ str(r입금대기['total']))
        print('신규주문:'+ str(r신규주문['total']))
        print('발송예정:'+ str(r발송예정['total']))
        print('발송지연:'+ str(r발송지연['total']))
        print('배송중:'+ str(r배송중['total']))
        print('배송완료:'+ str(r배송완료['total']))
        print('정산예정:'+ str(r정산예정['total']))
        print('정산완료:'+ str(r정산완료['total']))
        print('취소요청:'+ str(r취소요청['total']))
        print('반품요청:'+ str(r반품요청['total']))
        print('교환요청:'+ str(r교환요청['total']))            
        print('미수령신고:'+ str(r미수령신고['IacTotalCount']))    
        return data


    def getdate(self):
        now = datetime.now()
        searchEDT = datetime.now()
        searchSDT = now - relativedelta(months=1)
        searchEDT = (searchEDT.strftime('%Y-%m-%d'))
        searchSDT = (searchSDT.strftime('%Y-%m-%d'))
        date = [searchSDT,searchEDT]
        return date


    def getOrder(self,menu):
        date = self.getdate()

        if menu == '배송중':
            url = 'https://www.esmplus.com/Escrow/Delivery/GetSendingSearch'

            headers = {
                'referer' : 'https://www.esmplus.com/Escrow/Delivery/Sending?status=1040&type=N&menuCode=TDM111'
            }
        
            data = {
                'page' : '1',
                'limit' : '100',
                'siteGbn' :'0',
                'searchAccount' : '112611',
                'searchDateType':'DCD',
                'searchSDT':date[0],
                'searchEDT':date[1],
                'searchKey':'ON',
                'searchKeyword':'',
                'searchType':'1040',
                'excelInfo':'undefined',
                'searchStatus':'1040',
                'searchAllYn':'N',
                'SortFeild':'PayDate',
                'SortType':'Desc',
                'start':'0',
                'searchDistrType':'AL',
            }


        elif menu == '입금대기':
            url = 'https://www.esmplus.com/Escrow/Order/ReceiptCheckSearch'
            headers = {
                'referer' : 'https://www.esmplus.com/Escrow/Order/ReceiptCheck?type=N&menuCode=TDM104'
            }    
            data = {
                'page' : '1',
                'limit' : '50',
                'tabeGbn' :'1',
                'searchAccount' : 'TA',
                'searchDateType':'ORD',
                'searchSDT':date[0],
                'searchEDT':date[1],
                'searchKey':'ON',
                'searchKeyword':'',
                'searchDistrType':'AL',
                'searchAllYn':'N',
                'SortFeild':'OrderDate',
                'SortType':'Desc',
                'start':'0'
            }        

        elif menu == '신규주문':
            url = 'https://www.esmplus.com/Escrow/Order/NewOrderSearch'
            headers = {
                'referer' : 'https://www.esmplus.com/Escrow/Order/NewOrder?menuCode=TDM105'
            }    
            data = {
                'page' : '1',
                'limit' : '50',
                'siteGbn' :'0',
                'searchAccount' : '112611',
                'searchDateType':'ODD',
                'searchSDT':date[0],
                'searchEDT':date[1],
                'searchKey':'ON',
                'searchKeyword':'',
                'searchAllYn':'Y',
                'SortFeild':'PayDate',
                'SortType':'Desc',
                'start':'0',
                'searchDistrType':'AL',
                'searchTransPolicyType':''
            }
    
        elif menu == '발송예정':
            url = 'https://www.esmplus.com/Escrow/Delivery/GeneralDeliverySearch'
            headers = {'referer' : 'https://www.esmplus.com/Escrow/Delivery/GeneralDelivery?gbn=0&status=0&type=&searchAccount=&searchDateType=&searchSDT=&searchEDT=&searchKey=&searchKeyword=&searchDeliveryType=&searchOrderType=&searchPacking=&totalAccumulate=-&searchTransPolicyType='}
            data = {
                'page' : '1',
                'limit' : '50',
                'siteGbn' :'0',
                'searchAccount' : '112611',
                'searchDateType':'ODD',
                'searchSDT':date[0],
                'searchEDT':date[1],
                'searchKey':'ON',
                'searchKeyword':'',
                'excelInfo':'',
                'searchStatus':'0',
                'searchAllYn':'Y',
                'SortFeild':'PayDate',
                'SortType':'Desc',
                'start':'0',
                'searchOrderType':'',
                'searchDeliveryType':'',
                'searchPaking':'false',
                'searchDistrType':'AL',
                'searchTransPolicyType':''
            }
    
        elif menu == '발송지연':
            url = 'https://www.esmplus.com/Escrow/Delivery/GeneralDeliverySearch'
            headers = {'referer' : 'https://www.esmplus.com/Escrow/Delivery/GeneralDelivery?gbn=0&status=0&type=&searchAccount=112611&searchDateType=ODD&searchSDT=2021-06-06&searchEDT=2021-09-06&searchKey=ON&searchKeyword=&searchDeliveryType=&searchOrderType=C&searchPacking=false&totalAccumulate=-&listAllView=false&searchDistrType=AL&searchTransPolicyType='}
    
            data = {
                'page' : '1',
                'limit' : '50',
                'siteGbn' :'0',
                'searchAccount' : '112611',
                'searchDateType':'ODD',
                'searchSDT':date[0],
                'searchEDT':date[1],
                'searchKey':'ON',
                'searchKeyword':'',
                'excelInfo':'',
                'searchStatus':'0',
                'searchAllYn':'Y',
                'SortFeild':'PayDate',
                'SortType':'Desc',
                'start':'0',
                'searchOrderType':'C',
                'searchDeliveryType':'',
                'searchPaking':'false',
                'searchDistrType':'AL',
                'searchTransPolicyType':''
            }    
        
    
        elif menu == '배송완료':
            url = 'https://www.esmplus.com/Escrow/Delivery/GetSendingSearch'
            headers = {'referer':'https://www.esmplus.com/Escrow/Delivery/BuyDecision?status=1060&type=N&menuCode=TDM112'}
            data = {
                'page' : '1',
                'limit' : '100',
                'siteGbn' :'0',
                'searchAccount' : '112611',
                'searchDateType':'DCD',
                'searchSDT':date[0],
                'searchEDT':date[1],
                'searchKey':'ON',
                'searchKeyword':'',
                'searchType':'1050',
                'excelInfo':'undefined',
                'searchStatus':'1050',
                'searchAllYn':'N',
                'SortFeild':'PayDate',
                'SortType':'Desc',
                'start':'0',
                'searchDistrType':'AL'
            }

        elif menu == '정산예정':
            url = 'https://www.esmplus.com/Escrow/Delivery/BuyDecisionSearch'
            headers = {
                'referer' : 'https://www.esmplus.com/Escrow/Delivery/BuyDecision?status=1060&type=N&menuCode=TDM112'
            }
    
            data = {
                'page' : '1',
                'limit' : '100',
                'siteGbn' :'0',
                'searchAccount' : '112611',
                'searchDateType':'TRD',
                'searchSDT':date[0],
                'searchEDT':date[1],
                'searchKey':'ON',
                'searchKeyword':'',
                'searchStatus':'1060',
                'searchAllYn':'N',
                'SortFeild':'TransDate',
                'SortType':'Desc',
                'start':'0',
                'searchDistrType':'AL'
            }

        elif menu == '정산완료':
            url = 'https://www.esmplus.com/Escrow/Delivery/BuyDecisionSearch'
            headers = {
                'referer' : 'https://www.esmplus.com/Escrow/Delivery/BuyDecision?gbn=0&status=5010&type=N&searchTotal=-&searchAccount=112611&searchDateType=TRD&searchSDT=2021-08-06&searchEDT=2021-09-06&searchKey=ON&searchKeyword=&searchStatus=5010&listAllView=false&searchDistrType=AL&searchGlobalShopType=&searchOverseaDeliveryYn='
            }
    
            data = {
                'page' : '1',
                'limit' : '200',
                'siteGbn' :'0',
                'searchAccount' : '112611',
                'searchDateType':'TRD',
                'searchSDT':date[0],
                'searchEDT':date[1],
                'searchKey':'ON',
                'searchKeyword':'',
                'searchStatus':'5010',
                'searchAllYn':'N',
                'SortFeild':'TransDate',
                'SortType':'Desc',
                'start':'0',
                'searchDistrType':'AL'
            }

        elif menu == '취소요청':
            url = 'https://www.esmplus.com/Escrow/Claim/CancelManagementSearch'
            headers = {
                'referer' : 'https://www.esmplus.com/Escrow/Claim/CancelRequestManagement?menuCode=TDM115'
            }
    
            data = {
                'page' : '1',
                'limit' : '20',
                'siteGbn' :'1',
                'searchAccount' : 'TA',
                'searchDateType':'ODD',
                'searchSDT':date[0],
                'searchEDT':date[1],
                'searchType':'CR',
                'searchKey':'ON',
                'searchKeyword':'',
                'orderByType':'',
                'excelInfo':'',
                'searchStatus':'CR',
                'searchAllYn':'N',
                'tabGbn':'1',
                'SortFeild':'PayDate',
                'SortType':'Desc',
                'start':'0',
                'searchDistrType':'AL'
            }


        elif menu == '반품요청':
            url = 'https://www.esmplus.com/Escrow/Claim/ReturnManagementSearch'
            headers = {
                'referer' : 'https://www.esmplus.com/Escrow/Claim/ReturnRequestManagement?tab=1&status=RR&from=MAIN&menuCode=TDM118'
            }
    
            data = {
                'page' : '1',
                'limit' : '20',
                'siteGbn' :'1',
                'searchAccount' : 'TA^112611',
                'searchDateType':'DCD',
                'searchSDT':date[0],
                'searchEDT':date[1],
                'searchType':'RR',
                'searchKey':'ON',
                'searchKeyword':'',
                'orderByType':'',
                'excelInfo':'',
                'searchStatus':'RR',
                'searchAllYn':'Y',
                'tabGbn':'1',
                'SortFeild':'PayDate',
                'SortType':'Desc',
                'start':'0',
                'searchDistrType':'AL',
                'searchRewardStatus':'NN',
                'searchFastRefundYn':''
            }

        elif menu == '교환요청':
            url = 'https://www.esmplus.com/Escrow/Claim/ExchangeManagementSearch'
            headers = {
                'referer' : 'https://www.esmplus.com/Escrow/Claim/ExchangeRequestManagement?from=MAIN&menuCode=TDM123'
            }
    
            data = {
                'page' : '1',
                'limit' : '20',
                'siteGbn' :'1',
                'searchAccount' : 'TA^112611',
                'searchDateType':'DCD',
                'searchSDT':date[0],
                'searchEDT':date[1],
                'searchType':'',
                'searchKey':'ON',
                'searchKeyword':'',
                'orderByType':'',
                'excelInfo':'',
                'searchStatus':'',
                'searchAllYn':'Y',
                'tabGbn':'1',
                'SortFeild':'PayDate',
                'SortType':'Desc',
                'claimCount':'-',
                'start':'0',
                'searchDistrType':'AL'
            }

        elif menu == '미수령신고':
            url = 'https://www.esmplus.com/Escrow/Delivery/GetSendingSearchCount'
            headers = {
                'referer' : 'https://www.esmplus.com/Escrow/Delivery/Sending?status=7010&type=N&menuCode=TDM111'
            }
    
            data = {
                'siteGbn' :'0',
                'searchAccount' : '112611',
                'searchDateType':'DCD',
                'searchSDT':date[0],
                'searchEDT':date[1],
                'searchKey':'ON',
                'searchKeyword':'',
                'searchType':'7010',
                'excelInfo':'undefined',
                'searchStatus':'7010',
                'searchAllYn':'N',
                'SortFeild':'PayDate',
                'SortType':'Desc',
                'start':'0',
                'page': '1',
                'limit':'10000000',
                'searchDistrType':'AL'
            }

        res = self.post(url, data = data, headers=headers).json()
        return res
    

    # # HTML태그 없애는 함수
    def remove_tag(self,content):
        cleanr =re.compile('<.*?>')
        try:
            cleantext = re.sub(cleanr, '', content)
            return cleantext
        except:
            pass

    def orderViewSimple(self,res,menu):
        ACTotalPrice = 0
        ACTotalSttlExpectedAmnt = 0        
        orderCount = res['total']
        print(f'\n옥션 [ {menu} ] : {str(orderCount)}건')
        if orderCount != 0:
            no = 1
            for i in res['data']:
                print(f'옥션 {menu} No.{no}   ' + '=='*60)            
                OrderNo = i['OrderNo']
                SiteID = self.remove_tag(i['SiteID'])
                SiteIDValue = i['SiteIDValue']
                SellerCustNo = i['SellerCustNo']
                SellerID = i['SellerID']
                SiteOrderNo = i['SiteOrderNo']
                GoodsNo = i['GoodsNo']
                GoodsName = self.remove_tag(i['GoodsName'])
                PayExpireDate = i['PayExpireDate']
                PayDate = i['PayDate']
                TransScheduledDate = i['TransScheduledDate']
                TransDate = i['TransDate']
                DeliveryFinishDate = i['DeliveryFinishDate']
                BuyDecisionDate = i['BuyDecisionDate']
                TransNo = i['TransNo']
                DeliveryFeeType = i['DeliveryFeeType']
                DeliveryFee = self.remove_tag(i['DeliveryFee'])
                DeliveryComp = i['DeliveryComp']
                DeliveryCompNm = i['DeliveryCompNm']
                InvoiceNo = self.remove_tag(i['InvoiceNo'])
                BuyerID = i['BuyerID']
                BuyerName = i['BuyerName']
                OrderAmnt = i['OrderAmnt']
                TradeAmnt = i['TradeAmnt']
                OrderQty = i['OrderQty']
                SelOption = self.remove_tag(i['SelOption'])
                AddOption = self.remove_tag(i['AddOption'])
                RcverName = i['RcverName']
                RcverInfoCp = i['RcverInfoCp']
                RcverInfoHt = i['RcverInfoHt']
                ZipCode = i['ZipCode']
                RcverInfoAd = self.remove_tag(i['RcverInfoAd'])
                DeliveryMemo = self.remove_tag(i['DeliveryMemo'])
                CartNo = i['CartNo']
                CartNoStr = i['CartNoStr']
                TransScheduledReason = i['TransScheduledReason']
                FreeGift = i['FreeGift']
                FreeGiftCode = i['FreeGiftCode']
                Bonus = i['Bonus']
                BonusCode = i['BonusCode']
                DeliveryWay = i['DeliveryWay']
                GatherPlace = i['GatherPlace']
                GoodsSizeDesc = i['GoodsSizeDesc']
                PackingQty = i['PackingQty']
                DeliveryStatus = i['DeliveryStatus']
                SettleStatus = i['SettleStatus']
                ClaimDate = i['ClaimDate']
                ClaimReason = i['ClaimReason']
                ClaimDetailReason = i['ClaimDetailReason']
                ClaimRequestDate = i['ClaimRequestDate']
                ClaimObjctnDate = i['ClaimObjctnDate']
                BuyerCp = i['BuyerCp']
                BuyerHt = i['BuyerHt']
                SellerMngCode = self.remove_tag(i['SellerMngCode'])
                SellerDetailMngCode = self.remove_tag(i['SellerDetailMngCode'])
                PayWayCode = i['PayWayCode']
                RcverInfoPacking = i['RcverInfoPacking']
                LabelPrintDate = i['LabelPrintDate']
                OrderDate = i['OrderDate']
                OrderConfirmDate = i['OrderConfirmDate']
                DepositConfirmDate = i['DepositConfirmDate']
                SttlExpectedAmnt = i['SttlExpectedAmnt']
                SellerCouponDcAmnt = i['SellerCouponDcAmnt']
                SellerPointDcAmnt = i['SellerPointDcAmnt']
                SinglePayDcAmnt = i['SinglePayDcAmnt']
                MultiBuyDcAmnt = i['MultiBuyDcAmnt']
                GreatMembDcAmnt = i['GreatMembDcAmnt']
                GatherPlaceNo = i['GatherPlaceNo']
                GatherPlaceName = i['GatherPlaceName']
                SellerBcashSaveAmnt = i['SellerBcashSaveAmnt']
                DeliveryTypeCode = i['DeliveryTypeCode']
                trStyle = i['trStyle']
                PackingCount = i['PackingCount']
                MarketType = i['MarketType']
                SettleFinishDate = i['SettleFinishDate']
                SupplyPrice = i['SupplyPrice']
                SendProcessGbn = i['SendProcessGbn']
                ReDate = i['ReDate']
                ReInvoiceNo = i['ReInvoiceNo']
                ReRcverInfoAd = i['ReRcverInfoAd']
                ReZipCode = i['ReZipCode']
                SellPrice = i['SellPrice']
                ServiceUseAmnt = i['ServiceUseAmnt']
                GepLabelPrintDate = i['GepLabelPrintDate']
                ReCompName = i['ReCompName']
                BuyerDCAmnt = i['BuyerDCAmnt']
                RedeliveryStatus = i['RedeliveryStatus']
                ReceiverSSN = i['ReceiverSSN']
                DistrType = i['DistrType']
                SkuString = self.remove_tag(i['SkuString'])
                SkuStringNoFormat = i['SkuStringNoFormat']
                DeliveryStatusCode = i['DeliveryStatusCode']
                ReceiverEntryNo = i['ReceiverEntryNo']
                GlobalShopType = i['GlobalShopType']
                OverseaDeliveryYN = i['OverseaDeliveryYN']
                ShopTypeName = i['ShopTypeName']
                PartnerName = i['PartnerName']
                SellerSmileCashAmnt = i['SellerSmileCashAmnt']
                TransDueStatus = i['TransDueStatus']
                TransDueDate = i['TransDueDate']
                TransType = i['TransType']
                TotalCnt = i['TotalCnt']

                '''
                10005 / 우체국택배
                10003 / 로젠택배
                10014 / 대신택배
                10016 / 경동택배
                '''

                if DeliveryComp == 10005:
                    DeliveryCompNm = '우체국택배'
                elif DeliveryComp == 10003:
                    DeliveryCompNm = '로젠택배'
                elif DeliveryComp == 10014:
                    DeliveryCompNm = '대신택배'
                elif DeliveryComp == 10016:
                    DeliveryCompNm = '경동택배'
                
                # 택배비 가져오기 / 오류남
                # ac.getDeliveryFee(OrderNo)


                print('OrderNo: ', OrderNo)
                # print('SiteID: ', SiteID)
                # print('SiteIDValue: ', SiteIDValue)
                # print('SellerCustNo: ', SellerCustNo)
                # print('SellerID: ', SellerID)
                # print('SiteOrderNo: ', SiteOrderNo)
                print('GoodsNo: ', GoodsNo)
                print('GoodsName: ', GoodsName)
                # print('PayExpireDate: ', PayExpireDate)
                # print('PayDate: ', PayDate)
                # print('TransScheduledDate: ', TransScheduledDate)
                # print('TransDate: ', TransDate)
                # print('DeliveryFinishDate: ', DeliveryFinishDate)
                # print('BuyDecisionDate: ', BuyDecisionDate)
                # print('TransNo: ', TransNo)
                print('DeliveryFeeType: ', DeliveryFeeType)
                print('DeliveryFee: ', DeliveryFee)
                # print('DeliveryComp: ', DeliveryComp)
                print('DeliveryCompNm: ', DeliveryCompNm)
                # print('InvoiceNo: ', InvoiceNo)
                # print('BuyerID: ', BuyerID)
                print('BuyerName: ', BuyerName)
                print('OrderAmnt: ', OrderAmnt)
                # print('TradeAmnt: ', TradeAmnt)
                print('OrderQty: ', OrderQty)
                # print('SelOption: ', SelOption)
                # print('AddOption: ', AddOption)
                print('RcverName: ', RcverName)
                print('RcverInfoCp: ', RcverInfoCp)
                print('RcverInfoHt: ', RcverInfoHt)
                print('ZipCode: ', ZipCode)
                print('RcverInfoAd: ', RcverInfoAd)
                print('DeliveryMemo: ', DeliveryMemo)
                # print('CartNo: ', CartNo)
                # print('CartNoStr: ', CartNoStr)
                # print('TransScheduledReason: ', TransScheduledReason)
                # print('FreeGift: ', FreeGift)
                # print('FreeGiftCode: ', FreeGiftCode)
                # print('Bonus: ', Bonus)
                # print('BonusCode: ', BonusCode)
                # print('DeliveryWay: ', DeliveryWay)
                # print('GatherPlace: ', GatherPlace)
                # print('GoodsSizeDesc: ', GoodsSizeDesc)
                # print('PackingQty: ', PackingQty)
                # print('DeliveryStatus: ', DeliveryStatus)
                # print('SettleStatus: ', SettleStatus)
                # print('ClaimDate: ', ClaimDate)
                # print('ClaimReason: ', ClaimReason)
                # print('ClaimDetailReason: ', ClaimDetailReason)
                # print('ClaimRequestDate: ', ClaimRequestDate)
                # print('ClaimObjctnDate: ', ClaimObjctnDate)
                # print('BuyerCp: ', BuyerCp)
                # print('BuyerHt: ', BuyerHt)
                # print('SellerMngCode: ', SellerMngCode)
                # print('SellerDetailMngCode: ', SellerDetailMngCode)
                # print('PayWayCode: ', PayWayCode)
                # print('RcverInfoPacking: ', RcverInfoPacking)
                # print('LabelPrintDate: ', LabelPrintDate)
                # print('OrderDate: ', OrderDate)
                # print('OrderConfirmDate: ', OrderConfirmDate)
                # print('DepositConfirmDate: ', DepositConfirmDate)
                print('SttlExpectedAmnt: ', SttlExpectedAmnt)
                print('SellerCouponDcAmnt: ', SellerCouponDcAmnt)
                # print('SellerPointDcAmnt: ', SellerPointDcAmnt)
                # print('SinglePayDcAmnt: ', SinglePayDcAmnt)
                # print('MultiBuyDcAmnt: ', MultiBuyDcAmnt)
                # print('GreatMembDcAmnt: ', GreatMembDcAmnt)
                # print('GatherPlaceNo: ', GatherPlaceNo)
                # print('GatherPlaceName: ', GatherPlaceName)
                # print('SellerBcashSaveAmnt: ', SellerBcashSaveAmnt)
                # print('DeliveryTypeCode: ', DeliveryTypeCode)
                # print('trStyle: ', trStyle)
                # print('PackingCount: ', PackingCount)
                # print('MarketType: ', MarketType)
                # print('SettleFinishDate: ', SettleFinishDate)
                # print('SupplyPrice: ', SupplyPrice)
                # print('SendProcessGbn: ', SendProcessGbn)
                # print('ReDate: ', ReDate)
                # print('ReInvoiceNo: ', ReInvoiceNo)
                # print('ReRcverInfoAd: ', ReRcverInfoAd)
                # print('ReZipCode: ', ReZipCode)
                print('SellPrice: ', SellPrice)
                print('ServiceUseAmnt: ', ServiceUseAmnt)
                # print('GepLabelPrintDate: ', GepLabelPrintDate)
                # print('ReCompName: ', ReCompName)
                # print('BuyerDCAmnt: ', BuyerDCAmnt)
                # print('RedeliveryStatus: ', RedeliveryStatus)
                # print('ReceiverSSN: ', ReceiverSSN)
                # print('DistrType: ', DistrType)
                # print('SkuString: ', SkuString)
                # print('SkuStringNoFormat: ', SkuStringNoFormat)
                # print('DeliveryStatusCode: ', DeliveryStatusCode)
                # print('ReceiverEntryNo: ', ReceiverEntryNo)
                # print('GlobalShopType: ', GlobalShopType)
                # print('OverseaDeliveryYN: ', OverseaDeliveryYN)
                # print('ShopTypeName: ', ShopTypeName)
                # print('PartnerName: ', PartnerName)
                # print('SellerSmileCashAmnt: ', SellerSmileCashAmnt)
                # print('TransDueStatus: ', TransDueStatus)
                # print('TransDueDate: ', TransDueDate)
                # print('TransType: ', TransType)
                # print('TotalCnt: ', TotalCnt)
                print('\n')


                if menu != '입금대기':
                    ACTotalPrice += int(OrderAmnt.replace(',',''))
                    ACTotalSttlExpectedAmnt += int(SttlExpectedAmnt.replace(',',''))
                no += 1
            
        if orderCount != 0:
            print(f'-총주문합계금액: {ACTotalPrice}')
            print(f'-총정산예정금액: {ACTotalSttlExpectedAmnt}')


    def orderViewfull(self,res,menu):
        ACTotalPrice = 0
        ACTotalSttlExpectedAmnt = 0        
        orderCount = res['total']
        print('\n\n')
        print(f'[ {menu} ] : {str(orderCount)}건')
        if orderCount != 0:
            no = 1
            for i in res['data']:
                print(f'옥션 {menu} No.{no}   ' + '=='*60)            
                OrderNo = i['OrderNo']
                SiteID = self.remove_tag(i['SiteID'])
                SiteIDValue = i['SiteIDValue']
                SellerCustNo = i['SellerCustNo']
                SellerID = i['SellerID']
                SiteOrderNo = i['SiteOrderNo']
                GoodsNo = i['GoodsNo']
                GoodsName = self.remove_tag(i['GoodsName'])
                PayExpireDate = i['PayExpireDate']
                PayDate = i['PayDate']
                TransScheduledDate = i['TransScheduledDate']
                TransDate = i['TransDate']
                DeliveryFinishDate = i['DeliveryFinishDate']
                BuyDecisionDate = i['BuyDecisionDate']
                TransNo = i['TransNo']
                DeliveryFeeType = i['DeliveryFeeType']
                DeliveryFee = self.remove_tag(i['DeliveryFee'])
                DeliveryComp = i['DeliveryComp']
                DeliveryCompNm = i['DeliveryCompNm']
                InvoiceNo = self.remove_tag(i['InvoiceNo'])
                BuyerID = i['BuyerID']
                BuyerName = i['BuyerName']
                OrderAmnt = i['OrderAmnt']
                TradeAmnt = i['TradeAmnt']
                OrderQty = i['OrderQty']
                SelOption = self.remove_tag(i['SelOption'])
                AddOption = self.remove_tag(i['AddOption'])
                RcverName = i['RcverName']
                RcverInfoCp = i['RcverInfoCp']
                RcverInfoHt = i['RcverInfoHt']
                ZipCode = i['ZipCode']
                RcverInfoAd = self.remove_tag(i['RcverInfoAd'])
                DeliveryMemo = self.remove_tag(i['DeliveryMemo'])
                CartNo = i['CartNo']
                CartNoStr = i['CartNoStr']
                TransScheduledReason = i['TransScheduledReason']
                FreeGift = i['FreeGift']
                FreeGiftCode = i['FreeGiftCode']
                Bonus = i['Bonus']
                BonusCode = i['BonusCode']
                DeliveryWay = i['DeliveryWay']
                GatherPlace = i['GatherPlace']
                GoodsSizeDesc = i['GoodsSizeDesc']
                PackingQty = i['PackingQty']
                DeliveryStatus = i['DeliveryStatus']
                SettleStatus = i['SettleStatus']
                ClaimDate = i['ClaimDate']
                ClaimReason = i['ClaimReason']
                ClaimDetailReason = i['ClaimDetailReason']
                ClaimRequestDate = i['ClaimRequestDate']
                ClaimObjctnDate = i['ClaimObjctnDate']
                BuyerCp = i['BuyerCp']
                BuyerHt = i['BuyerHt']
                SellerMngCode = self.remove_tag(i['SellerMngCode'])
                SellerDetailMngCode = self.remove_tag(i['SellerDetailMngCode'])
                PayWayCode = i['PayWayCode']
                RcverInfoPacking = i['RcverInfoPacking']
                LabelPrintDate = i['LabelPrintDate']
                OrderDate = i['OrderDate']
                OrderConfirmDate = i['OrderConfirmDate']
                DepositConfirmDate = i['DepositConfirmDate']
                SttlExpectedAmnt = i['SttlExpectedAmnt']
                SellerCouponDcAmnt = i['SellerCouponDcAmnt']
                SellerPointDcAmnt = i['SellerPointDcAmnt']
                SinglePayDcAmnt = i['SinglePayDcAmnt']
                MultiBuyDcAmnt = i['MultiBuyDcAmnt']
                GreatMembDcAmnt = i['GreatMembDcAmnt']
                GatherPlaceNo = i['GatherPlaceNo']
                GatherPlaceName = i['GatherPlaceName']
                SellerBcashSaveAmnt = i['SellerBcashSaveAmnt']
                DeliveryTypeCode = i['DeliveryTypeCode']
                trStyle = i['trStyle']
                PackingCount = i['PackingCount']
                MarketType = i['MarketType']
                SettleFinishDate = i['SettleFinishDate']
                SupplyPrice = i['SupplyPrice']
                SendProcessGbn = i['SendProcessGbn']
                ReDate = i['ReDate']
                ReInvoiceNo = i['ReInvoiceNo']
                ReRcverInfoAd = i['ReRcverInfoAd']
                ReZipCode = i['ReZipCode']
                SellPrice = i['SellPrice']
                ServiceUseAmnt = i['ServiceUseAmnt']
                GepLabelPrintDate = i['GepLabelPrintDate']
                ReCompName = i['ReCompName']
                BuyerDCAmnt = i['BuyerDCAmnt']
                RedeliveryStatus = i['RedeliveryStatus']
                ReceiverSSN = i['ReceiverSSN']
                DistrType = i['DistrType']
                SkuString = self.remove_tag(i['SkuString'])
                SkuStringNoFormat = i['SkuStringNoFormat']
                DeliveryStatusCode = i['DeliveryStatusCode']
                ReceiverEntryNo = i['ReceiverEntryNo']
                GlobalShopType = i['GlobalShopType']
                OverseaDeliveryYN = i['OverseaDeliveryYN']
                ShopTypeName = i['ShopTypeName']
                PartnerName = i['PartnerName']
                SellerSmileCashAmnt = i['SellerSmileCashAmnt']
                TransDueStatus = i['TransDueStatus']
                TransDueDate = i['TransDueDate']
                TransType = i['TransType']
                TotalCnt = i['TotalCnt']

                '''
                10005 / 우체국택배
                10003 / 로젠택배
                10014 / 대신택배
                10016 / 경동택배
                '''

                if DeliveryComp == 10005:
                    DeliveryCompNm = '우체국택배'
                elif DeliveryComp == 10003:
                    DeliveryCompNm = '로젠택배'
                elif DeliveryComp == 10014:
                    DeliveryCompNm = '대신택배'
                elif DeliveryComp == 10016:
                    DeliveryCompNm = '경동택배'
                
                # 택배비 가져오기 / 오류남
                # ac.getDeliveryFee(OrderNo)


                print('OrderNo: ', OrderNo)
                print('SiteID: ', SiteID)
                print('SiteIDValue: ', SiteIDValue)
                print('SellerCustNo: ', SellerCustNo)
                print('SellerID: ', SellerID)
                print('SiteOrderNo: ', SiteOrderNo)
                print('GoodsNo: ', GoodsNo)
                print('GoodsName: ', GoodsName)
                print('PayExpireDate: ', PayExpireDate)
                print('PayDate: ', PayDate)
                print('TransScheduledDate: ', TransScheduledDate)
                print('TransDate: ', TransDate)
                print('DeliveryFinishDate: ', DeliveryFinishDate)
                print('BuyDecisionDate: ', BuyDecisionDate)
                print('TransNo: ', TransNo)
                print('DeliveryFeeType: ', DeliveryFeeType)
                print('DeliveryFee: ', DeliveryFee)
                print('DeliveryComp: ', DeliveryComp)
                print('DeliveryCompNm: ', DeliveryCompNm)
                print('InvoiceNo: ', InvoiceNo)
                print('BuyerID: ', BuyerID)
                print('BuyerName: ', BuyerName)
                print('OrderAmnt: ', OrderAmnt)
                print('TradeAmnt: ', TradeAmnt)
                print('OrderQty: ', OrderQty)
                print('SelOption: ', SelOption)
                print('AddOption: ', AddOption)
                print('RcverName: ', RcverName)
                print('RcverInfoCp: ', RcverInfoCp)
                print('RcverInfoHt: ', RcverInfoHt)
                print('ZipCode: ', ZipCode)
                print('RcverInfoAd: ', RcverInfoAd)
                print('DeliveryMemo: ', DeliveryMemo)
                print('CartNo: ', CartNo)
                print('CartNoStr: ', CartNoStr)
                print('TransScheduledReason: ', TransScheduledReason)
                print('FreeGift: ', FreeGift)
                print('FreeGiftCode: ', FreeGiftCode)
                print('Bonus: ', Bonus)
                print('BonusCode: ', BonusCode)
                print('DeliveryWay: ', DeliveryWay)
                print('GatherPlace: ', GatherPlace)
                print('GoodsSizeDesc: ', GoodsSizeDesc)
                print('PackingQty: ', PackingQty)
                print('DeliveryStatus: ', DeliveryStatus)
                print('SettleStatus: ', SettleStatus)
                print('ClaimDate: ', ClaimDate)
                print('ClaimReason: ', ClaimReason)
                print('ClaimDetailReason: ', ClaimDetailReason)
                print('ClaimRequestDate: ', ClaimRequestDate)
                print('ClaimObjctnDate: ', ClaimObjctnDate)
                print('BuyerCp: ', BuyerCp)
                print('BuyerHt: ', BuyerHt)
                print('SellerMngCode: ', SellerMngCode)
                print('SellerDetailMngCode: ', SellerDetailMngCode)
                print('PayWayCode: ', PayWayCode)
                print('RcverInfoPacking: ', RcverInfoPacking)
                print('LabelPrintDate: ', LabelPrintDate)
                print('OrderDate: ', OrderDate)
                print('OrderConfirmDate: ', OrderConfirmDate)
                print('DepositConfirmDate: ', DepositConfirmDate)
                print('SttlExpectedAmnt: ', SttlExpectedAmnt)
                print('SellerCouponDcAmnt: ', SellerCouponDcAmnt)
                print('SellerPointDcAmnt: ', SellerPointDcAmnt)
                print('SinglePayDcAmnt: ', SinglePayDcAmnt)
                print('MultiBuyDcAmnt: ', MultiBuyDcAmnt)
                print('GreatMembDcAmnt: ', GreatMembDcAmnt)
                print('GatherPlaceNo: ', GatherPlaceNo)
                print('GatherPlaceName: ', GatherPlaceName)
                print('SellerBcashSaveAmnt: ', SellerBcashSaveAmnt)
                print('DeliveryTypeCode: ', DeliveryTypeCode)
                print('trStyle: ', trStyle)
                print('PackingCount: ', PackingCount)
                print('MarketType: ', MarketType)
                print('SettleFinishDate: ', SettleFinishDate)
                print('SupplyPrice: ', SupplyPrice)
                print('SendProcessGbn: ', SendProcessGbn)
                print('ReDate: ', ReDate)
                print('ReInvoiceNo: ', ReInvoiceNo)
                print('ReRcverInfoAd: ', ReRcverInfoAd)
                print('ReZipCode: ', ReZipCode)
                print('SellPrice: ', SellPrice)
                print('ServiceUseAmnt: ', ServiceUseAmnt)
                print('GepLabelPrintDate: ', GepLabelPrintDate)
                print('ReCompName: ', ReCompName)
                print('BuyerDCAmnt: ', BuyerDCAmnt)
                print('RedeliveryStatus: ', RedeliveryStatus)
                print('ReceiverSSN: ', ReceiverSSN)
                print('DistrType: ', DistrType)
                print('SkuString: ', SkuString)
                print('SkuStringNoFormat: ', SkuStringNoFormat)
                print('DeliveryStatusCode: ', DeliveryStatusCode)
                print('ReceiverEntryNo: ', ReceiverEntryNo)
                print('GlobalShopType: ', GlobalShopType)
                print('OverseaDeliveryYN: ', OverseaDeliveryYN)
                print('ShopTypeName: ', ShopTypeName)
                print('PartnerName: ', PartnerName)
                print('SellerSmileCashAmnt: ', SellerSmileCashAmnt)
                print('TransDueStatus: ', TransDueStatus)
                print('TransDueDate: ', TransDueDate)
                print('TransType: ', TransType)
                print('TotalCnt: ', TotalCnt)
                print('\n')


                if menu != '입금대기':
                    ACTotalPrice += int(OrderAmnt.replace(',',''))
                    ACTotalSttlExpectedAmnt += int(SttlExpectedAmnt.replace(',',''))
                
                no += 1

        if orderCount != 0:
            print(f'-총주문합계금액: {ACTotalPrice}')
            print(f'-총정산예정금액: {ACTotalSttlExpectedAmnt}')       

########################### 쿠팡 클래스 #################################

class Coupang(Session):
    def __init__(self) -> None:
        super().__init__()

        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def login(self,id,pw):
        # id = "rmfrmffla"
        cid = f'VENDOR,{id}'
        # pw = 'qw970104@'

        data = {
            'username': cid,
            'password': pw,
        }        
        res = self.post('https://wing.coupang.com/login', data=data, headers=self.headers)
        res = self.get('https://wing.coupang.com/', headers=self.headers)
        redirect_cookie = res.headers['Set-Cookie']
        headers = {"Cookie": redirect_cookie}
    
    def getOrder(self,menu):
        # 쿠팡 주문(결제/배송)내역
        today = datetime.today().strftime("%Y-%m-%d")
        endDate = today
        sDate = datetime.today() - timedelta(30)
        startDate = sDate.strftime("%Y-%m-%d")

        deliveryStatus = menu.upper()
        countPerPage = 50
        page = 1
        url = 'https://wing.coupang.com/tenants/sfl-portal/delivery/management/dashboard/search?condition='
        param = f'{{"nextShipmentBoxId":null,"startDate":"{startDate}","endDate":"{endDate}","deliveryStatus":"{deliveryStatus}","deliveryMethod":null,"detailConditionKey":"NAME","detailConditionValue":null,"selectedComplexConditionKey":null,"countPerPage":{countPerPage},"page":{page},"shipmentType":null}}'
        param = parse.quote(param)
        
        url = url + param

        res = self.get(url, headers=self.headers).json()
        return res

    def getOrderPD(self):
        url = 'https://wing.coupang.com/tenants/sfl-portal/delivery/management/dashboard/find-raw-piv-and-inventory-name'
        self.headers = {
            'Host': 'wing.coupang.com',
            'Connection': 'keep-alive',
            'Content-Length': '85',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=UTF-8',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'Origin': 'https://wing.coupang.com',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://wing.coupang.com/tenants/sfl-portal/delivery/management?deliverStatus=FINAL_DELIVERY&startDate=2021-09-26&endDate=2021-10-09',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ko,en-US;q=0.9,en;q=0.8,fr;q=0.7'
            # 'Accept-Language':'ko,en-US;q=0.9,en;q=0.8,fr;q=0.7',
            # 'Referer' : 'https://wing.coupang.com/tenants/sfl-portal/delivery/management?deliverStatus=FINAL_DELIVERY&startDate=2021-09-26&endDate=2021-10-09',
            # 'Content-Type':'application/json',
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36'
        }

        # payload = {"0":"74514086621", "1":"74514104079", "2":"75137953044", "3":"76800604629", "4":"74514127382", "5":"76306840890", "6":"74661320539"}
        payload = [('0',74514086621), ('1',74514104079)]
        # data = [75656023249,75656023653,76854025661,74514035801,75958852713,76983157610,74514107433,76496563838,76541422727,74514067562,76496559307]

        # res = self.post(url, data=data, headers=self.headers).json()
        res = self.post(url, headers=self.headers, data=payload)
        return res


    def getPd(self,id):
        url = 'https://wing.coupang.com/tenants/seller-web/vendor-inventory/search'
        self.headers = {
            'Accept-Language':'ko,en-US;q=0.9,en;q=0.8,fr;q=0.7',
            'Content-Type':'application/json',
            'Referer':'https://wing.coupang.com/vendor-inventory/list'
        }

        # data = f'{{"searchIds":"{id}","startTime":"2000-01-01","endTime":"2099-12-31"}}'
        data = dict()
        data['searchIds'] = id
        # param = f'{{"searchIds":"{id}","startTime":"2000-01-01","endTime":"2099-12-31","productName":null,"brandName":null,"manufacturerName":null,"productType":"","dateType":"productRegistrationDate","dateRangeShowStyle":true,"dateRange":"all","saleEndDatePeriodType":null,"includeUsedProduct":null,"deleteType":"false","deliveryMethod":null,"shippingType":null,"shipping":null,"otherType":null,"productStatus":["SAVED","WAIT_FOR_SALE","VALID","SOLD_OUT","INVALID","END_FOR_SALE","APPROVING","IN_REVIEW","DENIED","PARTIAL_APPROVED","APPROVED","ALL"],"advanceConditionShow":null,"displayCategoryCodes":[],"currentMenuCode":null,"page":1,"countPerPage":50,"sortField":"vendorInventoryId","desc":true,"fromListV2":true}}'
        
        res = self.post(url,headers=self.headers,data=dumps(data)).json()
        
        return res
