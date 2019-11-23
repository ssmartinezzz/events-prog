from flask import Flask
from flask_sqlalchemy import SQLAlchemy #Incluye sqlAlchemy
from flask_mail import Mail, Message
from sqlalchemy import or_
import os
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_wtf import CSRFProtect
app = Flask(__name__)
load_dotenv()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True #Configuracion para que el ORM detecte las modificaciones que realicemos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'+os.getenv('DB_USERNAME')+':'+os.getenv('DB_PASS')+'@localhost/programacionej' #Configuración de las conexiones de  bases del tipo mysql, hay una variacion  porque hay que tener en cuenta que para que no quede hardcodeado usamos el enviroment
#Instancia que representa la base de datos
app.config['MAIL_HOSTNAME'] = 'localhost' #Dirección del servidor mail utilizado
app.config['MAIL_SERVER'] = 'smtp.googlemail.com' #Configuramos el servidor de mail que utilizaremos por default es el localhost, pero nostros usamos el de google
app.config['MAIL_PORT'] = 587#Puerto del servidor mail saliente SMTP
app.config['MAIL_USE_TLS'] = True #Especificar conexión con SSL/TLS diferentes tipos de protocolos para las seguridad con el servidor
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')#Configura el mail con el que enviaremos los mails a nuestros usuarios, por temas de seguridad para que no quede hardcodeado lo almacenamos en el env
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')#Configuramos la password del mail nuestro con el que estamos enviando correos, almacenada en el env
app.config['FLASKY_MAIL_SENDER'] = 'EventZ <no-replyeventZ@gmail.com>'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') #Trae la clave secreta del env, para que ninguna api de terceros se haga pasar por nosotros. Esta clave secreta se comprueba en varios lugares por el motivo antes mencionado
csrf = CSRFProtect(app)# Es util usar un token CSRF, permite que nuestra aplicación haga las peticiones desde nuestro sitio. En esta linea estamos Instanciando el modulo de flask que nos permite esta funcionalidad
db = SQLAlchemy(app) #Creamos el objeto que tiene todas las funcionalidades del ORM
email= Mail(app)  #Creamos el objetos que tiene las funcionalidades de los mail.
login_manager=LoginManager(app)# Instanciamos el objeto del modulo Flask Login llamado login manager el cual nos permite operar con las sesiones

if __name__ == '__main__':#Asegura que solo se ejectue el servidor cuando se ejecute el script directamente
	from routes import *
	from errors import *
	from apiroutes import *
	app.run(port = 5000, debug = False)
