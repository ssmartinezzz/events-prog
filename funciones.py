from app import db
from models import *
from sqlalchemy.exc import SQLAlchemyError
from errors import *

def mostrar_datos(formulario):
    print(formulario.nombre.data)
    print(formulario.apellido.data)
    print(formulario.password.data)
    # print(formulario.bio.data)
    print(formulario.email.data)
    # print(formulario.opciones.data)


def showEve(formulario):
    print(formulario.titulo.data)
    print(formulario.fechaevento.data)
    print(formulario.hora.data)
    print(formulario.opciones.data)
    print(formulario.desc.data)


def pCommentary(formulario):
    print(formulario.comentario.data)


def getUser(formulariolog):
    print(formulariolog.email.data)
    print(formulariolog.password.data)
def navbar(formularionav):
    print(formularionav.fechainicio.data)
    print(formularionav.fechafinal.data)
    print(formularionav.opciones.data)
def listEvent():
    eventlist =db.session.query(Evento).all()
    return eventlist

def createEvent(nombre,fecha,hora,descripcion,imagen,tipo,usuarioId):
    usuario=db.session.query(Usuario).get(usuarioId)
    evento = Evento(usuario=usuario,nombre=nombre,fecha=fecha,hora=hora,descripcion=descripcion,imagen=imagen,tipo=tipo)
    #Agregar a db
    db.session.add(evento)
    #Hacer commit de los cambios
    try:
        db.session.commit() #Envía la persona a la vista
    except SQLAlchemyError as e:
        db.session.rollback()
        mensaje= str(e._message())
        getLogEvents(mensaje)

def createUser(nombre,apellido,email,password,admin):

    #Crear una persona
    usuario = Usuario(nombre=nombre, apellido=apellido,email=email,notepassword=password,admin=admin)
    #Agregar a db
    db.session.add(usuario)
    #Hacer commit de los cambios
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        mensaje=str(e._message())
        getLogEvents(mensaje)

def updateDBEvent(evento):
    print("Actualizando evento!")
    db.session.add(evento)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        mensaje=str(e._message())
        getLogEvents(mensaje)

def createComment(contenido,usuarioId,eventoId):
    #Funcion que permite por el panel de mis eventos eliminar el evento que se toque con el respectivo id
    usuario=db.session.query(Usuario).get(usuarioId)
    evento=db.session.query(Evento).get(eventoId)
    fechahora=db.func.current_timestamp()
    comment = Comentario(contenido=contenido,fechahora=fechahora,evento=evento,usuario=usuario)
    db.session.add(comment)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        mensaje=str(e._message())
        getLogEvents(mensaje)


def mysql_query(query):
    return query.statement.compile(compile_kwargs={"literal_binds": True})
