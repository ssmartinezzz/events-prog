# -*- coding: utf-8 -*-
import datetime
from funciones import *
from flask import Flask,request,render_template,redirect, url_for
from flask import flash  # importar para mostrar mensajes flash
from forms_classes import *  # importar clase de formulario
from werkzeug.utils import secure_filename
import os.path
from app import db,login_manager,app
from models import *
import os
from email_functions import *
from flask_login import login_required, login_user, logout_user, current_user, LoginManager



@login_manager.unauthorized_handler #Método que cuando intente acceder a ruta sin estar logeado muestre lo siguiente.
def unauthorized_callback():
    flash('Para continuar debe iniciar sesión.')
    return redirect(url_for('index'))

@app.route('/logout')
#Limitar el acceso a los usuarios registrados
@login_required
def logout():
    logout_user()
    #Insntanciar formulario de Login
    formularionav=Navegation()
    formulariolog = Logeo()
    pag=1
    pag_tam=6
    eventos = Evento.query.order_by(Evento.fecha).paginate(pag,pag_tam,error_out=False)
    flash('Logged off!')
    return render_template('index.html', formulariolog=formulariolog,formularionav=formularionav,eventos=eventos)



@app.route('/')
#Ruta sin filtro aplicado
@app.route('/<int:pag>', methods=["POST", "GET"])
#Ruta cuando se aplica el filtro
@app.route('/<int:pag>/<fechainicio>/<fechafinal>/<opciones>',methods=['GET'])
def index(pag=1,fechainicio='',fechafinal='',opciones=''):
    formularionav=Navegation()
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
    formulariolog = Logeo()  # Instanciar formulario de registro
    if formulariolog.validate_on_submit():  # Si el formulario ha sido enviado y es validado correctamente
        usuario=Usuario.query.filter_by(email=formulariolog.email.data).first()
        if usuario is not None and usuario.verificar_pass(formulariolog.password.data):
            login_user(usuario,False)
            flash('Usuario Logeado exitosamente')  # Mostrar mensaje
            getUser(formulariolog)  # Imprimir datos por consola
            return redirect(url_for('index'))
        else:
            flash('Usuario contraseñas incorrectos!')
            return redirect(url_for('index'))
    return render_template('login.html', formulariolog=formulariolog)


# RUTA PARA REGISTRO DE UN NUEVO USUARIO
@app.route('/registro', methods=["POST", "GET"])
def register():
    formulario = Registro()  # Instanciar formulario de registro
    if formulario.validate_on_submit():  # Si el formulario ha sido enviado y es validado correctamente
        mostrar_datos(formulario)  # Imprimir datos por consola
        createUser(formulario.nombre.data,formulario.apellido.data,formulario.email.data,formulario.password.data,admin=False)#Paso los campos obligatorios que necesita esta funcion para crear un nuevo usuario, es decir los campos de los modelos
        email=formulario.email.data# Almaceno en las variables propias de la funcion el contenido del formulario
        sendMail(email,'Su cuenta de EventZ ha sido creada!','mail/newaccount') #Funcion del mail que requiere la direccion a enviar "VAR mail", con el mensaje a mostrar teniendo en cuenta un formato txt y html que poseemos
        flash('Usuario registrado exitosamente')  # Mostrar mensaje
        print(formulario.email.data)#terminal
        return redirect(url_for('index'))
    return render_template('registro.html', formulario=formulario)


@app.route('/menu')
@login_required
def menu():
    return render_template('main-menu.html')

#url que lista los eventos de cualquier usuario (antes de sesiones lista solo lo del usuarioId 301)
@app.route('/mis-eventos')
@login_required
def myEvents():
    listaeventos=db.session.query(Evento).filter(Evento.usuarioId==current_user.usuarioId).all()
    return render_template('my-events.html',listaeventos=listaeventos)

# RUTA Y DUNCION PARA LA CREACION DE UN EVENTO
@app.route('/creacion', methods=["POST", "GET"])
@login_required
def createNewEvent():
    formulario = EventoCrear()
    if formulario.validate_on_submit():
        f = formulario.imagen.data  # Obtener imagen
        filename = secure_filename(f.filename)
        f.save(os.path.join('static/Fondo/', filename))
        flash("Evento creado exitosamente!")
        showEve(formulario)
        listaeventos=db.session.query(Evento).filter(Evento.usuarioId==current_user.usuarioId).all()
        createEvent(formulario.titulo.data,formulario.fechaevento.data,formulario.hora.data,formulario.desc.data,filename,formulario.opciones.data,current_user.usuarioId)
        return redirect(url_for('myEvents'))
    return render_template('create-event.html', formulario=formulario, destino="createNewEvent")

