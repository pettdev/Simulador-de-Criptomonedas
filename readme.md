# CryptoDex: Simulador de mercado de criptomonedas

App desarrollada con Flask y SQLite3. CryptoDex es un _Simulador de servicios de intercambio de criptomonedas_, con precios en tiempo real a través de CoinAPI.

**Nota**: Este proyecto se desarrolló con fines educativos y evaluativos. No está destinado para su uso en producción.

## 1. Instalar dependencias

En su entorno virtual, instalar todas las dependencias de `requirements.txt`, ejecutando el siguiente comando en la terminal (Linux, MacOS, Windows): 
```
pip install -r requirements.txt
```

## 2. Renombrar .env_template

Renombrar el archivo `.env_template` a **.env**, agregar y guardar el siguiente código:
```
FLASK_APP=main.py
FLASK_DEBUG=true
```

## 3. Agregar key

- Renombrar el archivo `.config_template.py` a **config.py**.
- Obtener key (gratuita) de [Market Data API](https://docs.coinapi.io/market-data/) de CoinAPI
- Aplicar key en `config.py` renombrado dentro de las comillas dobles:

```
API_KEY="INGRESA TU API_KEY"
```

## 4. Ejecutar servidor

```
flask run
```

En caso de que el puerto 5000 esté ocupado, ejecutar el siguiente código para establecer el servidor en el puerto 5001, o el de su preferencia:

```
flask --app main run -p 5001
```

# Uso de la aplicación


Por defecto, el usuario obtendrá 1.000,00 EUR para comprar criptomonedas desde la primera vez que se ejecuta el servidor.

## Pasos para Comprar y Vender

1.  **Navegación:** Dirígete a la sección de "Compra/Venta".
2.  **Selección de Moneda de Venta:** Elige la moneda que deseas vender (EUR si es tu primera transacción).
3.  **Selección de Moneda de Compra:** Selecciona la moneda que deseas adquirir.
4.  **Cálculo:** Utiliza la calculadora integrada para determinar la cantidad a comprar. La calculadora muestra automáticamente la cantidad resultante antes de la confirmación.
5.  **Confirmación:** Revisa la transacción y haz clic en el botón "Confirmar" para completar la operación.

**Nota:** La calculadora te permite previsualizar la cantidad a comprar y el precio unitario antes de confirmar la transacción.

## Sección de Inicio

Una vez que completes tu primera transacción, serás redirigido a la sección de Inicio. Aquí, encontrarás un resumen detallado de tu última operación, incluyendo:
* Monedas involucradas (compra y venta).
* Precio de la transacción.
* Montos intercambiados.

Si aún no has realizado ninguna compra, la página de "Inicio" te mostrará una invitación para iniciar tu primera transacción.

## Sección de Status (Estado)

En esta sección, podrás acceder a analíticas básicas de tu actividad, tales como:
* Cantidad total invertida.
* Retorno de la inversión.
* Valor general de tu portafolio, expresado en Euros.

## Manejo de Errores

El sistema incluye validaciones para prevenir errores comunes. Los errores se mostrarán en la consola del navegador durante el desarrollo. Ejemplos de errores incluyen:

* Intentar comprar una moneda que aún no posees.
* Intentar vender una cantidad de moneda que excede tu saldo disponible.
