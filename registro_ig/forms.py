from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, DateField, FloatField
from wtforms.validators import DataRequired, ValidationError


# Validación de campos
def validate_q_from(form, field):
    # Aplicar aquí mensajes de error de saldo y saldo insufciente proximamente
    if field.data < 0:
        raise ValidationError("Cantidad a vender: Por favor, ingrese una cantidad válida.")
    elif field.data == 0:
        raise ValidationError("Cantidad a vender: La cantidad debe ser mayor a cero.")
    

class PurchaseForm(FlaskForm):
    coin_from = SelectField('Moneda a vender:',
                                choices=[('EUR'), ('BTC'), ('ETH'), ('USDT'), ('BNB'), ('XRP'), ('ADA'), ('SOL'), ('DOT'), ('MATIC')],
                                validators=[DataRequired(message='Moneda a vender: campo obligatorio. Debe seleccionar una opción.')])
    
    coin_to = SelectField('Moneda a comprar:',
                            choices=[('BTC'), ('ETH'), ('USDT'), ('BNB'), ('EUR'), ('XRP'), ('ADA'), ('SOL'), ('DOT'), ('MATIC')],
                            validators=[DataRequired(message='Moneda a comprar: campo obligatorio. Debe seleccionar una opción.')])
    
    q_from = FloatField('Cantidad a vender:', validators=[validate_q_from])
    
    q_to = FloatField('Cantidad a comprar:',
                            validators=[DataRequired(message='Cantidad a comprar: campo obligatorio.')],
                            render_kw={'readonly': True}) # Campo de solo lectura
    
    unit_price = FloatField('Precio unitario (P.U.):',
                                validators=[DataRequired(message='Precio unitario (P.U.): campo obligatorio.')],
                                render_kw={'readonly': True}) # Campo de solo lectura
    
    submit_button = SubmitField('Confirmar')