#Ruta que nos permite actualizar los datos de un evento traido de db, donde al ser igualados y llenados en el formulario podemos efectuar los cambios
@app.route('/update/evento/<id>', methods=["POST", "GET"])
@login_required
def updateEvent(id):
    evento = db.session.query(Evento).get(id)
    formulario=EventoCrear(obj=evento)
    EventoCrear.opcional(formulario.imagen)
    if formulario.validate_on_submit():
        flash('Las modificaciones del evento han sido guardadas con éxito!!!')
        showEve(formulario)
        evento.nombre=formulario.titulo.data    # A los valores de la query del objeto que queremos le asignamos los nuevos conseguidos por el propio formulario
        evento.fecha=formulario.fechaevento.data
        evento.hora=formulario.hora.data
        evento.tipo=formulario.opciones.data
        evento.descripcion=formulario.desc.data
        evento.imagen=formulario.imagen.data

        updateDBEvent(evento)
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
@login_required
def deleteEvent(id):
    evento= db.session.query(Evento).get(id)
    db.session.delete(evento)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        mensaje=str(e._message())
        getLogEvents(mensaje)
    flash('Evento eliminado exitosamente!')
    return redirect(url_for('myEvents'))

@app.route('/comentario/borrar/<id>')
@login_required
def deleteMyComment(id):
    comentario = db.session.query(Comentario).get(id)
    eventID= comentario.eventoId
    db.session.delete(comentario)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        mensaje=str(e._message())
        getLogEvents(mensaje)
    flash('El comentario ha sido borrado con exito!')
    return redirect(url_for('detailedEvent',id=eventID))

# RUTA Y FUNCION PARA LISTAR LOS EVENTOS CON LOS COMENTARIOS Y CREARLOS
@app.route('/evento/<id>', methods=["POST", "GET"])
def detailedEvent(id):
    evento = db.session.query(Evento).get(id)
    commentList =db.session.query(Comentario).filter(Comentario.eventoId==id).order_by(Comentario.fechahora).all()
    form = Comentarios()
    if form.validate_on_submit():
        flash('Comentario Enviado')
        pCommentary(form)
        createComment(form.comentario.data,current_user.usuarioId,id)
        return redirect(url_for('detailedEvent',id=id))
    return render_template('evento.html', id=id, evento=evento,form=form,commentList=commentList)

""""RUTAS QUE SOLO PUEDE ACCEDER EL ADMINISTRADOR DEL SITIO, CONTIENE LAS FUNCIONES"""

#Ruta que muestra el menu de opciones disponibles al administrador
@app.route('/admin/menu')
@login_required
def menuadmin():
    if not current_user.admin:
        flash('Forbidden route, unable to access!')
        return redirect(url_for('index'))
    else:
        return render_template('admin-menu.html')

#Ruta que le permite visibilizar los eventos disponibles a controlar.
@app.route('/admin/regular/')
@login_required
def eventsControl():
    if not current_user.admin:
        flash('Forbidden route, unable to access!')
        return redirect(url_for('index'))
    listaeventos=db.session.query(Evento).all()
    return render_template('admineventos.html',listaeventos=listaeventos)

#Ruta para que el admin regule un evento "x".
@app.route('/admin/evento/<id>',methods=["POST","GET"])
@login_required
def eventbyAdmin(id):
    if current_user.admin:
        evento = db.session.query(Evento).get(id)
        comentadmin =db.session.query(Comentario).filter(Comentario.eventoId==id).order_by(Comentario.fechahora).all()
        return render_template('event-adminview.html', comentadmin=comentadmin,id=id,evento=evento)

    elif  not current_user.admin:
        flash('Forbidden route, unable to access!')
        return redirect(url_for('index'))



#Ruta que elimina el evento que el admin desee, (NO ES DESAPROBAR)
@app.route('/admin/evento/eliminar/<id>')
@login_required
def deletedByAdmin(id):
    if not current_user.admin:
        flash('Forbidden route, unable to access!')
        return redirect(url_for('index'))
    evento= db.session.query(Evento).get(id)
    db.session.delete(evento)
    email=evento.usuario.email
    sendMail(email,'Su evento ha sido borrado!','mail/deleted')
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        mensaje=str(e._message())
        getLogEvents(mensaje)
    print(email)
    flash('Evento eliminado exitosamente!')
    return redirect(url_for('eventsControl'))


#El administrador es capaz de aprobar el evento mediante esta funcion
@app.route('/admin/evento/validate/<id>')
@login_required
def checkEvent(id):
    if not current_user.admin:
        flash('Forbidden route, unable to access!')
        return redirect(url_for('index'))
    evento=db.session.query(Evento).get(id)
    if evento.aprobado==True:
        print("Evento ya aprobado con anterioridad")
        return redirect(url_for('index'))
    elif evento.aprobado==False:
        evento.aprobado=True
        email=evento.usuario.email
        updateDBEvent(evento)
        sendMail(email,'Su evento ha sido aprobado por el administrador!','mail/event-confirm')
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            mensaje=str(e._message())
            getLogEvents(mensaje)
        print(email)
        flash('Evento aprobado!')
        return redirect(url_for('eventsControl',evento=evento))


#Ruta que le permite al administrador del sistema eliminar el comentario deseado de un evento "x"
@app.route('/comentario/eliminar/<id>')
@login_required
def deleteComment(id):
    if not current_user.admin:
        flash('Forbidden route, unable to access!')
        return redirect(url_for('index'))
    comentario = db.session.query(Comentario).get(id)
    eventID= comentario.eventoId
    db.session.delete(comentario)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        mensaje=str(e._message())
        getLogEvents(mensaje)
    flash('El comentario ha sido borrado con exito!')
    return redirect(url_for('eventbyAdmin',id=eventID))
