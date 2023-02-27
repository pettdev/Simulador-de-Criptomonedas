import sqlite3 as sql
from config import *

class Connection:
    def __init__(self,query,args=[]):
        self.con = sql.connect(ORIGIN_DATA)
        self.cur = self.con.cursor()
        self.res = self.cur.execute(query,args)
        

def createDB():
    con = sql.connect('transactions.db')
    con.commit()
    con.close()


def createTradingTable():
    con = sql.connect('transactions.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    coin_from TEXT NOT NULL,
                    q_from REAL NOT NULL,
                    coin_to TEXT NOT NULL,
                    q_to REAL NOT NULL,
                    unit_price REAL NOT NULL
                )''')
    con.commit()
    con.close()


def createAssetsTable():
    con = sql.connect('transactions.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    asset TEXT NOT NULL,
                    amount REAL NOT NULL
                )''')
    con.commit()
    con.close()

def executeAll():
    createDB()
    createTradingTable()
    createAssetsTable()

#executeAll()