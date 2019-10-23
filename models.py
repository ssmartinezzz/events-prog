from app import db,login_manager
from werkzeug.security import generate_password_hash, check_password_hash #Permite generar y verificar pass con hash encriptadas
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer # Genera los token de confirmación para ccomparar token de logeo
from flask_login import UserMixin, LoginManager
class Evento(db.Model):
    eventoId = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(90), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    descripcion = db.Column(db.String(500), nullable= True)
    imagen = db.Column(db.String(40), nullable=False)
    tipo = db.Column(db.String(15), nullable=False)
    #Relación entre evento y usuario
    usuarioId=db.Column(db.Integer, db.ForeignKey('usuario.usuarioId'), nullable=False)
    usuario=db.relationship("Usuario", back_populates="eventos")
    aprobado=db.Column(db.Boolean,nullable=False, default=False)
    #Relación entre evento y comentario
    comentarios=db.relationship("Comentario", back_populates="evento", cascade="all,delete-orphan") #se pide la lista de comentarios


    def __repr__(self):
        return '<Evento: %r %r %r %r %r %r %r %r >' % (self.eventoId,self.nombre, self.fecha,self.hora, self.descripcion, self.imagen, self.tipo,self.aprobado)

class Usuario(UserMixin,db.Model):
    usuarioId = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    apellido = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    admin = db.Column(db.Boolean, nullable=False)

    #Relación entre evento y usuario
    eventos=db.relationship("Evento", back_populates="usuario", cascade="all, delete-orphan")
    #Relación entre usuario y comentario
    comentarios=db.relationship("Comentario", back_populates="usuario", cascade="all, delete-orphan")

    @property
    def notepassword(self):
        raise AttributeError('La password no puede leerse')
    #Al setear la pass generar un hash
    @notepassword.setter
    def notepassword(self, notepassword):
        self.password = generate_password_hash(notepassword)
    def get_id(self):
           return (self.usuarioId)
    def is_admin(self):
        aux= False
        if self.admin == 1:
            aux = True
        return aux
    #Al verififcar pass comparar hash del valor ingresado con el de la db
    def verificar_pass(self, notepassword):
        return check_password_hash(self.password, notepassword)
    def __repr__(self):
        return '<Usuario: %r %r %r %r %r %r >' % (self.usuarioId,self.nombre,self.apellido, self.email, self.password,self.admin)

@login_manager.user_loader #Funcion por defecto que tengo que especificar de como buscarlo
def load_user(user_id):
    return Usuario.query.get(int(user_id)) #Buscar el usuario por id para logear



class Comentario(db.Model):
    comentarioId = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.String(500), nullable = False)
    fechahora = db.Column(db.DateTime, nullable=False)
    #Relación entre usuario y comentario
    usuarioId=db.Column(db.Integer,db.ForeignKey('usuario.usuarioId'),nullable=False)
    usuario=db.relationship("Usuario", back_populates="comentarios")
    #Relación entre evento y comentario
    eventoId=db.Column(db.Integer, db.ForeignKey('evento.eventoId'), nullable=False)
    evento= db.relationship("Evento", back_populates="comentarios")
    def __repr__(self):
        return '<Comentario: %r %r %r >' % (self.comentarioId,self.texto, self.fechahora)
