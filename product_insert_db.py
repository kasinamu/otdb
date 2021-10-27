from auction import Auction
import pymysql
from database import Database

db = Database()
db.createPDTabel()

# ac = Auction()

# pdno = 1

# for p in range(1,100):
#     res = ac.getPd100(p)
#     count = len(res['data'])
#     for i in res['data']:
#         print(pdno)
#         db.insertProduct(i)
#         pdno +=1
        
#         if pdno == 7299:
#             break


conn = db.connect()
cur = conn.cursor()
str = '0520'
sql = f"SELECT * FROM product WHERE goodsCode like '%{str}'"
cur.execute(sql)
rows = cur.fetchall()
no = 1
for row in rows:
    print(no, '='*50)
    print(row)
    print('\n')
    no+=1