# CryptoDex: Simulador de mercado de criptomonedas
Aplicación WEB desarrollado con Flask y el motor de BBDD de SQLite3, en Python. CryptoDex es un _Simulador de servicios de intercambio de criptomonedas_, con precios en tiempo real a través de CoinAPI.

## 1. ¿Cómo instalar la aplicación?:
En su entorno virtual, instalar todas las dependencias de `requirements.txt`, ejecutando el siguiente comando en la terminal: 
```
pip install -r requirements.txt
```
Aquí puedes encontrar la librería utilizada: [Flask](https://flask.palletsprojects.com/en/2.2.x/)

## 2. Renombrar el archivo .env_template a .env y agregar las siguientes lineas:
```
FLASK_APP=main.py
FLASK_DEBUG=true
```
## 3. Renombrar config_template.py a config.py y agregar tu clave de API:
En ésta parte deberás obtener tu *API_KEY* gratuita en la [Documentación de CoinAPI](https://docs.coinapi.io/). Reemplaza tu clave de API obtenida en tu correo electrónico y reemplaza el contenido dentro de las comillas en la siguiente línea del código config.py renombrado:

```
API_KEY="INGRESA TU API_KEY"
```
## 4. Ejecutar servidor y comienzar a testear:
```
flask run
```
# Comandos opcionales:
Ten en cuenta que los siguientes comandos no son necesarios si usas el archivo `.env`, sin embargo, éstos comandos te ofrecen mayor autonomía en el servidor.
## - Comando para ejecutar el servidor:
```
flask --app main run
```

## - Comando para actualizar el servidor con cambios de codigo en tiempo real:
Para observar el proceso del código durante su ejecución en tiempo real.
```
flask --app main --debug run
```

## - Comando especial para lanzar el servidor en un puerto diferente:
En caso de que el puerto predeterminado (5000) esté ocupado, puedes intentar ejecutar este código para establecer el servidor en el puerto 5001, y otro según lo que te funcione.

```
flask --app main run -p 5001
```

## - Comando para lanzar en modo debug y con puerto específico:
```
flask --app main --debug run -p 5001
```