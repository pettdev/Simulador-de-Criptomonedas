from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, DateField, FloatField
from wtforms.validators import DataRequired


class PurchaseForm(FlaskForm):
    
    
    coin_from = SelectField('Moneda a vender:',
                                choices=[('EUR'), ('BTC'), ('ETH'), ('USDT'), ('BNB'), ('XRP'), ('ADA'), ('SOL'), ('DOT'), ('MATIC')],
                                validators=[DataRequired(message='Moneda a vender: campo obligatorio. Debe seleccionar una opción.')])
    
    coin_to = SelectField('Moneda a comprar:',
                            choices=[('BTC'), ('ETH'), ('USDT'), ('BNB'), ('EUR'), ('XRP'), ('ADA'), ('SOL'), ('DOT'), ('MATIC')],
                            validators=[DataRequired(message='Moneda a comprar: campo obligatorio. Debe seleccionar una opción.')])
    
    q_from = FloatField('Cantidad a vender:',
                            validators=[DataRequired(message='Cantidad a vender: campo obligatorio. Debe completar este campo.')])
    
    q_to = StringField('Cantidad a comprar:',
                            validators=[DataRequired(message='Cantidad a comprar: campo obligatorio.')],
                            render_kw={'readonly': True}) # Campo de solo lectura
    
    unit_price = FloatField('Precio unitario (P.U.):',
                                validators=[DataRequired(message='Precio unitario (P.U.): campo obligatorio.')],
                                render_kw={'readonly': True}) # Campo de solo lectura
    
    submit_button = SubmitField('Confirmar')