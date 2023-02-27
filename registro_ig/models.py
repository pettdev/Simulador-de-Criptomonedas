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
        
        return output
    
    raise ModelError("The coins variable must be a list object")

# print(get_current_value(get_each_coin_from_balance(), get_each_coin_to_balance(), Exchange()))


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


class AssetTradeValidator:
    def __init__(self, eur_balance):
        # Saldos de monedas
        purchased_coins = dict(get_each_coin_to_balance()) # Compradas
        sold_coins = dict(get_each_coin_from_balance()) # Vendidas

        # Unir diccionarios en sold_coins
        for key, value in purchased_coins.items():
            sold_coins[key] = value
        
        self.eur_balance = eur_balance
        self.balances = sold_coins

    def validate_eur(self, selling_amount):
        
        # Continúa solo si el balance de euros existe
        if self.eur_balance:
            # Agregar moneda euros si no existe
            if 'EUR' not in self.balances:
                self.balances['EUR'] = 0
                register_asset(['EUR', 0])

            # Euros disponibles: Saldo del Usuario - Total Euros gastados (de la BBDD)
            eur_available = self.eur_balance - self.balances['EUR']

            # Si la cantidad de venta > saldo disponible de euros:
            if selling_amount > eur_available:
                print(f"\nNot enough EUR balance. The cost is {selling_amount}, but you have only {eur_available} EUR.\n")
                return False
            # Si la diferencia del saldo disponible y el gasto total es negativa:
            elif eur_available < 0:
                print(f"Fondos insuficientes. Por favor, recargar.")
                return False
            
            return True
        print("Nonexistent euro balance.")
        return False


    def validate_trade(self, asset, amount, buy): 
        # Si es una venta
        if not buy:
            # Si no existe como moneda de compra, no permitir
            if asset not in self.balances:
                # Permitir agregar EUR por primera vez
                if asset == 'EUR':
                    return True
                return False
            # Aplicar validaciones al monto de todas las monedas (excepto EUR)
            elif asset != 'EUR':
                decrement_amount(amount, asset)
                # No puede superar el balance
                if amount > self.balances[asset]:
                    print(f"Not enough {asset} balance. The cost is {amount}, but you have only {self.balances[asset]} {asset}.")
                    return False
                # No puede ser negativo
                elif amount < 0:
                    print(f"The amount can't be a negative balance. Your current EUR balance is {self.balances[asset]} {asset}.")
                    return False
            else:
                # Si no existe, sumar
                increment_amount(amount, asset)
                
        # Si es una compra
        else:
            # Superada la validación sell, permitir agregar moneda comprada
            if asset not in self.balances:
                register_asset([asset, amount])
            else:
                increment_amount(amount, asset)
        return True
        
    
    def buy(self, asset, amount, buy=True):
        if self.validate_trade(asset, amount, buy):
            return True
        print(f"Buying_asset error: Verify {asset} amount.")
        return False
    
    
    def sell(self, asset, amount, buy=False):
        if self.validate_trade(asset, amount, buy):
            if asset == 'EUR':
                return self.validate_eur(amount)

            return True
        print(f"Selling_asset error: Verify {asset} amount.")
        return False


    def execute(self, selling_asset, selling_amount, buying_asset, buying_amount):
        if selling_asset == buying_asset:
            print("No puedes comprar la misma moneda.")
            return False
        return self.sell(selling_asset, selling_amount) and self.buy(buying_asset, buying_amount)
    
    
    def get_asset_balance(self, asset):
        return self.balances[asset]
    
    
    