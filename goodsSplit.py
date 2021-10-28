from auction import Auction
from naver import Naver
from coupang import Coupang
from database import Database
import pymysql
import re

db = Database()
sql = "select * from products"
rows = db.excuteRow("select * from products",True)

no=1
for row in rows:
    print(f"\n\n{no}")
    print(row)
    no+=1
