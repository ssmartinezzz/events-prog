from app import email, app, db
from flask_mail import Mail, Message  # Importar para enviar Mail
from flask_wtf import CSRFProtect  # importar para proteccion CSRF
from flask import Flask, render_template, session, redirect, url_for
from models import *
from errors import getLogEvents
from threading import Thread
import os
import time
import smtplib


def sendMail(to, subject, template, **kwargs):
    # Configurar asunto, emisor y destinatarios
    msg = Message(
        subject, sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to]) # Configuro el mensaje: subject el asunto , sender: Mail enviante obtenido del entorno virtual, con los destinatarios
    # Seleccionar template para mensaje de texto plano
    msg.body = render_template('mail/' + template + '.txt', **kwargs) #Configura el texto plano del mensaje buscandolo en nuestra carpeta de templates
    # Seleccionar template para mensaje HTML
    msg.html = render_template('mail/' + template + '.html', **kwargs)
    thr = Thread(target=threadMail, args=[app, msg])  #Crea un hilo que ejecuta en background el envio del mail configurado aca.
    # Iniciar hilo para mandar mail rápido
    thr.start()


def threadMail(app, msg, **kwargs):
    # Espera 5 segundo, utilizada en el ejercicio para comprobar la diferencia entre sync y async
    time.sleep(5)
    # Se utiliza el contexto de la aplicación para tener acceso a la configuración
    with app.app_context():
        try:
            # Enviar mail
            email.send(msg)
            print("Mail enviado correctamente")

        # Mostrar errores por consola
        except smtplib.SMTPAuthenticationError as e:
            # Parseo el error obtenido del mail (este caso credenciales) a un string
            mensaje = str(e)
            # Al ser el mensaje una string lo puedo mandar como parametro a mi funcion que maneja el log de errores
            getLogEvents(mensaje)
        except smtplib.SMTPServerDisconnected as e:
            mensaje = str(e)
            getLogEvents(mensaje)
        except smtplib.SMTPSenderRefused as e:
            mensaje = str(e)
            getLogEvents(mensaje)
        except smtplib.SMTPException as e:
            error = str(e)
            getLogEvents(error)
        except OSError as e:
            error = str(e)
            getLogEvents(error)


def registredUser(email): # Funcion que recibe un email por formularios si existen coincidencias con dicho mail y no permitir crear esa cuenta
    auxiliar = False
    if db.session.query(Usuario).filter(Usuario.email.ilike(email)).count() == 0: #ilike detecta si hay concidencias con el string del email en la base de datos
        auxiliar = True
    return auxiliar
