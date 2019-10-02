from app import db
from models import *
def listar_eventos():
    import csv
    with open('actividades-culturales.csv') as f:
        a = [{k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)]
    return a

def comentarios():
        import csv
        with open('coments.csv') as f:
            a = [{k: v for k, v in row.items()}
                for row in csv.DictReader(f, skipinitialspace=True)]
        return a
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
    print(formulariolog.usuario.data)
    print(formulariolog.password.data)
def navbar(formularionav):
    print(formularionav.fechainicio.data)
    print(formularionav.fechafinal.data)
    print(formularionav.titulo.data)
    print(formularionav.opciones.data)        
def listEvent():
    eventlist =db.session.query(Evento).all()
    return eventlist
#@app.route('/evento/crear/<eventoId>/<nombre>/<fechahora>/<descripcion>/<imagen>')
def createEvent(nombre,fecha,hora,descripcion,imagen,tipo,usuarioId):
    #EJ: /persona/crear/Marcos/Gonzales/1999-05-01
    #Crear una persona
    usuario=db.session.query(Usuario).get(usuarioId)
    evento = Evento(usuario=usuario,nombre=nombre,fecha=fecha,hora=hora,descripcion=descripcion,imagen=imagen,tipo=tipo)
    #Agregar a db
    db.session.add(evento)
    #Hacer commit de los cambios
    db.session.commit()
    #Envía la persona a la vista
    #return render_template('evento.html',evento=evento)
#@app.route('/usuario/crear/<nombre>/<apellido>/<email>/<password>/<admin>')
def createUser(nombre,apellido,email,password,admin):
    #EJ: /persona/crear/Marcos/Gonzales/1999-05-01
    #Crear una persona
    usuario = Usuario(nombre=nombre, apellido=apellido,email=email,password=password,admin=admin)
    admin=False
    #Agregar a db
    db.session.add(usuario)
    #Hacer commit de los cambios
    db.session.commit()
    #Envía la persona a la vista
    #return render_template('usuario.html',usuario=usuario)
