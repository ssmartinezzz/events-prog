from flask import redirect, url_for, request
from datetime import datetime
from app import app,db,csrf
from models import *
from flask import jsonify
from emailfunctions import *


#Listar todos los eventos
#curl -i -H "Content-Type:application/json" -H "Accept: application/json" http://localhost:5000/api/listaeventos
@app.route('/api/listaeventos', methods=['GET'])
def listAllEventsApi():
    eventos = db.session.query(Evento).filter(Evento.aprobado==False)

    #Recorrer la lista de personas convirtiendo cada una a JSO
    return jsonify({ 'Eventos': [evento.a_json() for evento in eventos] })

#Listar evento por id
#curl -i -H "Content-Type:application/json" -H "Accept: application/json" http://localhost:5000/admin/listareventos/id
@app.route('/admin/listareventos/<id>',methods=['GET'])
def listEventsbyApi(id):
    evento =  db.session.query(Evento).get(id)
    return jsonify({'Evento':[evento.a_json()]})

#Aprobar evento por id
#curl -X POST -i -H  "Content-Type:application/json" -H "Accept:application/json" http://127.0.0.1:5000/admin/evento/aprobar/id
@app.route('/admin/evento/aprobar/<id>',methods=['POST'])
@csrf.exempt
def aprobarEventosApi(id):
    evento=db.session.query(Evento).get(id)
    evento.aprobado=True
    email=evento.usuario.email
    sendMail(email,'Su evento ha sido borrado!','mail/event-confirm')
    db.session.commit()
    print("El evento ha sido aprobado")
    print(email)
    return jsonify({'Evento':[evento.a_json()]})
#curl -i -X PUT -H "Content-Type:application/json" -H "Accept:application/json" http://localhost:5000/api/evento/15 -d '{"nombre":"eventaso"}'
@app.route('/api/evento/<id>', methods=['PUT'])
@csrf.exempt
def apiActualizarEvento(id):
    evento =  db.session.query(Evento).get(id)
    evento.nombre = request.json.get('nombre', evento.nombre)
    evento.fecha = request.json.get('fecha', evento.fecha)
    evento.descripcion = request.json.get('descripcion', evento.descripcion)
    evento.tipo=request.json.get('tipo', evento.tipo)
    evento.aprobado=False
    db.session.add(evento)
    db.session.commit()
    #Convertir la persona actualizada en JSON
    #Pasar código de status
    return jsonify(evento.a_json()) , 201

#Eliminar evento
#curl -i -X DELETE -H "Accept: application/json" http://localhost:5000/eventoadmin/eliminareve/2
@app.route('/eventoadmin/eliminareve/<id>', methods=['DELETE'])
@csrf.exempt
def deleteApiEvent(id):
    eventoaeliminar= db.session.query(Evento).get(id)
    db.session.delete(eventoaeliminar)
    email=evento.usuario.email
    sendMail(email,'Su evento ha sido borrado!','mail/deleted')
    db.session.commit()
    print("Evento eliminado con éxito")
    return '',204



"""PARTE DE LA API PARA LOS COMENTARIOS """
#curl -i -H "Content-Type:application/json" -H "Accept: application/json" http://localhost:5000/api/convertToJSON/17
@app.route('/api/convertToJSON/<id>', methods=['GET'])
def convertToJSON(id):
    comentario = db.session.query(Comentario).get(id)
    return jsonify(comentario.a_json())

#curl -i -H "Content-Type:application/json" -H "Accept: application/json" http://localhost:5000/api/evento/coments/24
@app.route('/api/evento/coments/<id>',methods=['GET'])
def apigetComments(id):
    comentarios= db.session.query(Comentario).filter(Comentario.eventoId==Evento.eventoId,Comentario.eventoId==id,Evento.eventoId==id)
    return jsonify({ 'Comentarios': [comentario.a_json() for comentario in comentarios] })

#curl -i -X DELETE -H "Accept: application/json" http://localhost:5000/api/deletecomment/60
@app.route('/api/deletecomment/<id>',methods=['DELETE'])
@csrf.exempt
def deleteCommentapi(id):
    comentario =db.session.query(Comentario).get(id)
    db.session.delete(comentario)
    db.session.commit()
    print("Comentario borrado correctamente")
    return '',204
