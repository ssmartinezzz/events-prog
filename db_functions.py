from app import db
from models import *
from sqlalchemy.exc import SQLAlchemyError
from errors import *

#Conjunto de funciones que nos muestran los valores almacenados en los distintos tipos de formularios que disponemos. Como Formulario de comentarios,LogIn,Evento, Usuario
def mostrar_datos(formulario):
    print(formulario.nombre.data)
    print(formulario.apellido.data)
    print(formulario.password.data)
    print(formulario.email.data)

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

#Funciones que almacenan consultas de la base de datos permitiendo funcionalidades

#Funcion que crea un Evento directamente en la base de datos.Requiere de parametros todas las columnas que el Modelo de Evento posee.
def createEvent(nombre,fecha,hora,descripcion,imagen,tipo,usuarioId): #Se le agregar el usuarioId que es fundamental ya que un Evento es netamente una tabla relacional con Usuario
    usuario=db.session.query(Usuario).get(usuarioId)#Se obtiene por consulta el usuario que este actualmente logeado, tambien se podria obtener pos current_user
    evento = Evento(usuario=usuario,nombre=nombre,fecha=fecha,hora=hora,descripcion=descripcion,imagen=imagen,tipo=tipo) #Se instancia un Objeto Evento con los atributos y los valores recibidos.
    db.session.add(evento)#Se añade el nuevo evento a la Base de datos, pero requiere que se actualicen los cambios. Dando lugar al siguiente paso: Manejo de errores.

    try:
        db.session.commit()  #Se intentará subir los cambios en la base. Si Ocurre algun tipo de error se exceptuara dicho commit y se hara un rollback
    except SQLAlchemyError as e:
        db.session.rollback() #El rollback revierte los cambios de la base de datos. Si llegase a ocurrir un error se volveria al estado de la db antes de añadir el evento.
        mensaje= str(e._message())# Parseamos el error a string para poder almacenarlo en una variable.
        getLogEvents(mensaje) # La variable es almacenada y la funcion getLogEvents la añade a un log de errores para que el admin la vea.

#Funcion que recibe los datos de un formulario de registro de usuario,exceptuando el campo de administrador.
def createUser(nombre,apellido,email,password,admin):

    usuario = Usuario(nombre=nombre, apellido=apellido,email=email,notepassword=password,admin=admin)#Instanciamos el Objeto Usuario y lo creamos con todos los atributos obtenidos
    #Se tiene en cuenta que notepassword posee la característica que encriptar la contraseña del usuario para ser subida en la bd. El campo de admin por defecto es False.
    db.session.add(usuario)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        mensaje=str(e._message())
        getLogEvents(mensaje)

def updateDBEvent(evento): #Recibe enteramente una instancia de un Objeto evento, con todos los datos del formulario actualizado, reemplazados en el objeto
    print("Actualizando evento!")
    db.session.add(evento)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        mensaje=str(e._message())
        getLogEvents(mensaje)

def createComment(contenido,usuarioId,eventoId): #Requiere un argumento un valor de formulario, los otros se obtienen por consultas
    #Funcion que permite por el panel de mis eventos eliminar el evento que se toque con el respectivo id
    usuario=db.session.query(Usuario).get(usuarioId) #Obtiene nuevamente el Id del usuario ya que es clave para poder relacionar Evento - Usuario -Comentario
    evento=db.session.query(Evento).get(eventoId)#Obtiene Id del Evento necesario para la relacion.
    fechahora=db.func.current_timestamp()# Obtenemos la fecha y hora actual en la Base de datos para poder fijar una fecha de creacion del comentario
    comment = Comentario(contenido=contenido,fechahora=fechahora,evento=evento,usuario=usuario) #Se instancia el Objeto comentario.
    db.session.add(comment)# Se agrega a la base de datos, pero procede a tratar de efectuar o no los cambios con posibilidad de errores.
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        mensaje=str(e._message())
        getLogEvents(mensaje)


def mysql_query(query):
    return query.statement.compile(compile_kwargs={"literal_binds": True})
