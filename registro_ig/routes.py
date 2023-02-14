from registro_ig import app
from flask import render_template, request, redirect, url_for
from registro_ig.models import *
from registro_ig.forms import PurchaseForm
from config import *
from datetime import datetime


@app.route("/")
def index():
    
    register = select_table()
    
    return render_template('index.html', pageTitle='Registro de movimientos', inicio="secondary", page='index.html', data=register)


@app.route("/purchase", methods=['GET', 'POST'])
def purchase():
    form = PurchaseForm()
    
    if request.method == 'GET': ### Método GET ###
        
        return render_template('purchase.html', form=form, pageTitle='Compra de criptos', compra="secondary", page='purchase.html', form_values=None)
    
    else: ### Métodos POST ###
        
        # Obtener Fecha y Hora
        now = datetime.now()
        time = now.strftime("%H:%M:%S")
        date = now.strftime("%Y-%m-%d")

        ## POST Botón ##
        if 'submit_button' in request.form:
        
            if form.validate_on_submit():
                
                insert_row([
                    date,
                    time,
                    form.coin_from.data,
                    form.q_from.data,
                    form.coin_to.data,
                    form.q_to.data,
                    form.unit_price.data
                    ])
                
                return redirect(url_for('index'))
            
            return render_template('purchase.html', form=form, pageTitle='Compra de criptos', compra="secondary", page='purchase.html')
            
            
        ## POST Calculadora ##
        
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
            send_data = {
                "q_to_value": q_to,
                "unit_price_value": unit_price
                }
            
            return render_template('purchase.html', form=form, form_values=send_data, pageTitle='Compra de criptos', compra="secondary", page='purchase.html')
            

@app.route("/status")
def status():
    
    invertido = None
    recuperado = None
    valor_compra = None
    valor_actual = None
    
    return render_template('status.html', pageTitle='Estado de la inversión', status="secondary", page='status.html', invertido=invertido, recuperado=recuperado, valor_compra=valor_compra, valor_actual=valor_actual)

# Validación de errores

def validate_q_from(form,field):
    if field.data < 0:
        raise ValidationError("Cantidad a vender: Por favor, ingrese una cantidad válida.")
    if field.data == 0:
        raise ValidationError("Cantidad a vender: La cantidad debe ser mayor a cero.")
    
def validate_coin_balances(form, field, coin):
    pass