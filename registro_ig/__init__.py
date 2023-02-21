from flask import Flask

# Creación de instancia Flask
app = Flask(__name__, instance_relative_config=True)
# Lectura de clave secreta de config.py
app.config.from_object("config")

from registro_ig.routes import *
