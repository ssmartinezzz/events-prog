from flask import render_template,request, jsonify
from app import app
import datetime
#Manejar error de página no encontrada
@app.errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:#Si la solicitud acepta json y no HTML
        response = jsonify({'error': 'not found'})#Responder con JSON
        response.status_code = 404
        return response
    return render_template('404.html'), 404#Sino responder con template HTML

#Manejar error de error interno
@app.errorhandler(500)
def internal_server_error(e):
    print(e)
    getLogEvents(e)
    #Si la solicitud acepta json y no HTML
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        #Responder con JSON
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    #Sino responder con template HTML
    return render_template('500.html'), 500

def getLogEvents(error):
    log=open('error.log','a')
    log.write("\n")
    log.write(f"\nHa ocurrido el error:{error})")
    log.write(f"\nDATE:{datetime.datetime.now()}$\n")
    log.close()


def errores():
    return render_template('500.html')
