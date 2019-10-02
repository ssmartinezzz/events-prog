from flask import Flask
from flask_sqlalchemy import SQLAlchemy #Incluye sqlAlchemy
from sqlalchemy import or_

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#Configuración de conexion de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/programacionej'
#Instancia que representa la base de datos
db = SQLAlchemy(app)

#Ejecutar pip install -r requirements.txt


if __name__ == '__main__': #Asegura que solo se ejectue el servidor cuando se ejecute el script directamente
    from routes import *
    app.run(port = 8000, debug = True)
