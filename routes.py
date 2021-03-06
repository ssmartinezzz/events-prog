# -*- coding: utf-8 -*-
import datetime
from db_functions import *
from flask import flash  # importar para mostrar mensajes flash
from forms_classes import *  # importar clase de formulario
from werkzeug.utils import secure_filename
import os.path
from app import db,login_manager,app
from models import *
import os
from email_functions import *
from flask_login import login_required, login_user, logout_user, current_user, LoginManager
from errors import *


@login_manager.unauthorized_handler #Método que cuando intente acceder a ruta sin estar logeado muestre lo siguiente. unauthorized_handler nos permite presonalizar este tipo de error sin tener que abortar con el error 401
def unauthorized_callback():
    flash('Para continuar debe iniciar sesión.','danger')
    return redirect(url_for('index'))




@app.route('/')
#Ruta sin filtro aplicado
@app.route('/<int:pag>', methods=["POST", "GET"])
#Ruta cuando se aplica el filtro
@app.route('/<int:pag>/<fechainicio>/<fechafinal>/<opciones>',methods=['GET'])
def index(pag=1,fechainicio='',fechafinal='',opciones=''):
    formularionav=Navegationform()
    pag_tam = 6
    if(request.args):
        fechainicio = request.args.get('fechainicio',None)
        fechafinal = request.args.get('fechafinal',None)
        opciones = request.args.get('opciones',None)
    eventos=Evento.query.filter(Evento.aprobado==True)
    if(fechainicio!=None and fechainicio!=''):
        formularionav.fechainicio.data = datetime.datetime.strptime(fechainicio, "%Y-%m-%d").date()
        eventos=eventos.filter(Evento.fecha<=fechainicio)
    if(fechafinal!=None and fechafinal!=''):
        formularionav.fechafinal.data= datetime.datetime.strptime(fechafinal, "%Y-%m-%d").date()
        eventos=eventos.filter(Evento.fecha>=fechafinal)
    if(opciones!=None and opciones!='' and opciones!='null'and opciones!='None'):
        formularionav.opciones.data = opciones
        eventos = eventos.filter(Evento.tipo==opciones)
    eventos=eventos.order_by(Evento.fecha.desc())
    eventos=eventos.paginate(pag,pag_tam,error_out=False)
    return render_template('index.html', formularionav=formularionav,eventos=eventos)


# Ruta para el inicio de sesion
@app.route('/iniciar', methods=["POST", "GET"])
def logIn():
    formulariolog = Logform()  # Instanciar formulario de registro
    if formulariolog.validate_on_submit():  # Si el formulario ha sido enviado y es validado correctamente
        usuario=Usuario.query.filter_by(email=formulariolog.email.data).first() #Obtengo el mail del usuario de la bd y lo guardo en un objeto para poder pasarlo por parametro al login_user del LoginManager
        if usuario is not None and usuario.verificar_pass(formulariolog.password.data): # Verifico la password encriptada en la bd y la comparo con la del form
            login_user(usuario,False) # Realizo el login del usuario, el False denota que el campo de remember me no este activado
            flash('Usuario Logeado exitosamente','success')  # Mostrar mensaje
            getUser(formulariolog)  # Imprimir datos por consola
            return redirect(url_for('index'))
        else:
            flash('Usuario contraseñas incorrectos!','danger')
            return redirect(url_for('index'))
    return render_template('login.html', formulariolog=formulariolog)

@app.route('/logout')
#Limitar el acceso a los usuarios registrados
@login_required
def logout():
    logout_user() # Metodo del LoginManager que permite deslogear una cuenta
    flash('Logged off!','danger')
    return redirect(url_for('index'))



# RUTA PARA REGISTRO DE UN NUEVO USUARIO
@app.route('/registro', methods=["POST", "GET"])
def register():
    formulario = Registerform()  # Instanciar formulario de registro
    if formulario.submit.data is True and formulario.validate_on_submit():# Si el formulario ha sido enviado y es validado correctamente
        if registredUser(formulario.email.data):
            mostrar_datos(formulario)  # Imprimir datos por consola
            usuario=createUser(formulario.nombre.data,formulario.apellido.data,formulario.email.data,formulario.password.data,admin=False)#Paso los campos obligatorios que necesita esta funcion para crear un nuevo usuario, es decir los campos de los modelos
            if usuario==False:
                return errores()
            email=formulario.email.data# Almaceno en las variables propias de la funcion el contenido del formulario
            sendMail(email,'Su cuenta de EventZ ha sido creada!','newaccount', formulario=formulario) #Funcion del mail que requiere la direccion a enviar "VAR mail", con el mensaje a mostrar teniendo en cuenta un formato txt y html que poseemos
            flash('Usuario registrado exitosamente','success')  # Mostrar mensaje
            print(formulario.email.data)#terminal
            return redirect(url_for('index'))

        else:
            flash('Existe una cuenta registrada con el email ingresado', 'danger')

    return render_template('register.html', formulario=formulario)


