from app import db
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
    #Relación entre evento y comentario
    comentarios=db.relationship("Comentario", back_populates="evento", cascade="all,delete-orphan") #se pide la lista de comentarios


    def __repr__(self):
        return '<Evento: %r %r %r %r %r>' % (self.eventoId,self.nombre, self.fecha,self.hora, self.descripcion, self.imagen, self.tipo)

class Usuario(db.Model):
    usuarioId = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    apellido = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    admin = db.Column(db.Boolean, nullable=False)

    #Relación entre evento y usuario
    eventos=db.relationship("Evento", back_populates="usuario", cascade="all, delete-orphan")
    #Relación entre usuario y comentario
    comentarios=db.relationship("Comentario", back_populates="usuario", cascade="all, delete-orphan")
    def __repr__(self):
        return '<Usuario: %r %r %r %r %r %r %r>' % (self.usuarioId,self.nombre,self.apellido, self.email, self.password,self.admin, self.fecha)

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

#db.drop_all() #Elimina las tablas de la db
db.create_all() #Crea las tablas de la db a patir de los modelos
