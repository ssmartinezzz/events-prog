from flask import redirect, url_for, request
from datetime import datetime
from app import app,db
from models import *
from flask import jsonify


#Listar todos los eventos
#curl -i -H "Content-Type:application/json" -H "Accept: application/json" http://localhost:5000/admin/regular
@app.route('/admin/regular', methods=['GET'])
def listAllEventsApi():
    eventos = db.session.query(Evento).all()
    #Recorrer la lista de personas convirtiendo cada una a JSO
    return jsonify({ 'Eventos': [evento.a_json() for evento in eventos] })

#Listar evento por id
#curl -i -H "Content-Type:application/json" -H "Accept: application/json" http://localhost:5000/admin/evento/17
@app.route('/admin/evento/<id>',methods=['GET'])
def listEventsbyApi(id):
    evento =  db.session.query(Evento).get(id)
    comentadmin = db.session.query(Comentario).filter(Comentario.eventoId ==id).order_by(Comentario.fechahora).all()
    return jsonify({'Evento':[evento.a_json()]})
    return jsonify({'Comentarios':[comentadmin.a_jason()]})



#Aprobar evento por id
#curl -X POST -i -H  "Content-Type:application/json" -H "Accept:application/json" http://127.0.0.1:8000/admin/evento/validate/17
@app.route('/admin/evento/validate/<id>',methods=['POST'])
def aprobarEventosApi(id):
    evento=db.session.query(Evento).get(id)
    evento.aprobado=True
    email=evento.usuario.email
    #actualizareve(evento)
    #sendMail(email,'Su evento ha sido aprobado por el administrador!','mail/event-confirm')
    db.session.commit()
    print("El evento ha sido aprobado")


#Eliminar evento
#curl -i -X DELETE -H "Accept: application/json" http://localhost:5000/api/persona/2
@app.route('/eventoadmin/eliminar/<id>', methods=['DELETE'])
def deleteApiEvent(id):
    evento= db.session.query(Evento).get(id)
    db.session.delete(evento)
    #email=evento.usuario.email
    #sendMail(email,'Su evento ha sido borrado!','mail/mensaje')
    db.session.commit()
    print("Evento eliminado con éxito")
