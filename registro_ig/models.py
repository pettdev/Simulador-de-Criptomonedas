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


# Obtener Valor Actual de la cuenta en euros
def get_current_value(coin_from_list, coin_to_list, ExchangeClass):
    
    if isinstance(coin_from_list, list) and isinstance(coin_to_list, list):
        output = {}
        total = 0 # Valor actual (valor total de cartera en euros)
        exch = ExchangeClass
        
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
        
        return output
    
    raise ModelError("The coins variable must be a list object")


#print(get_current_value(get_each_coin_from_balance(), get_each_coin_to_balance(), Exchange()))

class AssetPurchaseValidator:
    def init(self, eur_balance):
        self.balances = {'EUR': eur_balance}
        self.eur_balance = self.balances['EUR']
        
        
    def validateTrade(self, asset, amount):
        if asset not in self.balances:     
            self.balances[asset] = 0
        if amount > self.balances[asset]:
            print(f"Not enough {asset} balance. The cost is {amount}, but you have only {self.balances[asset]} {asset}.")
            return False
        elif amount < 0:
            print(f"The amount can't be a negative balance. Your current EUR balance is {self.balances[asset]} {asset}.")
            return False
        return True
        
    
    def buy(self, asset, amount):
        if self.validateTrade(asset, amount):
            if asset == 'EUR':
                self.eur_balance += amount
            else:    
                self.balances[asset] += amount
        raise ModelError(f'Error: Verify buying asset ({asset}) amount or asset name.')
    
    
    def sell(self, asset, amount):
        if self.validateTrade(asset, amount):
            if asset == 'EUR':
                self.eur_balance -= amount
            else:
                self.balances[asset] -= amount
        raise ModelError(f'Error: Verify selling asset ({asset}) amount or asset name.')


    def trade(self, buying_asset, buying_amount, selling_asset, selling_amount):
        # buying asset is coin_to
        # buying amount is q_to
        self.buy(buying_asset, buying_amount)
    
        # selling asset is coin_from
        # selling amount is q_from
        self.sell(selling_asset, selling_amount)
        
        return True
        
        
    
    def get_asset_balance(self, asset):
        return self.balances[asset]