@app.route('/menu')
@login_required  #Metodo de Flask Login del LoginManager que permite darle acceso restringido a ciertas vistas.
def menu():
    return render_template('main-menu.html')

#url que lista los eventos de cualquier usuario (antes de sesiones lista solo lo del usuarioId 301)
@app.route('/mis-eventos')
@login_required#Metodo de Flask Login del LoginManager que permite darle acceso restringido a ciertas vistas.
def myEvents():
    listaeventos=db.session.query(Evento).filter(Evento.usuarioId==current_user.usuarioId).all()
    return render_template('my-events.html',listaeventos=listaeventos)

# RUTA Y DUNCION PARA LA CREACION DE UN EVENTO
@app.route('/creacion', methods=["POST", "GET"])
@login_required#Metodo de Flask Login del LoginManager que permite darle acceso restringido a ciertas vistas.
def createNewEvent():
    formulario = Eventform()
    if formulario.validate_on_submit():
        f = formulario.imagen.data  # Obtener imagen
        filename = secure_filename(f.filename)
        f.save(os.path.join('static/Fondo/', filename))
        flash("Evento creado exitosamente!",'success')
        showEve(formulario)
        listaeventos=db.session.query(Evento).filter(Evento.usuarioId==current_user.usuarioId).all()

        evento=createEvent(formulario.titulo.data,formulario.fechaevento.data,formulario.hora.data,formulario.desc.data,filename,formulario.opciones.data,current_user.usuarioId)
        if evento==False:
            return errores()
        return redirect(url_for('myEvents'))
    return render_template('create-event.html', formulario=formulario, destino="createNewEvent")

#Ruta que nos permite actualizar los datos de un evento traido de db, donde al ser igualados y llenados en el formulario podemos efectuar los cambios
@app.route('/update/evento/<id>', methods=["POST", "GET"])
@login_required#Metodo de Flask Login del LoginManager que permite darle acceso restringido a ciertas vistas.
def updateEvent(id):
    evento = db.session.query(Evento).get(id)
    formulario=Eventform(obj=evento)
    Eventform.opcional(formulario.imagen)
    if formulario.validate_on_submit():
        flash('Las modificaciones del evento han sido guardadas con éxito!!!','success')
        showEve(formulario)
        evento.nombre=formulario.titulo.data    # A los valores de la query del objeto que queremos le asignamos los nuevos conseguidos por el propio formulario
        evento.fecha=formulario.fechaevento.data
        evento.hora=formulario.hora.data
        evento.tipo=formulario.opciones.data
        evento.descripcion=formulario.desc.data
        evento.imagen=formulario.imagen.data
        evento.aprobado=False

        actualizado=updateDBEvent(evento)
        if actualizado==False:
            return errores()
        return redirect(url_for('index'))
    else:
            formulario.titulo.data=evento.nombre
            formulario.fechaevento.data=evento.fecha
            formulario.hora.data=evento.hora
            formulario.opciones.data=evento.tipo
            formulario.desc.data=evento.descripcion
            formulario.imagen.data=evento.imagen
    return render_template('create-event.html', formulario=formulario, destino="updateEvent",evento=evento)

@app.route('/evento/borrar/<id>')
@login_required#Metodo de Flask Login del LoginManager que permite darle acceso restringido a ciertas vistas.
def deleteEvent(id):
    evento= db.session.query(Evento).get(id)
    db.session.delete(evento)
    try:
        db.session.commit()
        flash('Evento eliminado exitosamente!','warning')
        if current_user.admin==True:
            return redirect(url_for('eventsControl'))
        else:
            return redirect(url_for('myEvents'))
    except SQLAlchemyError as e:
        db.session.rollback()
        mensaje=str(e._message())
        getLogEvents(mensaje)
        return render_template('500.html')




@app.route('/comentario/borrar/<id>')
@login_required#Metodo de Flask Login del LoginManager que permite darle acceso restringido a ciertas vistas.
def deleteMyComment(id):
    comentario = db.session.query(Comentario).get(id) #Realizo la consulta para traer un solo comentario especificando el id
    eventID= comentario.eventoId #Necesito almacenar el id del evento al cual pertenecia el comentario para poder volver a la vista del mismo
    db.session.delete(comentario) #Borro el comentario de la Db, procedo al manejo de errores.
    try:
        db.session.commit() #Si no hay problemas, realiza los cambios efectuados
        flash('El comentario ha sido borrado con exito!','warning')
        return redirect(url_for('detailedEvent',id=eventID))
    except SQLAlchemyError as e:
        db.session.rollback() #Si ocurre un error, retrocede los cambios efectuados en la base al eliminar el comentario y almacenamos el error en nuestro log gracias al handler de errores
        mensaje=str(e._message())
        getLogEvents(mensaje)
        return render_template('500.html')

