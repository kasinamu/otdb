import os
import time
import hmac, hashlib
import urllib.parse
import urllib.request
import ssl
import json
from datetime import datetime, timedelta

class Coupang():
    def __init__(self):
        self.vendorId = "A00429731"
        self.accesskey = "84e356e4-005a-42d2-bc3f-3c4bd8e01e57"
        self.secretkey = "138a06b1c45d717ae1884352c0f96e5780a58881"
    
    def getOrder(self, createdAtFrom="", createdAtTo="", status="", nextToken="", maxPerPage=50):
        os.environ['TZ'] = 'GMT+0'
        now = datetime.now()
        dtime=time.strftime('%y%m%d')+'T'+time.strftime('%H%M%S')+'Z'
        method = "GET"
        path = f"/v2/providers/openapi/apis/api/v4/vendors/{self.vendorId}/ordersheets"

        if createdAtTo == "":
            createdAtTo = now.strftime('%Y-%m-%d')
        
        if createdAtFrom == "":
            createdAtFrom = now - timedelta(days=3)
            createdAtFrom = createdAtFrom.strftime('%Y-%m-%d')
        
        params = {
            'createdAtFrom':f'{createdAtFrom}',
            'createdAtTo':f'{createdAtTo}',
            'status':f'{status}',
            'nextToken':f'{nextToken}',
            'maxPerPage': f'{maxPerPage}' # 페이지당 호출개수
        }

        query = urllib.parse.urlencode(params)
        message = dtime+method+path+query
        accesskey = self.accesskey
        secretkey = self.secretkey

        signature=hmac.new(secretkey.encode('utf-8'),message.encode('utf-8'),hashlib.sha256).hexdigest()
        authorization  = "CEA algorithm=HmacSHA256, access-key="+accesskey+", signed-date="+dtime+", signature="+signature
        
        url = "https://api-gateway.coupang.com"+path+"?%s" % query
        req = urllib.request.Request(url)
        req.add_header("Content-type","application/json;charset=UTF-8")
        req.add_header("Authorization",authorization)
        req.get_method = lambda: method
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        try:
            resp = urllib.request.urlopen(req,context=ctx)
        except urllib.request.HTTPError as e:
            print(e.code)
            print(e.reason)
            print(e.fp.read())
        except urllib.request.URLError as e:
            print(e.errno)
            print(e.reason)
            print(e.fp.read())
        else:
            # 200
            body = resp.read().decode(resp.headers.get_content_charset())
            res = json.loads(body)
            return res

    def viewOrderSimple(self,res,menu):
        code = res['code']
        message = res['message']
        data = res['data']
        nextToken = res['nextToken']
        orderCount = len(res['data'])
        print(f'\n쿠팡 [ {menu} ] : {str(orderCount)}건')

        totalSalePrice = 0
        no = 1
        for i in res['data']:
            print(f'No:{no}  ' + '='*50)
            shipmentBoxId = i['shipmentBoxId'] # Number	배송번호(묶음배송번호)
            orderId = i['orderId'] # Number	주문번호
            orderedAt = i['orderedAt'] # String	주문일시 yyyy-MM-dd'T'HH:mm:ss

            # orderer Object 주문자
            ordererName = i['orderer']['name'] # String	    주문자 이름
            ordrerEmail = i['orderer']['email'] # String 주문자 email 마스킹 처리됨
            reciverSafeNumber = i['orderer']['safeNumber'] # String 수취인 연락처(안심번호)
            ordererNumber = i['orderer']['ordererNumber'] # String 주문자 연락처(실전화번호)
            paidAt = i['paidAt'] # 	String	결제일시 yyyy-MM-dd'T'HH:mm:ss
            status = i['status'] # 	String  발주서 상태
            if status == 'ACCEPT':
                status = '결제완료'
            elif status == 'INSTRUCT':
                status = '상품준비중'
            elif status == 'DEPARTURE':
                status = '배송지시'
            elif status == 'DELIVERING':
                status = '배송중'
            elif status == 'FINAL_DELIVERY':
                status = '배송완료'
            shippingPrice = i['shippingPrice'] # Number 배송비
            remotePrice = i['remotePrice'] # Number 도서산간배송비
            remoteArea = i['remoteArea'] # Boolean 도서산간여부
            parcelPrintMessage = i['parcelPrintMessage'] # String배송메시지 (optional)
            splitShipping = i['splitShipping'] # Boolean  분리배송여부
            ableSplitShipping = i['ableSplitShipping'] # Boolean  분리배송가능여부
            
            # reciver Object 수취인
            reciverName = i['receiver']['name'] # String
            reciverSafeNumber = i['receiver']['safeNumber']
            reciverNumber = i['receiver']['receiverNumber']
            addr1 = i['receiver']['addr1']
            addr2 = i['receiver']['addr2']
            postCode = i['receiver']['postCode']

            # orderItems
            productId = i['orderItems'][0]['productId']
            vendorItemId = i['orderItems'][0]['vendorItemId']
            vendorItemName = i['orderItems'][0]['vendorItemName']
            shippingCount = i['orderItems'][0]['shippingCount']
            salesPrice = i['orderItems'][0]['salesPrice']
            orderPrice = i['orderItems'][0]['orderPrice']
            discountPrice = i['orderItems'][0]['discountPrice']
            instantCouponDiscount = i['orderItems'][0]['instantCouponDiscount']
            downloadableCouponDiscount = i['orderItems'][0]['downloadableCouponDiscount']
            coupangDiscount = i['orderItems'][0]['coupangDiscount']
            sellerProductId = i['orderItems'][0]['sellerProductId']
            sellerProductName = i['orderItems'][0]['sellerProductName']
            sellerProductItemName = i['orderItems'][0]['sellerProductItemName']
            firstSellerProductItemName = i['orderItems'][0]['firstSellerProductItemName']
            cancelCount = i['orderItems'][0]['cancelCount']
            holdCountForCancel = i['orderItems'][0]['holdCountForCancel']
            estimatedShippingDate = i['orderItems'][0]['estimatedShippingDate']
            plannedShippingDate = i['orderItems'][0]['plannedShippingDate']
            invoiceNumberUploadDate = i['orderItems'][0]['invoiceNumberUploadDate']
            extraProperties = i['orderItems'][0]['extraProperties']
            pricingBadge = i['orderItems'][0]['pricingBadge']
            usedProduct = i['orderItems'][0]['usedProduct']
            confirmDate = i['orderItems'][0]['confirmDate']
            deliveryChargeTypeName = i['orderItems'][0]['deliveryChargeTypeName']
            canceled = i['orderItems'][0]['canceled']

            #overseaShippingInfoDto 해외배송정보
            personalCustomsClearanceCode = i['overseaShippingInfoDto']['personalCustomsClearanceCode']
            ordererPhoneNumber = i['overseaShippingInfoDto']['ordererPhoneNumber']

            deliveryCompanyName = i['deliveryCompanyName']
            invoiceNumber = i['invoiceNumber']
            inTrasitDateTime = i['inTrasitDateTime']
            deliveredDate = i['deliveredDate']
            refer = i['refer']
            shipmentType = i['shipmentType']


            ## print
            print('=='*60)
            print('orderId: ',orderId)

            # orderer Object 주문자
            print('ordererName: ',ordererName)
            print('status: ',status)
            print('shippingPrice: ',shippingPrice)
            
            # reciver Object 수취인
            print('reciverName: ',reciverName)
            print('reciverSafeNumber: ',reciverSafeNumber)
            print('reciverNumber: ',reciverNumber)
            print('addr1: ',addr1)
            print('addr2: ',addr2)
            print('postCode: ',postCode)
            # orderItems
            print('sellerProductId: ',sellerProductId) # 등록상품ID
            print('productId: ',productId) # 노출상품ID
            print('vendorItemId: ',vendorItemId)  # 옵션ID
            print('vendorItemName: ',vendorItemName)
            print('shippingCount: ',shippingCount)
            print('salesPrice: ',salesPrice)
            print('orderPrice: ',orderPrice)
            print('discountPrice: ',discountPrice)
            print('instantCouponDiscount: ',instantCouponDiscount)
            print('downloadableCouponDiscount: ',downloadableCouponDiscount)
            print('coupangDiscount: ',coupangDiscount)
            print('deliveryChargeTypeName: ',deliveryChargeTypeName)
            print('deliveryCompanyName: ',deliveryCompanyName)
            print('parcelPrintMessage: ',parcelPrintMessage)
            
            

            totalSalePrice += orderPrice
            no+=1

        if orderCount > 0:
            print(f'\n\n총판매금액:{totalSalePrice}')




    def viewOrderFull(self,res,menu):
        code = res['code']
        message = res['message']
        data = res['data']
        nextToken = res['nextToken']
        orderCount = len(res['data'])
        print(f'쿠팡 검색건수:{orderCount}   ' + '='*50)
        totalSalePrice = 0

        for i in res['data']:
            shipmentBoxId = i['shipmentBoxId'] # Number	배송번호(묶음배송번호)
            orderId = i['orderId'] # Number	주문번호
            orderedAt = i['orderedAt'] # String	주문일시 yyyy-MM-dd'T'HH:mm:ss

            # orderer Object 주문자
            ordererName = i['orderer']['name'] # String	    주문자 이름
            ordrerEmail = i['orderer']['email'] # String 주문자 email 마스킹 처리됨
            reciverSafeNumber = i['orderer']['safeNumber'] # String 수취인 연락처(안심번호)
            ordererNumber = i['orderer']['ordererNumber'] # String 주문자 연락처(실전화번호)
            
            paidAt = i['paidAt'] # 	String	결제일시 yyyy-MM-dd'T'HH:mm:ss
            status = i['status'] # 	String  발주서 상태
            '''
            Parameter Name / Status
            ACCEPT	/ 결제완료
            INSTRUCT / 상품준비중
            DEPARTURE / 배송지시
            DELIVERING / 배송중
            FINAL_DELIVERY / 배송완료
            NONE_TRACKING / 업체 직접 배송(배송 연동 미적용), 추적불가
            '''
            shippingPrice = i['shippingPrice'] # Number 배송비
            remotePrice = i['remotePrice'] # Number 도서산간배송비
            remoteArea = i['remoteArea'] # Boolean 도서산간여부
            parcelPrintMessage = i['parcelPrintMessage'] # String배송메시지 (optional)
            splitShipping = i['splitShipping'] # Boolean  분리배송여부
            ableSplitShipping = i['ableSplitShipping'] # Boolean  분리배송가능여부
            
            # reciver Object 수취인
            reciverName = i['receiver']['name'] # String
            reciverSafeNumber = i['receiver']['safeNumber']
            reciverNumber = i['receiver']['receiverNumber']
            addr1 = i['receiver']['addr1']
            addr2 = i['receiver']['addr2']
            postCode = i['receiver']['postCode']

            # orderItems
            productId = i['orderItems'][0]['productId']
            vendorItemId = i['orderItems'][0]['vendorItemId']
            vendorItemName = i['orderItems'][0]['vendorItemName']
            shippingCount = i['orderItems'][0]['shippingCount']
            salesPrice = i['orderItems'][0]['salesPrice']
            orderPrice = i['orderItems'][0]['orderPrice']
            discountPrice = i['orderItems'][0]['discountPrice']
            instantCouponDiscount = i['orderItems'][0]['instantCouponDiscount']
            downloadableCouponDiscount = i['orderItems'][0]['downloadableCouponDiscount']
            coupangDiscount = i['orderItems'][0]['coupangDiscount']
            # externalVendorSkuCode = i['orderItems']['externalVendorSkuCode']
            # etcInfoHeader = i['orderItems']['etcInfoHeader']
            # etcInfoValue = i['orderItems']['etcInfoValue']
            # etcInfoValues = i['orderItems']['etcInfoValues']
            sellerProductId = i['orderItems'][0]['sellerProductId']
            sellerProductName = i['orderItems'][0]['sellerProductName']
            sellerProductItemName = i['orderItems'][0]['sellerProductItemName']
            firstSellerProductItemName = i['orderItems'][0]['firstSellerProductItemName']
            cancelCount = i['orderItems'][0]['cancelCount']
            holdCountForCancel = i['orderItems'][0]['holdCountForCancel']
            estimatedShippingDate = i['orderItems'][0]['estimatedShippingDate']
            plannedShippingDate = i['orderItems'][0]['plannedShippingDate']
            invoiceNumberUploadDate = i['orderItems'][0]['invoiceNumberUploadDate']
            extraProperties = i['orderItems'][0]['extraProperties']
            pricingBadge = i['orderItems'][0]['pricingBadge']
            usedProduct = i['orderItems'][0]['usedProduct']
            confirmDate = i['orderItems'][0]['confirmDate']
            deliveryChargeTypeName = i['orderItems'][0]['deliveryChargeTypeName']
            canceled = i['orderItems'][0]['canceled']

            #overseaShippingInfoDto 해외배송정보
            personalCustomsClearanceCode = i['overseaShippingInfoDto']['personalCustomsClearanceCode']
            # orderersSsn = i['overseaShippingInfoDto']['orderersSsn']
            ordererPhoneNumber = i['overseaShippingInfoDto']['ordererPhoneNumber']

            deliveryCompanyName = i['deliveryCompanyName']
            invoiceNumber = i['invoiceNumber']
            inTrasitDateTime = i['inTrasitDateTime']
            deliveredDate = i['deliveredDate']
            refer = i['refer']
            shipmentType = i['shipmentType']


            ## print
            print('=='*60)
            print('shipmentBoxId: ',shipmentBoxId)
            print('orderId: ',orderId)
            print('orderedAt: ',orderedAt)

            # orderer Object 주문자
            print('ordererName: ',ordererName)
            print('ordrerEmail: ',ordrerEmail)
            print('reciverSafeNumber: ',reciverSafeNumber)
            print('ordererNumber: ',ordererNumber)
            
            print('paidAt: ',paidAt)
            print('status: ',status)
            '''
            Parameter Name / Status
            ACCEPT	/ 결제완료
            INSTRUCT / 상품준비중
            DEPARTURE / 배송지시
            DELIVERING / 배송중
            FINAL_DELIVERY / 배송완료
            NONE_TRACKING / 업체 직접 배송(배송 연동 미적용), 추적불가
            '''
            print('shippingPrice: ',shippingPrice)
            print('remotePrice: ',remotePrice)
            print('remoteArea: ',remoteArea)
            print('parcelPrintMessage: ',parcelPrintMessage)
            print('splitShipping: ',splitShipping)
            print('ableSplitShipping: ',ableSplitShipping)
            
            # reciver Object 수취인
            print('reciverName: ',reciverName)
            print('reciverSafeNumber: ',reciverSafeNumber)
            print('reciverNumber: ',reciverNumber)
            print('addr1: ',addr1)
            print('addr2: ',addr2)
            print('postCode: ',postCode)

            # orderItems
            print('productId: ',productId)
            print('vendorItemId: ',vendorItemId)
            print('vendorItemName: ',vendorItemName)
            print('shippingCount: ',shippingCount)
            print('salesPrice: ',salesPrice)
            print('orderPrice: ',orderPrice)
            print('discountPrice: ',discountPrice)
            print('instantCouponDiscount: ',instantCouponDiscount)
            print('downloadableCouponDiscount: ',downloadableCouponDiscount)
            print('coupangDiscount: ',coupangDiscount)
            # print('externalVendorSkuCode: ',externalVendorSkuCode)
            # print('etcInfoHeader: ',etcInfoHeader)
            # print('etcInfoValue: ',etcInfoValue)
            # print('etcInfoValues: ',etcInfoValues)
            print('sellerProductId: ',sellerProductId)
            print('sellerProductName: ',sellerProductName)
            print('sellerProductItemName: ',sellerProductItemName)
            print('firstSellerProductItemName: ',firstSellerProductItemName)
            print('cancelCount: ',cancelCount)
            print('holdCountForCancel: ',holdCountForCancel)
            print('estimatedShippingDate: ',estimatedShippingDate)
            print('plannedShippingDate: ',plannedShippingDate)
            print('invoiceNumberUploadDate: ',invoiceNumberUploadDate)
            print('extraProperties: ',extraProperties)
            print('pricingBadge: ',pricingBadge)
            print('usedProduct: ',usedProduct)
            print('confirmDate: ',confirmDate)
            print('deliveryChargeTypeName: ',deliveryChargeTypeName)
            print('canceled: ',canceled)

            #overseaShippingInfoDto 해외배송정보
            print('personalCustomsClearanceCode: ',personalCustomsClearanceCode)
            # print('orderersSsn: ',orderersSsn)
            print('ordererPhoneNumber: ',ordererPhoneNumber)

            print('deliveryCompanyName: ',deliveryCompanyName)
            print('invoiceNumber: ',invoiceNumber)
            print('inTrasitDateTime: ',inTrasitDateTime)
            print('deliveredDate: ',deliveredDate)
            print('refer: ',refer)
            print('shipmentType: ',shipmentType)

            totalSalePrice += orderPrice

        if orderCount > 0:
            print(f'\n\n총판매금액:{totalSalePrice}')
