from app import email, app,db
from flask_mail import Mail, Message #Importar para enviar Mail
from flask_wtf import CSRFProtect #importar para proteccion CSRF
from flask import Flask, render_template, session, redirect, url_for
from models import *
from errors import getLogEvents
from threading import Thread
import os, time, smtplib
def confMsg(to, subject, template, **kwargs):
    #Configurar asunto, emisor y destinatarios
    msg = Message( subject, sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    #Seleccionar template para mensaje de texto plano
    msg.body = render_template(template + '.txt', **kwargs)
    #Seleccionar template para mensaje HTML
    msg.html = render_template(template + '.html', **kwargs)
    return msg



def enviarMailAsync(app, msg):
    #Espera 5 segundo, utilizada en el ejercicio para comprobar la diferencia entre sync y async
    time.sleep(5)
    #Se utiliza el contexto de la aplicación para tener acceso a la configuración
    with app.app_context():
        try:
    	    #Enviar mail
            email.send(msg)
            print("Mail enviado correctamente")

        #Mostrar errores por consola
        except smtplib.SMTPAuthenticationError as e:
            mensaje =str(e)
            getLogEvents(mensaje)
        except smtplib.SMTPServerDisconnected as e:
            mensaje =str(e)
            getLogEvents(mensaje)
        except smtplib.SMTPSenderRefused as e:
            mensaje =str(e)
            getLogEvents(mensaje)
        except smtplib.SMTPException as e:
            error= str(e)
            getLogEvents(error)
        except OSError as e:
            error=str(e)
            getLogEvents(error)



#Función para enviar mail
def sendMail(to, subject, template, **kwargs):
    #Crear configuración
    msg = confMsg(to, subject, template, **kwargs)
    #Crear hilo
    thr = Thread(target=enviarMailAsync, args=[app, msg])
    #Iniciar hilo
    thr.start()
