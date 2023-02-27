from registro_ig import app
from flask import render_template, request, redirect, url_for
from registro_ig.models import *
from registro_ig.forms import PurchaseForm
from datetime import datetime
from config import *


@app.route("/")
def index():
    register = table_display()
    
    return render_template('index.html', pageTitle='Registro de movimientos', inicio="secondary", page='index', data=register)


@app.route("/purchase", methods=['GET', 'POST'])
def purchase():
    form = PurchaseForm()
    
    # # # Método GET # # #
    if request.method == 'GET':
        
        return render_template('purchase.html', form=form, pageTitle='Compra de criptos', compra="secondary", page='purchase', form_values=None)
    
    # # # Método POST # # #
    eur_balance = 1000 # Balance de euros
    
    # Validador de Cartera
    validate_wallet = AssetTradeValidator(eur_balance)
    
    # # POST - Botón de formulario # #
    if 'submit_button' in request.form:
        coin_from = form.coin_from.data
        q_from = form.q_from.data
        coin_to = form.coin_to.data
        q_to = form.q_to.data
        unit_price = form.unit_price.data

        if form.validate_on_submit():
            
             # Obtener Fecha y Hora
            now = datetime.now()
            time = now.strftime("%H:%M:%S")
            date = now.strftime("%Y-%m-%d")
            
            print('##### Ésto nunca cambiará ########## Here /////// Solo cuando la tabla cambie ///////',
                validate_wallet.balances)
                    
            if validate_wallet.execute(coin_from, q_from, coin_to, q_to):
                insert_row([date, time, coin_from, q_from, coin_to, q_to, unit_price])

                # SERÍA BUENO QUE FUNCIONARA EL FLASH para accesibilidad de errores.
                return redirect(url_for('index'))
    
        return render_template('purchase.html', form=form, pageTitle='Compra de criptos', compra="secondary", page='purchase', form_values=None)
        
        
    # # POST - Calculadora # #
    if "calculate.x" and "calculate.y" in request.form:
        
        # Definir elecciones del usuario
        coin_from = form.coin_from.data
        q_from = form.q_from.data
        coin_to = form.coin_to.data
        
        # Obtener q_to y p_u
        exch = Exchange()
        exch.get_rate(coin_from, coin_to, API_KEY)
        q_to = round(exch.rate * q_from, 8) # Redondeo hasta 8 decimales
        
        exch.get_unit_price(q_from, q_to)
        unit_price = round(exch.unit_price, 8)

        # Datos a enviar al formulario
        data_retrieved = {
            "q_to_value": q_to,
            "unit_price_value": unit_price
            }
        
        return render_template('purchase.html', form=form, form_values=data_retrieved, pageTitle='Compra de criptos', compra="secondary", page='purchase')
            

@app.route("/status")
def status():
    
    invertido = None
    recuperado = None
    valor_compra = None
    valor_actual = None
    
    return render_template('status.html', pageTitle='Estado de la inversión', status="secondary", page='status', invertido=invertido, recuperado=recuperado, valor_compra=valor_compra, valor_actual=valor_actual)