# RUTA Y FUNCION PARA LISTAR LOS EVENTOS CON LOS COMENTARIOS Y CREARLOS
@app.route('/evento/<id>', methods=["POST", "GET"])
def detailedEvent(id):
    evento = db.session.query(Evento).get(id)
    commentList =db.session.query(Comentario).filter(Comentario.eventoId==id).order_by(Comentario.fechahora).all()
    form = Commentsform()
    if form.validate_on_submit(): #Si los datos del formulario son correctos procede a ejecutar lo siguiente
        flash('Comentario Enviado','success')
        pCommentary(form)
        comentario=createComment(form.comentario.data,current_user.usuarioId,id)
        if comentario==False:
            return errores()
        return redirect(url_for('detailedEvent',id=id))
    return render_template('event.html', id=id, evento=evento,form=form,commentList=commentList) #Lleva a la vista del evento dicho en particular.

""""RUTAS QUE SOLO PUEDE ACCEDER EL ADMINISTRADOR DEL SITIO, CONTIENE LAS FUNCIONES"""

#Ruta que muestra el menu de opciones disponibles al administrador
@app.route('/admin/menu')
@login_required#Metodo de Flask Login del LoginManager que permite darle acceso restringido a ciertas vistas.
def menuadmin():
    if not current_user.admin: #Corrobora gracias el id del Usuario de la bd almacenado en current_user gracias a LoginManager, si el mismo en la Db si es administrador o no
        flash('Forbidden route, unable to access!','danger')
        return redirect(url_for('index')) #Al no ser admin nos muestra una notificacion de error y procede a llevarnos a la pagina de inicio
    else:
        return render_template('admin-menu.html')

#Ruta que le permite visibilizar los eventos disponibles a controlar.
@app.route('/admin/regular/')
@login_required
def eventsControl():
    if not current_user.admin:
        flash('Forbidden route, unable to access!','danger')
        return redirect(url_for('index'))
    listaeventos=db.session.query(Evento).all()
    return render_template('admin-events.html',listaeventos=listaeventos)

#Ruta para que el admin regule un evento "x".
@app.route('/admin/evento/<id>',methods=["POST","GET"])
@login_required
def eventbyAdmin(id):
    if current_user.admin:
        form=Commentsform()
        evento = db.session.query(Evento).get(id)
        comentadmin =db.session.query(Comentario).filter(Comentario.eventoId==id).order_by(Comentario.fechahora).all()
        return render_template('event-adminview.html', comentadmin=comentadmin,id=id,evento=evento,form=form)

    elif  not current_user.admin:
        flash('Forbidden route, unable to access!','danger')
        return redirect(url_for('index'))


#El administrador es capaz de aprobar el evento mediante esta funcion
@app.route('/admin/evento/validate/<id>')
@login_required
def checkEvent(id):
    if not current_user.admin:
        flash('Forbidden route, unable to access!','danger')
        return redirect(url_for('index'))
    evento=db.session.query(Evento).get(id)
    if evento.aprobado==True:
        print("Evento ya aprobado con anterioridad")
        return redirect(url_for('index'))
    elif evento.aprobado==False: #Si el evento se encontraba en estado pendiente de aprobacion aprobado=False procede a:
        evento.aprobado=True #Establecer como aprobado el evento
        email=evento.usuario.email # Se obtiene al Usuario relacionado con el evento, es decir el propietario y se obtiene su email.
        updateDBEvent(evento) # Funcion que actualizara el objeto del evento, y alli maneja excepciones
        sendMail(email,'Su evento ha sido aprobado por el administrador!','event-confirm')
        print(email)
        flash('Evento aprobado!','success')
        return redirect(url_for('eventsControl',evento=evento))


#Ruta que le permite al administrador del sistema eliminar el comentario deseado de un evento "x"
@app.route('/comentario/eliminar/<id>')
@login_required
def deleteComment(id):
    if not current_user.admin:
        flash('Forbidden route, unable to access!','danger')
        return redirect(url_for('index'))
    comentario = db.session.query(Comentario).get(id)
    eventID= comentario.eventoId # Antes de borrar el comentario, guardamos el evento relacionado al mismo para poder redireccionarnos despues de ejecutar al mismo evento
    db.session.delete(comentario)# Elimina el Comentario del evento, intentará efectuar los cambios en la db.
    try:
        db.session.commit()
        flash('El comentario ha sido borrado con exito!','success')
        return redirect(url_for('eventbyAdmin',id=eventID))

    except SQLAlchemyError as e:
        db.session.rollback()
        mensaje=str(e._message())
        getLogEvents(mensaje)
        return render_template('500.html')
