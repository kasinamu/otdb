import requests
from urllib import parse
# from fake_useragent import UserAgent
from requests import Session
from dateutil.relativedelta import relativedelta
# from bs4 import BeautifulSoup
from rsa import encrypt, PublicKey
from lzstring import LZString
import lzstring
from uuid import uuid4
from json import dumps
import json
from datetime import datetime, timedelta
import sqlite3
import rsa
import re
import uuid
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


########################### 네이버 클래스 #################################

class Naver(Session):
    def __init__(self):
        super().__init__()
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        self.nid = "cadone0024"
        self.npw = "qw97010400@"
        self.login()

    def encrypt(self, key_str, uid, upw):
        def naver_style_join(l):
            return ''.join([chr(len(s)) + s for s in l])

        sessionkey, keyname, e_str, n_str = key_str.split(',')
        e, n = int(e_str, 16), int(n_str, 16)

        message = naver_style_join([sessionkey, uid, upw]).encode()

        pubkey = rsa.PublicKey(e, n)
        encrypted = rsa.encrypt(message, pubkey)

        return keyname, encrypted.hex()


    def encrypt_account(self, uid, upw):
        key_str = requests.get('https://nid.naver.com/login/ext/keys.nhn').content.decode("utf-8")
        return self.encrypt(key_str, uid, upw)


    def login(self):

        encnm, encpw = self.encrypt_account(self.nid, self.npw)

        s = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504]
        )
        s.mount('https://', HTTPAdapter(max_retries=retries))
        request_headers = {
            'User-agent': 'Mozilla/5.0'
        }

        bvsd_uuid = uuid.uuid4()
        encData = '{"a":"%s-4","b":"1.3.4","d":[{"i":"id","b":{"a":["0,%s"]},"d":"%s","e":false,"f":false},{"i":"%s","e":true,"f":false}],"h":"1f","i":{"a":"Mozilla/5.0"}}' % (bvsd_uuid, self.nid, self.nid, self.npw)
        bvsd = '{"uuid":"%s","encData":"%s"}' % (bvsd_uuid, lzstring.LZString.compressToEncodedURIComponent(encData))

        url = "https://nid.naver.com/nidlogin.login?url=https%3A%2F%2Fsell.smartstore.naver.com%2F%23%2FnaverLoginCallback%3Furl%3Dhttps%253A%252F%252Fsell.smartstore.naver.com%252F%2523"
        res = s.post(url, data={
            'svctype': '0',
            'enctp': '1',
            'encnm': encnm,
            'enc_url': 'http0X0.0000000000001P-10220.0000000.000000www.naver.com',
            'url': 'www.naver.com',
            'smart_level': '1',
            'encpw': encpw,
            'bvsd': bvsd
        }, headers=request_headers)

        finalize_url = re.search(r'location\.replace\("([^"]+)"\)', res.content.decode("utf-8")).group(1)
        s.get(finalize_url)
        redirect_cookie = res.headers['Set-Cookie']
        self.headers = {"Cookie": redirect_cookie}
        self.getStatus()

    
    def getStatus(self):
        url = 'https://sell.smartstore.naver.com/api/dashboards/pay/sale-stats'
        res = self.get(url).json()

        결제대기 = res['paymentWaitCases']
        신규주문 = res['newOrderCases']
        오늘출발 = res['todayDispatchCases']
        예약구매 = res['preOrderCases']
        배송준비 = res['deliveryPreparingCases']
        배송중 = res['deliveringCases']
        배송완료 = res['deliveredCases']

        dict_status = {
            '결제대기': 결제대기,
            '신규주문': 신규주문,
            '오늘출발': 오늘출발,
            '예약구매': 예약구매,
            '배송준비': 배송준비,
            '배송중': 배송중,
            '배송완료': 배송완료
        }
        return dict_status

    def getOrder(self,menu):
        url = 'https://sell.smartstore.naver.com/o/v3/graphql'
        if menu == '신규주문':
            referer = 'https://sell.smartstore.naver.com/o/v3/n/sale/delivery'
            payload = {"operationName":"smartstoreFindDeliveriesBySummaryInfoType_ForSaleDelivery","variables":{"merchantNo":"510947431","serviceType":"MP","paging_page":1,"paging_size":100,"sort_type":"RECENTLY_ORDER_YMDT","sort_direction":"DESC","summaryInfoType":"NEW_ORDERS"},"query":"query smartstoreFindDeliveriesBySummaryInfoType_ForSaleDelivery($merchantNo: String!, $paging_page: Int, $paging_size: Int, $serviceType: ServiceType!, $sort_direction: SortDirectionType, $sort_type: SortType, $summaryInfoType: SummaryInfoType) {\n  deliveryList: smartstoreFindDeliveriesBySummaryInfoType_ForSaleDelivery(merchantNo: $merchantNo, paging_page: $paging_page, paging_size: $paging_size, serviceType: $serviceType, sort_direction: $sort_direction, sort_type: $sort_type, summaryInfoType: $summaryInfoType) {\n    elements {\n      ...deliveryElementField\n      __typename\n    }\n    pagination {\n      ...paginationField\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment deliveryElementField on DeliveryMp {\n  deliveryFeeClass\n  deliveryInvoiceNo\n  orderQuantity\n  productName\n  payDateTime\n  deliveryDateTime\n  deliveryFeeRatingClass\n  productOrderMemo\n  orderMemberId\n  remoteAreaCostChargeAmt\n  salesCommissionPrepay\n  payLocationType\n  totalDiscountAmt\n  orderNo\n  payMeansClass\n  productClass\n  commissionClassType\n  purchaserSocialSecurityNo\n  oneYearOrderAmt\n  saleChannelType\n  oneYearOrderCount\n  receiverAddress\n  deliveryCompanyName\n  sellerProductManagementCode\n  grade\n  sellingInterlockCommissionClassType\n  sellingInterlockCommissionInflowPath\n  orderMemberTelNo\n  deliveryFeeAmt\n  claimNo\n  deliveryMethod\n  deliveryMethodPay\n  biztalkAccountId\n  giftName\n  receiverTelNo2\n  productPayAmt\n  receiverTelNo1\n  sixMonthOrderAmt\n  orderStatus\n  productUnitPrice\n  waybillPrintDateTime\n  threeMonthOrderCount\n  orderMemberName\n  productOrderNo\n  deliveryCompanyCode\n  productOptionContents\n  dispatchDueDateTime\n  knowledgeShoppingCommissionAmt\n  productOptionAmt\n  productNo\n  individualCustomUniqueCode\n  orderDateTime\n  placingOrderDateTime\n  inflowPath\n  receiverName\n  settlementExpectAmt\n  deliveryNo\n  threeMonthOrderAmt\n  sellerDiscountAmt\n  deliveryFeeDiscountAmt\n  dispatchDateTime\n  sixMonthOrderCount\n  receiverZipCode\n  payCommissionAmt\n  takingGoodsPlaceAddress\n  syncDateTime\n  productOrderStatus\n  sellerInternalCode2\n  sellerOptionManagementCode\n  sellerInternalCode1\n  deliveryBundleGroupSeq\n  productUrl\n  subscriptionRound\n  subscriptionPeriodCount\n  __typename\n}\n\nfragment paginationField on Pagination {\n  size\n  totalElements\n  page\n  totalPages\n  __typename\n}\n"}
            strlist = 'deliveryList'

        elif menu == '배송준비':
            referer = 'https://sell.smartstore.naver.com/o/v3/n/sale/delivery?summaryInfoType=DELIVERY_READY'
            payload = {"operationName":"smartstoreFindDeliveriesBySummaryInfoType_ForSaleDelivery","variables":{"merchantNo":"510947431","serviceType":"MP","paging_page":1,"paging_size":100,"sort_type":"RECENTLY_ORDER_YMDT","sort_direction":"DESC","summaryInfoType":"DELIVERY_READY"},"query":"query smartstoreFindDeliveriesBySummaryInfoType_ForSaleDelivery($merchantNo: String!, $paging_page: Int, $paging_size: Int, $serviceType: ServiceType!, $sort_direction: SortDirectionType, $sort_type: SortType, $summaryInfoType: SummaryInfoType) {\n  deliveryList: smartstoreFindDeliveriesBySummaryInfoType_ForSaleDelivery(merchantNo: $merchantNo, paging_page: $paging_page, paging_size: $paging_size, serviceType: $serviceType, sort_direction: $sort_direction, sort_type: $sort_type, summaryInfoType: $summaryInfoType) {\n    elements {\n      ...deliveryElementField\n      __typename\n    }\n    pagination {\n      ...paginationField\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment deliveryElementField on DeliveryMp {\n  deliveryFeeClass\n  deliveryInvoiceNo\n  orderQuantity\n  productName\n  payDateTime\n  deliveryDateTime\n  deliveryFeeRatingClass\n  productOrderMemo\n  orderMemberId\n  remoteAreaCostChargeAmt\n  salesCommissionPrepay\n  payLocationType\n  totalDiscountAmt\n  orderNo\n  payMeansClass\n  productClass\n  commissionClassType\n  purchaserSocialSecurityNo\n  oneYearOrderAmt\n  saleChannelType\n  oneYearOrderCount\n  receiverAddress\n  deliveryCompanyName\n  sellerProductManagementCode\n  grade\n  sellingInterlockCommissionClassType\n  sellingInterlockCommissionInflowPath\n  orderMemberTelNo\n  deliveryFeeAmt\n  claimNo\n  deliveryMethod\n  deliveryMethodPay\n  biztalkAccountId\n  giftName\n  receiverTelNo2\n  productPayAmt\n  receiverTelNo1\n  sixMonthOrderAmt\n  orderStatus\n  productUnitPrice\n  waybillPrintDateTime\n  threeMonthOrderCount\n  orderMemberName\n  productOrderNo\n  deliveryCompanyCode\n  productOptionContents\n  dispatchDueDateTime\n  knowledgeShoppingCommissionAmt\n  productOptionAmt\n  productNo\n  individualCustomUniqueCode\n  orderDateTime\n  placingOrderDateTime\n  inflowPath\n  receiverName\n  settlementExpectAmt\n  deliveryNo\n  threeMonthOrderAmt\n  sellerDiscountAmt\n  deliveryFeeDiscountAmt\n  dispatchDateTime\n  sixMonthOrderCount\n  receiverZipCode\n  payCommissionAmt\n  takingGoodsPlaceAddress\n  syncDateTime\n  productOrderStatus\n  sellerInternalCode2\n  sellerOptionManagementCode\n  sellerInternalCode1\n  deliveryBundleGroupSeq\n  productUrl\n  __typename\n}\n\nfragment paginationField on Pagination {\n  size\n  totalElements\n  page\n  totalPages\n  __typename\n}\n"}
            strlist = 'deliveryList'

        elif menu == '배송중':
            referer = 'https://sell.smartstore.naver.com/o/v3/n/sale/delivery/situation?summaryInfoType=DELIVERING'
            payload = {"operationName":"SmartStoreFindDeliveryStatusesBySummaryInfoType_ForSaleDeliveryStatus","variables":{"merchantNo":"510947431","serviceType":"MP","paging_page":1,"paging_size":100,"summaryInfoType":"DELIVERING"},"query":"query SmartStoreFindDeliveryStatusesBySummaryInfoType_ForSaleDeliveryStatus($merchantNo: String!, $paging_page: Int, $paging_size: Int, $serviceType: String!, $sort_direction: SortDirectionType, $sort_type: SortType, $summaryInfoType: SummaryInfoType) {\n  deliveryStatusListMp: SmartStoreFindDeliveryStatusesBySummaryInfoType_ForSaleDeliveryStatus(merchantNo: $merchantNo, paging_page: $paging_page, paging_size: $paging_size, serviceType: $serviceType, sort_direction: $sort_direction, sort_type: $sort_type, summaryInfoType: $summaryInfoType) {\n    elements {\n      ...deliveryStatusElementFieldMp\n      __typename\n    }\n    pagination {\n      ...paginationField\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment deliveryStatusElementFieldMp on SaleDeliveryStatusMp {\n  deliveryFeeClass\n  mistakenInvoiceRegDateTime\n  deliveryInvoiceNo\n  orderQuantity\n  productName\n  mistakenInvoiceReason\n  payDateTime\n  deliveryFeeRatingClass\n  mistakenInvoiceYn\n  orderMemberId\n  remoteAreaCostChargeAmt\n  invoiceNo\n  purchaseDecisionRequestDateTime\n  totalDiscountAmt\n  orderNo\n  productClass\n  deliveryCompleteDateTime\n  purchaseDecisionExtensionReason\n  saleChannelType\n  receiverAddress\n  deliveryCompanyName\n  sellerProductManagementCode\n  claimStatus\n  orderMemberTelNo\n  purchaseDecisionExtensionDateTime\n  deliveryFeeAmt\n  deliveryMethod\n  biztalkAccountId\n  receiverTelNo2\n  productPayAmt\n  receiverTelNo1\n  orderStatus\n  productUnitPrice\n  orderMemberName\n  productOrderNo\n  deliveryCompanyCode\n  productOptionContents\n  productOptionAmt\n  productNo\n  purchaseDecisionExpectDateTime\n  receiverName\n  deliveryNo\n  purchaseDecisionRequestOperator\n  sellerDiscountAmt\n  deliveryFeeDiscountAmt\n  dispatchDateTime\n  receiverZipCode\n  syncDateTime\n  productOrderStatus\n  sellerInternalCode2\n  sellerInternalCode1\n  deliveryBundleGroupSeq\n  productUrl\n  __typename\n}\n\nfragment paginationField on Pagination {\n  size\n  totalElements\n  page\n  totalPages\n  __typename\n}\n"}
            strlist = 'deliveryStatusListMp'

        elif menu == '배송완료':
            referer = 'https://sell.smartstore.naver.com/o/v3/n/sale/delivery/situation?summaryInfoType=DELIVERING'
            payload = {"operationName":"SmartStoreFindDeliveryStatusesBySummaryInfoType_ForSaleDeliveryStatus","variables":{"merchantNo":"510947431","serviceType":"MP","paging_page":1,"paging_size":100,"summaryInfoType":"DELIVERED"},"query":"query SmartStoreFindDeliveryStatusesBySummaryInfoType_ForSaleDeliveryStatus($merchantNo: String!, $paging_page: Int, $paging_size: Int, $serviceType: String!, $sort_direction: SortDirectionType, $sort_type: SortType, $summaryInfoType: SummaryInfoType) {\n  deliveryStatusListMp: SmartStoreFindDeliveryStatusesBySummaryInfoType_ForSaleDeliveryStatus(merchantNo: $merchantNo, paging_page: $paging_page, paging_size: $paging_size, serviceType: $serviceType, sort_direction: $sort_direction, sort_type: $sort_type, summaryInfoType: $summaryInfoType) {\n    elements {\n      ...deliveryStatusElementFieldMp\n      __typename\n    }\n    pagination {\n      ...paginationField\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment deliveryStatusElementFieldMp on SaleDeliveryStatusMp {\n  deliveryFeeClass\n  mistakenInvoiceRegDateTime\n  deliveryInvoiceNo\n  orderQuantity\n  productName\n  mistakenInvoiceReason\n  payDateTime\n  deliveryFeeRatingClass\n  mistakenInvoiceYn\n  orderMemberId\n  remoteAreaCostChargeAmt\n  invoiceNo\n  purchaseDecisionRequestDateTime\n  totalDiscountAmt\n  orderNo\n  productClass\n  deliveryCompleteDateTime\n  purchaseDecisionExtensionReason\n  saleChannelType\n  receiverAddress\n  deliveryCompanyName\n  sellerProductManagementCode\n  claimStatus\n  orderMemberTelNo\n  purchaseDecisionExtensionDateTime\n  deliveryFeeAmt\n  deliveryMethod\n  biztalkAccountId\n  receiverTelNo2\n  productPayAmt\n  receiverTelNo1\n  orderStatus\n  productUnitPrice\n  orderMemberName\n  productOrderNo\n  deliveryCompanyCode\n  productOptionContents\n  productOptionAmt\n  productNo\n  purchaseDecisionExpectDateTime\n  receiverName\n  deliveryNo\n  purchaseDecisionRequestOperator\n  sellerDiscountAmt\n  deliveryFeeDiscountAmt\n  dispatchDateTime\n  receiverZipCode\n  syncDateTime\n  productOrderStatus\n  sellerInternalCode2\n  sellerInternalCode1\n  deliveryBundleGroupSeq\n  productUrl\n  __typename\n}\n\nfragment paginationField on Pagination {\n  size\n  totalElements\n  page\n  totalPages\n  __typename\n}\n"}
            strlist = 'deliveryStatusListMp'

        elif menu == '구매확정':
            referer = 'https://sell.smartstore.naver.com/o/v3/sale/purchaseDecision?summaryInfoType=PURCHASE_DECIDED'
            payload = {"operationName":"SmartStoreFindPurchaseDecisionsBySummaryInfoType_ForPurchaseDecision","variables":{"merchantNo":"510947431","serviceType":"MP","paging_page":1,"paging_size":100,"sort_type":"PRODUCT_ORDER_PURCHASE_DECISION_COMPLETE_OPERATION_YMDT","sort_direction":"DESC","summaryInfoType":"PURCHASE_DECIDED"},"query":"query SmartStoreFindPurchaseDecisionsBySummaryInfoType_ForPurchaseDecision($merchantNo: String!, $serviceType: String!, $paging_page: Int, $paging_size: Int, $sort_direction: SortDirectionType, $sort_type: SortType, $summaryInfoType: SummaryInfoType) {\n  purchaseDecisionList: SmartStoreFindPurchaseDecisionsBySummaryInfoType_ForPurchaseDecision(merchantNo: $merchantNo, serviceType: $serviceType, paging_page: $paging_page, paging_size: $paging_size, sort_direction: $sort_direction, sort_type: $sort_type, summaryInfoType: $summaryInfoType) {\n    elements {\n      ...purchaseDecisionElementField\n      __typename\n    }\n    pagination {\n      ...paginationField\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment purchaseDecisionElementField on PurchaseDecisionMp {\n  deliveryFeeAmt\n  deliveryFeeClass\n  deliveryMethod\n  biztalkAccountId\n  deliveryInvoiceNo\n  productPayAmt\n  orderStatus\n  productUnitPrice\n  purchaseDecisionCompleteDateTime\n  orderQuantity\n  productName\n  orderMemberName\n  payDateTime\n  productOrderNo\n  productOptionContents\n  deliveryFeeRatingClass\n  orderMemberId\n  knowledgeShoppingCommissionAmt\n  remoteAreaCostChargeAmt\n  productOptionAmt\n  salesCommissionPrepay\n  productNo\n  payLocationType\n  totalDiscountAmt\n  orderNo\n  payMeansClass\n  productClass\n  commissionClassType\n  inflowPath\n  receiverName\n  settlementExpectAmt\n  deliveryNo\n  deliveryCompleteDateTime\n  saleChannelType\n  sellerDiscountAmt\n  deliveryCompanyName\n  deliveryFeeDiscountAmt\n  dispatchDateTime\n  sellerProductManagementCode\n  payCommissionAmt\n  syncDateTime\n  productOrderStatus\n  sellerInternalCode2\n  sellingInterlockCommissionClassType\n  sellingInterlockCommissionInflowPath\n  sellerInternalCode1\n  deliveryBundleGroupSeq\n  productUrl\n  __typename\n}\n\nfragment paginationField on Pagination {\n  size\n  totalElements\n  page\n  totalPages\n  __typename\n}\n"}
            strlist = 'purchaseDecisionList'



        self.headers = {
            'accept':'*/*',
            'accept-language':'ko,en-US;q=0.9,en;q=0.8,fr;q=0.7',
            'content-type':'application/json',
            'origin':'https://sell.smartstore.naver.com',
            'referer': f'{referer}',
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
        }
        
        res = self.post(url, headers=self.headers, data=dumps(payload)).json()
        return res


    def orderViewFull(self,res,menu='신규주문'):
        keys = res['data'].keys()
        for k in keys:
            if (len(res['data'][k]['elements']))==0:
                print(f'네이버 {menu} 0건   ' + '=='*60)  
            else:
                no = 1
                for i in res['data'][k]['elements']:
                    print(f'\n네이버 {menu} No.{no}   ' + '=='*60)    
                    productOrderNo = i['productOrderNo'] #상품주문번호
                    orderNo = i['orderNo'] #주문번호
                    dispatchDateTime = i['dispatchDateTime'] #발송처리일
                    orderStatus = i['orderStatus'] #주문상태
                    deliveryMethod = i['deliveryMethod'] #배송방법
                    deliveryCompanyName = i['deliveryCompanyName'] #택배사
                    # invoiceNo = i['invoiceNo'] #송장번호
                    # 배송트래킹 = https://sell.smartstore.naver.com/o/v3/n/sale/delivery/tracking/{deliveryNo}/{productOrderNo}
                    deliveryNo = i['deliveryNo']
                    saleChannelType = i['saleChannelType'] #판매채널
                    orderMemberName = i['orderMemberName'] #구매자
                    orderMemberId = i['orderMemberId'] #구매자ID
                    receiverName = i['receiverName'] #수취인
                    # claimStatus = i['claimStatus'] #클레임상태 # 배송준비에선 없는 키
                    productNo = i['productNo'] #상품번호        
                    # 스토어 상품페이지 https://smartstore.naver.com/otindustry/products/{productNo}
                    productUrl = i['productUrl']
                    productName = i['productName'] #상품명
                    productClass = i['productClass'] #상품종류
                    productOptionContents = i['productOptionContents'] #옵션정보
                    orderQuantity = i['orderQuantity'] #수량
                    productUnitPrice = i['productUnitPrice'] #상품가격
                    productOptionAmt = i['productOptionAmt'] #옵션가격
                    totalDiscountAmt = i['totalDiscountAmt'] # 상품별 할인액
                    sellerDiscountAmt = i['sellerDiscountAmt'] #판매자 부담 할인액
                    productPayAmt = i['productPayAmt'] #상품별 총 주문금액
                    payDateTime = i['payDateTime'] #결제일

                    ## 배송준비에선 없는 키
                    lst = ['배송준비','신규주문']
                    if menu not in lst:
                        deliveryCompleteDateTime = i['deliveryCompleteDateTime'] #배송완료일
                        purchaseDecisionRequestDateTime = i['purchaseDecisionRequestDateTime'] #구매확정 요청일
                        purchaseDecisionRequestOperator = i['purchaseDecisionRequestOperator'] #구매확정 요청자
                        mistakenInvoiceYn = i['mistakenInvoiceYn'] # 문제송장 여부
                        mistakenInvoiceRegDateTime = i['mistakenInvoiceRegDateTime'] # 문제송장 등록일
                        mistakenInvoiceReason = i['mistakenInvoiceReason'] # 문제송장 등록사유
                        purchaseDecisionExpectDateTime = i['purchaseDecisionExpectDateTime'] # 자동구매확정 예정일
                        purchaseDecisionExtensionDateTime = i['purchaseDecisionExtensionDateTime'] # 구매확정연장 설정일
                        purchaseDecisionExtensionReason = i['purchaseDecisionExtensionReason'] # 구매확정연장 사유


                    sellerProductManagementCode = i['sellerProductManagementCode'] # 판매자 상품코드
                    sellerInternalCode1 = i['sellerInternalCode1'] # 판매자 내부코드1
                    sellerInternalCode2 = i['sellerInternalCode2'] # 판매자 내부코드2
                    deliveryBundleGroupSeq = i['deliveryBundleGroupSeq'] # 배송비 묶음번호
                    deliveryFeeClass = i['deliveryFeeClass'] # 배송비 형태
                    deliveryFeeRatingClass = i['deliveryFeeRatingClass'] # 배송비 유형
                    deliveryFeeAmt = i['deliveryFeeAmt'] # 배송비 합계
                    remoteAreaCostChargeAmt = i['remoteAreaCostChargeAmt'] # 제주/도서 추가배송비
                    deliveryFeeDiscountAmt = i['deliveryFeeDiscountAmt'] # 배송비 할인액
                    receiverTelNo1 = i['receiverTelNo1'] # 수취인연락처1
                    receiverTelNo2 = i['receiverTelNo2'] # 수취인연락처2
                    receiverAddress = i['receiverAddress'] # 배송지
                    orderMemberTelNo = i['orderMemberTelNo'] # 구매자연락처
                    receiverZipCode = i['receiverZipCode'] # 우편번호

                    print('productOrderNo: ',productOrderNo) 
                    print('orderNo: ',orderNo) 
                    print('dispatchDateTime: ',dispatchDateTime) 
                    print('orderStatus: ',orderStatus) 
                    print('deliveryMethod: ',deliveryMethod) 
                    print('deliveryCompanyName: ',deliveryCompanyName) 
                    # print('invoiceNo: ',invoiceNo) # 배송준비에선 없는 키
                    print('deliveryNo: ',deliveryNo) 
                    print('saleChannelType: ',saleChannelType) 
                    print('orderMemberName: ',orderMemberName) 
                    print('orderMemberId: ',orderMemberId) 
                    print('receiverName: ',receiverName) 
                    # print('claimStatus: ',claimStatus) # 배송준비에선 없는 키
                    print('productNo: ',productNo) 
                    print('productUrl: ',productUrl) 
                    print('productName: ',productName) 
                    print('productClass: ',productClass) 
                    print('productOptionContents: ',productOptionContents) 
                    print('orderQuantity: ',orderQuantity) 
                    print('productUnitPrice: ',productUnitPrice) 
                    print('productOptionAmt: ',productOptionAmt) 
                    print('totalDiscountAmt: ',totalDiscountAmt) 
                    print('sellerDiscountAmt: ',sellerDiscountAmt) 
                    print('productPayAmt: ',productPayAmt) 
                    print('payDateTime: ',payDateTime)

                    if menu not in lst:
                        print('deliveryCompleteDateTime: ',deliveryCompleteDateTime) # 배송준비에선 없는 키
                        print('purchaseDecisionRequestDateTime: ',purchaseDecisionRequestDateTime) # 배송준비에선 없는 키
                        print('purchaseDecisionRequestOperator: ',purchaseDecisionRequestOperator) # 배송준비에선 없는 키
                        print('mistakenInvoiceYn: ',mistakenInvoiceYn) # 배송준비에선 없는 키
                        print('mistakenInvoiceRegDateTime: ',mistakenInvoiceRegDateTime) # 배송준비에선 없는 키
                        print('mistakenInvoiceReason: ',mistakenInvoiceReason) # 배송준비에선 없는 키
                        print('purchaseDecisionExpectDateTime: ',purchaseDecisionExpectDateTime) # 배송준비에선 없는 키
                        print('purchaseDecisionExtensionDateTime: ',purchaseDecisionExtensionDateTime) # 배송준비에선 없는 키
                        print('purchaseDecisionExtensionReason: ',purchaseDecisionExtensionReason) # 배송준비에선 없는 키

                    print('sellerProductManagementCode: ',sellerProductManagementCode) 
                    print('sellerInternalCode1: ',sellerInternalCode1) 
                    print('sellerInternalCode2: ',sellerInternalCode2) 
                    print('deliveryBundleGroupSeq: ',deliveryBundleGroupSeq) 
                    print('deliveryFeeClass: ',deliveryFeeClass) 
                    print('deliveryFeeRatingClass: ',deliveryFeeRatingClass) 
                    print('deliveryFeeAmt: ',deliveryFeeAmt) 
                    print('remoteAreaCostChargeAmt: ',remoteAreaCostChargeAmt) 
                    print('deliveryFeeDiscountAmt: ',deliveryFeeDiscountAmt) 
                    print('receiverTelNo1: ',receiverTelNo1) 
                    print('receiverTelNo2: ',receiverTelNo2) 
                    print('receiverAddress: ',receiverAddress) 
                    print('orderMemberTelNo: ',orderMemberTelNo) 
                    print('receiverZipCode: ',receiverZipCode)
                    no+=1


    def orderViewSimple(self,res,menu):
        keys = res['data'].keys()
        for k in keys:
            if (len(res['data'][k]['elements']))==0:
                print(f'\n네이버 [ {menu} ] : 0건')  
            else:
                no = 1
                for i in res['data'][k]['elements']:
                    print(f'\n네이버 {menu} No.{no}   ' + '=='*60)    
                    productOrderNo = i['productOrderNo'] #상품주문번호
                    orderNo = i['orderNo'] #주문번호
                    dispatchDateTime = i['dispatchDateTime'] #발송처리일
                    orderStatus = i['orderStatus'] #주문상태
                    deliveryMethod = i['deliveryMethod'] #배송방법
                    deliveryCompanyName = i['deliveryCompanyName'] #택배사
                    # invoiceNo = i['invoiceNo'] #송장번호
                    # 배송트래킹 = https://sell.smartstore.naver.com/o/v3/n/sale/delivery/tracking/{deliveryNo}/{productOrderNo}
                    deliveryNo = i['deliveryNo']
                    saleChannelType = i['saleChannelType'] #판매채널
                    orderMemberName = i['orderMemberName'] #구매자
                    orderMemberId = i['orderMemberId'] #구매자ID
                    receiverName = i['receiverName'] #수취인
                    # claimStatus = i['claimStatus'] #클레임상태 # 배송준비에선 없는 키
                    productNo = i['productNo'] #상품번호        
                    # 스토어 상품페이지 https://smartstore.naver.com/otindustry/products/{productNo}
                    productUrl = i['productUrl']
                    productName = i['productName'] #상품명
                    productClass = i['productClass'] #상품종류
                    productOptionContents = i['productOptionContents'] #옵션정보
                    orderQuantity = i['orderQuantity'] #수량
                    productUnitPrice = i['productUnitPrice'] #상품가격
                    productOptionAmt = i['productOptionAmt'] #옵션가격
                    totalDiscountAmt = i['totalDiscountAmt'] # 상품별 할인액a
                    sellerDiscountAmt = i['sellerDiscountAmt'] #판매자 부담 할인액
                    productPayAmt = i['productPayAmt'] #상품별 총 주문금액
                    payDateTime = i['payDateTime'] #결제일

                    ## 배송준비에선 없는 키
                    lst = ['배송준비','신규주문']
                    if menu not in lst:
                        deliveryCompleteDateTime = i['deliveryCompleteDateTime'] #배송완료일
                        purchaseDecisionRequestDateTime = i['purchaseDecisionRequestDateTime'] #구매확정 요청일
                        purchaseDecisionRequestOperator = i['purchaseDecisionRequestOperator'] #구매확정 요청자
                        mistakenInvoiceYn = i['mistakenInvoiceYn'] # 문제송장 여부
                        mistakenInvoiceRegDateTime = i['mistakenInvoiceRegDateTime'] # 문제송장 등록일
                        mistakenInvoiceReason = i['mistakenInvoiceReason'] # 문제송장 등록사유
                        purchaseDecisionExpectDateTime = i['purchaseDecisionExpectDateTime'] # 자동구매확정 예정일
                        purchaseDecisionExtensionDateTime = i['purchaseDecisionExtensionDateTime'] # 구매확정연장 설정일
                        purchaseDecisionExtensionReason = i['purchaseDecisionExtensionReason'] # 구매확정연장 사유


                    sellerProductManagementCode = i['sellerProductManagementCode'] # 판매자 상품코드
                    sellerInternalCode1 = i['sellerInternalCode1'] # 판매자 내부코드1
                    sellerInternalCode2 = i['sellerInternalCode2'] # 판매자 내부코드2
                    deliveryBundleGroupSeq = i['deliveryBundleGroupSeq'] # 배송비 묶음번호
                    deliveryFeeClass = i['deliveryFeeClass'] # 배송비 형태
                    deliveryFeeRatingClass = i['deliveryFeeRatingClass'] # 배송비 유형
                    deliveryFeeAmt = i['deliveryFeeAmt'] # 배송비 합계
                    remoteAreaCostChargeAmt = i['remoteAreaCostChargeAmt'] # 제주/도서 추가배송비
                    deliveryFeeDiscountAmt = i['deliveryFeeDiscountAmt'] # 배송비 할인액
                    receiverTelNo1 = i['receiverTelNo1'] # 수취인연락처1
                    receiverTelNo2 = i['receiverTelNo2'] # 수취인연락처2
                    receiverAddress = i['receiverAddress'] # 배송지
                    orderMemberTelNo = i['orderMemberTelNo'] # 구매자연락처
                    receiverZipCode = i['receiverZipCode'] # 우편번호

                    print('orderNo: ',orderNo) 
                    print('orderStatus: ',orderStatus) 
                    # print('deliveryMethod: ',deliveryMethod) 
                    print('deliveryCompanyName: ',deliveryCompanyName) 
                    print('orderMemberName: ',orderMemberName) 
                    print('receiverName: ',receiverName) 
                    print('productNo: ',productNo) 
                    print('productName: ',productName) 
                    print('orderQuantity: ',orderQuantity) 
                    print('productUnitPrice: ',productUnitPrice) 
                    # print('productOptionAmt: ',productOptionAmt) 
                    # print('totalDiscountAmt: ',totalDiscountAmt) 
                    # print('sellerDiscountAmt: ',sellerDiscountAmt) 
                    print('productPayAmt: ',productPayAmt) 

                    print('deliveryFeeClass: ',deliveryFeeClass) 
                    print('deliveryFeeRatingClass: ',deliveryFeeRatingClass) 
                    print('deliveryFeeAmt: ',deliveryFeeAmt) 
                    print('receiverTelNo1: ',receiverTelNo1) 
                    print('receiverTelNo2: ',receiverTelNo2) 
                    print('receiverAddress: ',receiverAddress) 
                    print('receiverZipCode: ',receiverZipCode)
                    no+=1