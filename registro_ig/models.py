from registro_ig.connection import *
import requests
from flask import redirect, url_for


# Métodos para manipulación de datos 


def insert_row(register):
    # Heredar de Connection, clase para manipular BBDD con SQLite3
    connection = Connection("INSERT INTO transactions (date, time, coin_from, q_from, coin_to, q_to, unit_price) VALUES (?, ?, ?, ?, ?, ?, ?)", register)
    connection.con.commit()
    connection.con.close()


def select_table():
    connection = Connection('SELECT date, time, coin_from, q_from, coin_to, q_to, unit_price FROM transactions ORDER BY date;')
    rows = connection.res.fetchall()
    fields = connection.res.description
    
    results = [] # lista para guardar diccionario
   
    for row in rows:
        data = {} # diccionario para cada registro
        position = 0 # position de columna

        for field in fields:
            data[field[0]] = row[position]
            position += 1
        results.append(data)

    connection.con.commit()
    connection.con.close()

    return results


def get_each_coin_from_balance():
    connection = Connection('SELECT coin_from, SUM (q_from) FROM transactions GROUP BY coin_from;')
    data = connection.res.fetchall()

    connection.con.commit()
    connection.con.close()
    
    return data


# Comunicación con API 

print(get_each_coin_from_balance())

class ModelError(Exception()):
    pass

class Exchange():
    
    def get_rate(self, base, quota, API_KEY):
        r = requests.get(f'https://rest.coinapi.io/v1/exchangerate/{base}/{quota}/?apikey={API_KEY}')
        
        if r.status_code == 200:
            exchangeInfo = r.json()
            self.rate = exchangeInfo['rate']
            self.time = exchangeInfo['time']

        else:
            raise ModelError(f"Status: {r.status_code}. Error: {self.exchangeInfo['error']}")

    def get_unit_price(self, q_from, q_to):
            self.unit_price = q_from/q_to