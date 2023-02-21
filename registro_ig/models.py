import requests
from flask import redirect, url_for
from registro_ig.connection import *
from config import *


class ModelError(Exception()):
    pass


# Comunicación con API

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
            
            
# Métodos para manipulación de datos 

# Insertar información ingresada por el usuario
def insert_row(register):
    # Heredar de Connection, clase para manipular BBDD con SQLite3
    connection = Connection("INSERT INTO transactions (date, time, coin_from, q_from, coin_to, q_to, unit_price) VALUES (?, ?, ?, ?, ?, ?, ?)", register)
    connection.con.commit()
    connection.con.close()

# Mostrar la tabla de la base de datos
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

# Obtener el saldo total de cada moneda DE VENTA
def get_each_coin_from_balance():
    connection = Connection('SELECT coin_from, SUM (q_from) FROM transactions GROUP BY coin_from;')
    data = connection.res.fetchall()
    connection.con.commit()
    connection.con.close()
    
    return data

# Obtener el saldo total de cada moneda DE COMPRA
def get_each_coin_to_balance():
    connection = Connection('SELECT coin_to, SUM (q_to) FROM transactions GROUP BY coin_to;')
    data = connection.res.fetchall()
    connection.con.commit()
    connection.con.close()
    
    return data

# Obtener suma total de inversión cuya moneda sea EUROS
def get_eur_inversion():
    connection = Connection("SELECT coin_from, SUM (q_from) FROM transactions WHERE coin_from='EUR'")
    data = connection.res.fetchall()
    connection.con.commit()
    connection.con.close()
    
    return data

# Obtener suma total recuperado cuya moneda sea EUROS
def get_eur_recovery():
    connection = Connection("SELECT coin_to, SUM (q_to) FROM transactions WHERE coin_to='EUR'")
    data = connection.res.fetchall()
    connection.con.commit()
    connection.con.close()

    return data

# Obtener valor de compra
def get_acquisition_value(inversion, recovery):
    if isinstance(inversion, float) and isinstance(recovery, float):
        return inversion - recovery
    
    raise ModelError("Inversion or Recovery amount must be float type.")


# ([('BNB', 100.0), ('BTC', 0.05), ('ETH', 250.0), ('EUR', 11375.0)]
# [('BNB', 0.33506874), ('BTC', 0.53956739), ('ETH', 0.1893946), ('EUR', 1035.87947299), ('USDT', 389911.95221154), ('XRP', 77975.35918916)])

# PASO 1
# Se debe restar cada total de cantidad_to de cada moneda_to con...
# ... cada respectivo total cantidad_from de la misma moneda_from
# Es decir, total q_to de BTC - total q_from de BTC
# (Aplicado individualmente a cada moneda comprada o vendida)

# PASO 2
# Se debe consultar el precio en EUROS de cada respectiva moneda con CoinAPI
# multiplicar la cantidad de la criptomoneda o moneda en cuestión
# y obtener el total en euros de cada moneda_from y moneda_to multiplicado por...
# ... el precio unitario en euros de CoinAPI

# PASO 3
# Luego de haber obtenido cada euro equivalente para cada moneda...
# ... debe quedar una lista de monedas (sin importar si son coin_from o coin_to)...
# que se deben sumar, y este total es el Valor Actual

# Obtener el saldo de cada moneda (uniendo coin_from y coin_to) equivalente en EUR
def get_each_coin_eur_balance(coin_from_list, coin_to_list, Exchange_Class):
    if isinstance(coin_from_list, list) and isinstance(coin_to_list, list):
        output = {}
        exch = Exchange_Class
        
        coin_from_dict = dict(coin_from_list)
        coin_to_dict = dict(coin_to_list)
        
        # Selecciona el diccionario con mayor número de monedas
        
        if len(coin_from_dict) > len(coin_to_dict):
            all_coins = coin_from_dict
            other_dict = coin_to_dict
        else:
            all_coins = coin_to_dict
            other_dict = coin_from_dict
        
        # Agrega las monedas en output
        
        for coin in all_coins:
            
            # Si está en el otro diccionario también, agrega la moneda y obtén EUR
            if coin in other_dict:
                
                # Agregar moneda si no es EUR a output
                if coin != 'EUR':
                    
                    # Obtener tasa con CoinAPI
                    exch.get_rate(coin, 'EUR', API_KEY)
                    output[coin] = (coin_to_dict[coin] - coin_from_dict.get(coin, 0)) * exch.rate
                    
                # Agregar EUR en ouput y no usar la API
                else:
                    output[coin] = coin_to_dict[coin] - coin_from_dict.get(coin, 0)
                    
            # Si no está en el otro diccionario, agrega la moneda y obtén EUR
            else:
                 # obtener tasa con CoinAPI
                exch.get_rate(coin, 'EUR', API_KEY)
                output[coin] = all_coins[coin] * exch.rate      
                
        return output
    
    raise ModelError('The coins variable must be a list object')


#get_each_coin_eur_balance(get_each_coin_from_balance(), get_each_coin_to_balance(), Exchange())


'''Para ello debemos determinar que criptomonedas tenemos y que cantidad de las mismas.

BTC: Suma de cantidades to - Suma de cantidades from → 0,1 - 0,05 → 0,05 BTC
ETH: Suma de cantidades to - Suma de cantidades from → 2 - 1 → 1 ETH'''
# print("INVERSIÓN:", get_eur_inversion())
# print("RECUPERACIÓN:", get_eur_recovery())
# print('TOTAL Q_tO DE CADA MONEDA_TO', get_each_coin_to_balance())
# print('TOTAL Q_FROM DE CADA MONEDA_FROM', get_each_coin_from_balance())
# print("#####################################################################################################\n",
# get_each_coin_eur_balance(get_each_coin_from_balance(),get_each_coin_to_balance()),
# "\n#################################################################################################")