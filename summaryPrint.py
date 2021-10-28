from database import Database
db = Database()
def printDetail():
    var = input("\n\n1.세부내역전체 / 2.우체국용 / 3.제품찾기용 / ENTER:종료\n")
    
    if var == '1':
        db.orderSummaryPrint()
    elif var == '2':
        db.orderSummaryPost()
    elif var == '3':
        db.orderFindItem()
    else:
        print('종료합니다.')
        quit()
    printDetail()


printDetail()
