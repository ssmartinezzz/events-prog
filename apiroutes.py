from flask import redirect, url_for, request
from datetime import datetime
from app import app,db,csrf
from models import *
from flask import jsonify
from email_functions import *
from errors import *


#Listar todos los eventos
#curl -i -H "Content-Type:application/json" -H "Accept: application/json" http://localhost:5000/api/listaeventos
@app.route('/api/listaeventos', methods=['GET'])
def listAllEventsApi():
    eventos = db.session.query(Evento).filter(Evento.aprobado==False)

    #Recorrer la lista de personas convirtiendo cada una a JSON
    return jsonify({ 'Eventos': [evento.a_json() for evento in eventos] }) #Convierte a Json y lo devuelve por terminal todos los eventos que estan contenidos en la listadeeventos, mediante un foreach(similar a java)

#Listar evento por id
#curl -i -H "Content-Type:application/json" -H "Accept: application/json" http://localhost:5000/admin/listareventos/id
@app.route('/admin/listareventos/<id>',methods=['GET'])
def listEventsbyApi(id):
    evento =  db.session.query(Evento).get(id)
    return jsonify({'Evento':[evento.a_json()]}) #Nos convierte a Json el objeto evento que estamos trayendo de la consulta de base de datos, y lo convertimos usando el metodo creado en el objeto de la clase

#Aprobar evento por id
#curl -X POST -i -H  "Content-Type:application/json" -H "Accept:application/json" http://127.0.0.1:5000/admin/evento/aprobar/id
@app.route('/admin/evento/aprobar/<id>',methods=['POST'])
@csrf.exempt #Nos permite exceptuar la validacion del csrf, para que nuestra Api si pueda realizar peticiones al servidor. Si no lo hicieramos obtendríamos Bad request por la seguridad que el token nos brinda
def aprobarEventosApi(id):
    evento=db.session.query(Evento).get(id)
    if (evento.aprobado==True):
        print("El evento ya se encuentra aprobado!")
    elif (evento.aprobado==False):
        evento.aprobado=True
        email=evento.usuario.email
        sendMail(email,'Su evento ha sido aprobado!','event-confirm')
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            mensaje=str(e._message())
            getLogEvents(mensaje)
        print("El evento ha sido aprobado")
        print(email)
        return jsonify({'Evento':[evento.a_json()]})

#curl -i -X PUT -H "Content-Type:application/json" -H "Accept:application/json" http://localhost:5000/api/evento/15 -d '{"nombre":"eventaso"}'
@app.route('/api/evento/<id>', methods=['PUT'])
@csrf.exempt
def apiActualizarEvento(id):
    evento =  db.session.query(Evento).get(id)
    evento.nombre = request.json.get('nombre', evento.nombre) #El objeto va a realizar un pedido de que obtenga del Json segun la clave, un argumento valor json y lo convierte a uno del tipo del objeto
    evento.fecha = request.json.get('fecha', evento.fecha)
    evento.descripcion = request.json.get('descripcion', evento.descripcion)
    evento.tipo=request.json.get('tipo', evento.tipo)
    evento.aprobado=False
    db.session.add(evento)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        mensaje=str(e._message())
        getLogEvents(mensaje)
    return jsonify(evento.a_json()) , 201#Convertir la persona actualizada en JSON
    #Pasar código de status

#Eliminar evento
#curl -i -X DELETE -H "Accept: application/json" http://localhost:5000/eventoadmin/eliminareve/2
@app.route('/eventoadmin/eliminareve/<id>', methods=['DELETE'])
@csrf.exempt
def deleteApiEvent(id):
    eventoaeliminar= db.session.query(Evento).get(id)
    db.session.delete(eventoaeliminar)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        mensaje=str(e._message())
        getLogEvents(mensaje)
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
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        mensaje=str(e._message())
        getLogEvents(mensaje)
    print("Comentario borrado correctamente")
    return '',204
