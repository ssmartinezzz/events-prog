from app import db,login_manager
from werkzeug.security import generate_password_hash, check_password_hash #Permite generar y verificar pass con hash encriptadas
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer # Genera los token de confirmación para ccomparar token de logeo
from flask_login import UserMixin, LoginManager
from flask import url_for

class Evento(db.Model): # Obligatoriamente por el ORM de Flask-SQLAlchemy los objetos deben heredar Model para poder operar con las tablas
    eventoId = db.Column(db.Integer, primary_key=True) #Column indica que la variable será justamente una columna de la tabla relacional, primary_key: Clave primaria de la tabla para poder relacionarla
    nombre = db.Column(db.String(90), nullable=False)# nullable false: No puede ser nulo la columna
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    descripcion = db.Column(db.String(500), nullable= True)
    imagen = db.Column(db.String(40), nullable=False)
    tipo = db.Column(db.String(15), nullable=False)
    #Relación entre evento y usuario
    usuarioId=db.Column(db.Integer, db.ForeignKey('usuario.usuarioId'), nullable=False)  #ForeignKey clave para poder relacionar 1 objeto con muchos objetos en la relacion 1 -muchos. Se pone del lado de los muchos siempre
    usuario=db.relationship("Usuario", back_populates="eventos") #Primer parametro de relationship indicamos el objeto clase que representamos, en este caso con la relacion Representamos un objeto del tipo Usuario en el de evento
    aprobado=db.Column(db.Boolean,nullable=False, default=False) #El back_populates anterior nos indica cual es el nombre de la variable del otro objeto por el cual nos estamos relacionando
    #Relación entre evento y comentario
    comentarios=db.relationship("Comentario", back_populates="evento", cascade="all,delete-orphan") #se pide la lista de comentarios, el cascade nos dice como se comportará la relacion al modificar alguno de los onjetos de la relaciona
    #... en el caso de que se borre un Evento, eliminara todos los comentarios de la relacion 1 muchos. parametro delete-orphan
    def __repr__(self): #Es la funcion de representacion que nos muestra como se va imprimir el Model
        return '<Evento: %r %r %r %r %r %r %r %r >' % (self.eventoId,self.nombre, self.fecha,self.hora, self.descripcion, self.imagen, self.tipo,self.aprobado)

    #Metodo parecido a ToString de java que nos ayuda, en este caso a convertir los atributos de nuestro objeto a formato Json
    def a_json(self):
        evento_json = {
            'eventoId': url_for('listEventsbyApi', id=self.eventoId, _external=True), #Ruta para acceder a la persona
            'nombre': self.nombre,
            'fecha': self.fecha,
            'hora': str(self.hora),
            'descripcion':self.descripcion,
            'tipo':self.tipo,
            'aprobado':self.aprobado,
            'imagen':self.imagen

        }
        return evento_json
    @staticmethod
    #Metodo que estático no hace falta instanciarlo, perteneciente a la clase Evento, que podemos pasarle un Json y nos traera los atributos y los convertira adecuadamente a un Objeto evento
    def desde_json(evento_json):
        nombre = evento_json.get('nombre')
        fecha = evento_json.get('fecha')
        descripcion = evento_json.get('descripcion')
        tipo=evento_json.get('tipo')
        aprobado=evento_json.get('aprobado')
        return Evento(nombre=nombre, fecha=fecha, descripcion=descripcion,tipo=tipo,aprobado=aprobado)


class Usuario(UserMixin,db.Model): #Hereda model para poder trabajar con el ORM y las tablas. Tambien hereda el userMixin que hace que usuario herede todo lo de  is_aunthenticated
    usuarioId = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    apellido = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    admin = db.Column(db.Boolean, nullable=False)

    #Relación entre evento y usuario
    eventos=db.relationship("Evento", back_populates="usuario", cascade="all, delete-orphan") # relacion de 1usuario muchos eventos, se borra el user, elimina todos los eventos. El nombre de la relacion en el Objeto Evento se llama usuario ->Indicado por back_populates
    #Relación entre usuario y comentario
    comentarios=db.relationship("Comentario", back_populates="usuario", cascade="all, delete-orphan") #Borra el usuario, elimina todos sus comentarios. El back_populates nos muestra que la relacion en el Obj Comentario con Usuario se llama "usuario"

    @property #No permite acceder a la password del Usuario
    def notepassword(self):
        raise AttributeError('La password no puede leerse')
    #Al setear la pass generar un hash
    @notepassword.setter
    def notepassword(self, notepassword):
        self.password = generate_password_hash(notepassword)
    def get_id(self):
           return (self.usuarioId)

    #Al verififcar pass comparar hash del valor ingresado con el de la db
    def verificar_pass(self, notepassword):
        return check_password_hash(self.password, notepassword)

#Asi es como se imprime el objeto Usuario mediante su constructor
    def __repr__(self):
        return '<Usuario: %r %r %r %r %r %r >' % (self.usuarioId,self.nombre,self.apellido, self.email, self.password,self.admin)

@login_manager.user_loader #Funcion por defecto que tengo que especificar de como busco el Objeto del usuario y lo cargo en la session
def load_user(user_id):
    return Usuario.query.get(int(user_id)) #Buscar el usuario por id para logear



class Comentario(db.Model):
    comentarioId = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.String(500), nullable = False)
    fechahora = db.Column(db.DateTime, nullable=False)
    #Relación entre usuario y comentario
    usuarioId=db.Column(db.Integer,db.ForeignKey('usuario.usuarioId'),nullable=False) #Establecimiento de la clave foranea para poder relacionar los muchos con el Objeto individual
    usuario=db.relationship("Usuario", back_populates="comentarios") #La relacion establecida con el Obj Usuario nos muestra que alli se llama comentarios. relationship va a ser Usuario "Nombre de clase que se esta representando"
    #Relación entre evento y comentario
    eventoId=db.Column(db.Integer, db.ForeignKey('evento.eventoId'), nullable=False) #Clave con la que relacionamos 2 tablas en un modelo relacional,usando clave primaria y esta clave, siempre va del lado de los muchos
    evento= db.relationship("Evento", back_populates="comentarios")
    def __repr__(self):
        return '<Comentario: %r %r %r >' % (self.comentarioId,self.texto, self.fechahora)

    def a_json(self):
        comentario_json = {
            'comentarioId':url_for('convertToJSON', id=self.comentarioId, _external=True),
            'contenido': self.contenido,
            'fechahora': self.fechahora
        }
        return comentario_json

    @staticmethod
    #Metodo que estático no hace falta instanciarlo, perteneciente a la clase Comentario, que podemos pasarle un Json y nos traera los atributos y los convertira adecuadamente a un Objeto comentario
    def desde_json(comentario_json):
        contenido = evento_json.get('contenido')
        fechahora = evento_json.get('fechahora')
        return Comentario(contenido=contenido,fechahora=fechahora) #Crea el objeto


    def get_id(self):
         return (self.comentarioId)
