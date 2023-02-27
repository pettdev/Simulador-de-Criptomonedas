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
            exchangeError = r.json()['error']
            raise ModelError(f"Status: {r.status_code}. Error: {exchangeError}")

    def get_unit_price(self, q_from, q_to):
            return q_from/q_to
            

# Métodos para manipulación de datos 

# Insertar información ingresada por el usuario
def insert_row(register):
    # Heredar de Connection, clase para manipular BBDD con SQLite3
    connection = Connection("INSERT INTO transactions (date, time, coin_from, q_from, coin_to, q_to, unit_price) VALUES (?, ?, ?, ?, ?, ?, ?)", register)
    connection.con.commit()
    connection.con.close()

# Mostrar la tabla de la base de datos
def table_display():
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


# Obtener suma total de INVERSIÓN cuya moneda sea EUROS
def get_eur_inversion():
    connection = Connection("SELECT coin_from, SUM (q_from) FROM transactions WHERE coin_from='EUR'")
    data = connection.res.fetchall()
    connection.con.commit()
    connection.con.close()
    
    return data


# Obtener suma total RECUPERADO cuya moneda sea EUROS
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


# Obtener el saldo total de cada coin_from en euros
def get_each_coin_from_balance():
    connection = Connection('SELECT coin_from, SUM (q_from) FROM transactions GROUP BY coin_from;')
    data = connection.res.fetchall()
    connection.con.commit()
    connection.con.close()
    
    return data


# Obtener el saldo total de cada coin_to en euros
def get_each_coin_to_balance():
    connection = Connection('SELECT coin_to, SUM (q_to) FROM transactions GROUP BY coin_to;')
    data = connection.res.fetchall()
    connection.con.commit()
    connection.con.close()
    
    return data


def get_all_coins_balances():
    coin_to_coins = dict(get_each_coin_to_balance())
    coin_from_coins = dict(get_each_coin_from_balance())

    # Unir diccionarios en sold_coins
    for key, value in coin_to_coins.items():
        coin_from_coins[key] = value
        
    return coin_from_coins


def get_all_purchased_assets():
    connection = Connection('SELECT asset, amount FROM assets;')
    data = connection.res.fetchall()
    connection.con.commit()
    connection.con.close()
    
    return dict(data)


def increment_amount(amount:float, asset:str):
    connection = Connection(f"UPDATE assets set amount= amount + {amount} WHERE asset='{asset}'")
    connection.con.commit()
    connection.con.close()

    
def decrement_amount(amount:float, asset:str):
    connection = Connection(f"UPDATE assets set amount= amount - {amount} WHERE asset='{asset}'")
    connection.con.commit()
    connection.con.close()


def register_asset(register):
    connection = Connection("INSERT INTO assets (asset, amount) VALUES (?, ?)", register)
    connection.con.commit()
    connection.con.close()


# Obtener Valor Actual de la cuenta en euros
def get_current_value(coin_from_list, coin_to_list, ExchangeService):
    
    if isinstance(coin_from_list, list) and isinstance(coin_to_list, list):
        output = {}
        total = 0 # Valor actual (valor total de cartera en euros)
        exch = ExchangeService
        
        coin_from_dict = dict(coin_from_list)
        coin_to_dict = dict(coin_to_list)
        
        ## Selecciona el diccionario con mayor número de monedas
        
        if len(coin_from_dict) > len(coin_to_dict):
            all_coins = coin_from_dict
            other_dict = coin_to_dict
        else:
            all_coins = coin_to_dict
            other_dict = coin_from_dict
        
        ## Agrega las monedas en output
        
        for coin in all_coins:
            
            # Si está en el otro diccionario también, agrega la moneda y obtén EUR
            if coin in other_dict:
                
                # Agregar moneda si no es EUR a output
                if coin != "EUR":
                    
                    # Obtener tasa con CoinAPI
                    exch.get_rate(coin, "EUR", API_KEY)
                    euros = (coin_to_dict[coin] - coin_from_dict.get(coin, 0)) * exch.rate
                    output[coin] = euros
                    total += euros
                    
                # Agregar EUR en ouput y no usar la API
                else:
                    euros = coin_to_dict[coin] - coin_from_dict.get(coin, 0)
                    output[coin] = euros
                    total += euros
                    
            # Si no está en el otro diccionario, agrega la moneda y obtén EUR
            else:
                # Obtener tasa con CoinAPI
                exch.get_rate(coin, "EUR", API_KEY)
                euros = all_coins[coin] * exch.rate
                output[coin] = euros
                total += euros
        
        output["total_value"] = total
        
        return output["total_value"]
    
    raise ModelError("The coins variable must be a list object")


class AssetTradeValidator:
    def __init__(self):
        # Saldos de monedas
        self.coins_wallet = get_all_coins_balances() # transactions table
        self.purchased_assets = get_all_purchased_assets() # assets table
    
    
    def set_balance(self, account_currency, account_balance):
        if account_currency not in self.purchased_assets:
            return register_asset([account_currency, account_balance]) # Verificar si retorna True si todo sale bien


    def validate_selling_asset(self, asset, amount):
        # VERIFICAR EXISTENCIA
        # Si existe en assets table
        if asset in self.purchased_assets:
            # Verificar si se puede adquirir
            if amount > self.purchased_assets[asset]:
                print(f'selling_asset error: insufficient {asset} balance. Price is {amount}, but you only have {self.purchased_assets[asset]} {asset}')
                return False
            elif self.purchased_assets[asset] - amount > self.purchased_assets[asset]:
                print(f'selling_asset error: the {asset} balance cannot be negative ({amount}). Please, verify.')
                return False
            # Si no hay problemas, descontar
            else:
                decrement_amount(amount, asset)
                return True
        # Si no existe en assets table
        print(f"selling_asset error: nonexistent {asset} asset.")
        return False
            
    
    def validate_buying_asset(self, asset, amount):
        # VERIFICAR EXISTENCIA
        if asset in self.purchased_assets:
            # Si existe, incrementar
            increment_amount(amount, asset)
        else:
            # De lo contrario, registrar
            register_asset([asset, amount])
        return True
    
    def is_validated(self, selling_asset, selling_amount, buying_asset, buying_amount):
        return self.validate_selling_asset(selling_asset,selling_amount) and self.validate_buying_asset(buying_asset,buying_amount) and selling_asset != buying_asset