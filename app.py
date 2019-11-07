from flask import Flask
from flask_sqlalchemy import SQLAlchemy #Incluye sqlAlchemy
from flask_mail import Mail, Message #
from sqlalchemy import or_
import os
from flask_login import LoginManager
from dotenv import load_dotenv


from flask_wtf import CSRFProtect
app = Flask(__name__)
load_dotenv()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#Configuración de conexion de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'+os.getenv('DB_USERNAME')+':'+os.getenv('DB_PASS')+'@localhost/programacionej'
#Instancia que representa la base de datos
app.config['MAIL_HOSTNAME'] = 'localhost'
#Dirección del servidor mail utilizado
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
#Puerto del servidor mail saliente SMTP
app.config['MAIL_PORT'] = 587
#Especificar conexión con SSL/TLS
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SENDER'] = 'EventZ <no-replyeventZ@gmail.com>'
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
email= Mail(app)
login_manager=LoginManager(app)
def admin_required():
	return current_user.es_admin()


if __name__ == '__main__':#Asegura que solo se ejectue el servidor cuando se ejecute el script directamente
	from routes import *
	from errors import *
	from apiroutes import *
	app.run(port = 5000, debug = True)
