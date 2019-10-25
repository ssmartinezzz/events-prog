# -*- coding: utf-8 -*-
import datetime
from funciones import *
from flask import Flask,request,render_template,redirect, url_for
from flask_wtf import CSRFProtect  # importar para proteccion CSRF
from flask import flash  # importar para mostrar mensajes flash
from forms_classes import *  # importar clase de formulario
from werkzeug.utils import secure_filename
import os.path
from app import db,login_manager,app
from models import *
import os
from emailfunctions import *
from flask_login import login_required, login_user, logout_user, current_user, LoginManager



csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

def mysql_query(query):
    return query.statement.compile(compile_kwargs={"literal_binds": True})



@login_manager.unauthorized_handler #Método que cuando intente acceder a ruta sin estar logeado muestre lo siguiente.
def unauthorized_callback():
    flash('Para continuar debe iniciar sesión.','warning')
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
    flash('Logged off!','warning')
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
        eventos=eventos.filter(Evento.fecha>=fechainicio)
    if(fechafinal!=None and fechafinal!=''):
        formularionav.fechafinal.data= datetime.datetime.strptime(fechafinal, "%Y-%m-%d").date()
        eventos=eventos.filter(Evento.fecha<=fechafinal)
    if(opciones!=None and opciones!='' and opciones!='null'and opciones!='None'):
        formularionav.opciones.data = opciones
        eventos = eventos.filter(Evento.tipo==opciones)
    eventos = Evento.query.order_by(Evento.fecha).paginate(pag,pag_tam,error_out=False)
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
def registro():
    formulario = Registro()  # Instanciar formulario de registro
    if formulario.validate_on_submit():  # Si el formulario ha sido enviado y es validado correctamente
        flash('Usuario registrado exitosamente')  # Mostrar mensaje
        mostrar_datos(formulario)  # Imprimir datos por consola
        createUser(formulario.nombre.data,formulario.apellido.data,formulario.email.data,formulario.password.data,admin=True)
        email=formulario.email.data
        sendMail(email,'Su cuenta de EventZ ha sido creada!','mail/newaccount')
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
def eventos():
    listaeventos=db.session.query(Evento).filter(Evento.usuarioId==current_user.usuarioId).all()
    return render_template('my-events.html',listaeventos=listaeventos)

# RUTA Y DUNCION PARA LA CREACION DE UN EVENTO
@app.route('/creacion', methods=["POST", "GET"])
@login_required
def crear():
    formulario = EventoCrear()
    if formulario.validate_on_submit():
        f = formulario.imagen.data  # Obtener imagen
        filename = secure_filename(f.filename)
        f.save(os.path.join('static/Fondo/', filename))
        flash("Evento creado exitosamente!")
        showEve(formulario)
        createEvent(formulario.titulo.data,formulario.fechaevento.data,formulario.hora.data,formulario.desc.data,filename,formulario.opciones.data,current_user.usuarioId)
        return redirect(url_for('eventos'))
    return render_template('create-event.html', formulario=formulario, destino="crear")

#Ruta que nos permite actualizar los datos de un evento traido de db, donde al ser igualados y llenados en el formulario podemos efectuar los cambios
@app.route('/update/evento/<id>', methods=["POST", "GET"])
@login_required
def actualizar(id):
    evento = db.session.query(Evento).get(id)
    formulario=EventoCrear(obj=evento)
    EventoCrear.opcional(formulario.imagen)
    if formulario.validate_on_submit():
        flash('Las modificaciones del evento han sido guardadas con éxito!!!')
        showEve(formulario)
        evento.nombre=formulario.titulo.data
        evento.fecha=formulario.fechaevento.data
        evento.hora=formulario.hora.data
        evento.tipo=formulario.opciones.data
        evento.descripcion=formulario.desc.data
        evento.imagen=formulario.imagen.data

        actualizareve(evento)
        return redirect(url_for('index'))
    else:
            formulario.titulo.data=evento.nombre
            formulario.fechaevento.data=evento.fecha
            formulario.hora.data=evento.hora
            formulario.opciones.data=evento.tipo
            formulario.desc.data=evento.descripcion
            formulario.imagen.data=evento.imagen
    return render_template('create-event.html', formulario=formulario, destino="actualizar")
@app.route('/evento/actualizar/<evento>')
@login_required
def actualizareve(evento):
    print("Actualizando evento!")
    db.session.add(evento)
    db.session.commit()


# RUTA Y FUNCION PARA LISTAR LOS EVENTOS CON LOS COMENTARIOS Y CREARLOS
@app.route('/evento/<id>', methods=["POST", "GET"])
@login_required
def mostrarevento(id):
    listaeventos = listar_eventos()
    evento = db.session.query(Evento).get(id)
    #listacomentarios = comentarios() #Este es el csv
    commentList =db.session.query(Comentario).filter(Comentario.eventoId==id).order_by(Comentario.fechahora).all()
    form = Comentarios()
    if form.validate_on_submit():
        flash('Comentario Enviado')
        pCommentary(form)
        createComment(form.comentario.data,current_user.usuarioId,id)
        return redirect(url_for('mostrarevento',id=id))
    return render_template('evento.html', form=form, id=id, evento=evento, commentList=commentList, mostrarevento=mostrarevento,listaeventos=listaeventos)
@app.route('/comentary/create/<contenido>/<usuarioId>/<eventoId>')
@login_required
def createComment(contenido,usuarioId,eventoId):
    usuario=db.session.query(Usuario).get(usuarioId)
    evento=db.session.query(Evento).get(eventoId)
    fechahora=db.func.current_timestamp()
    comment = Comentario(contenido=contenido,fechahora=fechahora,evento=evento,usuario=usuario)
    db.session.add(comment)
    db.session.commit()


#Funcion que permite por el panel de mis eventos eliminar el evento que se toque con el respectivo id
@app.route('/evento/eliminar/<id>')
@login_required
def deleteEvent(id):
    evento= db.session.query(Evento).get(id)
    db.session.delete(evento)
    db.session.commit()
    flash('Evento eliminado exitosamente!')
    return redirect(url_for('eventos'))


"RUTAS QUE SOLO PUEDE ACCEDER EL ADMINISTRADOR DEL SITIO, CONTIENE LAS FUNCIONES"

#Ruta que muestra el menu de opciones disponibles al administrador
@app.route('/admin/menu')
@login_required
def menuadmin():
    if not current_user.is_admin==False:
        flash('Forbidden route, unable to access!')
        return redirect(url_for('index'))

    else:
        return render_template('admin-menu.html')

#Ruta que le permite visibilizar los eventos disponibles a controlar.
@app.route('/admin/regular/')
@login_required
def regular():
    if not current_user.is_admin==False:
        flash('Forbidden route, unable to access!')
        return redirect(url_for('index'))

    else:
        listaeventos=db.session.query(Evento).all()
        return render_template('admineventos.html',listaeventos=listaeventos)

#Ruta para que el admin regule un evento "x".
@app.route('/admin/evento/<id>',methods=["POST","GET"])
@login_required
def eventoad(id):
    if current_user.is_admin==False:
        flash('Forbidden route, unable to access!')
        return redirect(url_for('index'))
    else:
        comentadmin = db.session.query(Comentario).filter(Comentario.eventoId ==id).order_by(Comentario.fechahora).all()
        evento = db.session.query(Evento).get(id)
        return render_template('event-adminview.html', comentadmin=comentadmin,id=id,evento=evento)


#Ruta que elimina el evento que el admin desee, (NO ES DESAPROBAR)
@app.route('/eventoadmin/eliminar/<id>')
@login_required
def deletedByAdmin(id):
    if not current_user.is_admin==False:
        flash('Forbidden route, unable to access!')
        return redirect(url_for('index'))
    else:
        evento= db.session.query(Evento).get(id)
        db.session.delete(evento)
        email=evento.usuario.email
        sendMail(email,'Su evento ha sido borrado!','mail/mensaje')
        print(email)
        db.session.commit()
        flash('Evento eliminado exitosamente!')
        return redirect(url_for('regular'))


#El administrador es capaz de aprobar el evento mediante esta funcion
@app.route('/admin/evento/validate/<id>')
@login_required
def checkEvent(id):
    if not current_user.is_admin==False:
        flash('Forbidden route, unable to access!')
        return redirect(url_for('index'))
    else:
        evento=db.session.query(Evento).get(id)
        evento.aprobado=True
        email=evento.usuario.email
        actualizareve(evento)
        flash('Evento aprobado!')
        sendMail(email,'Su evento ha sido aprobado por el administrador!','mail/event-confirm')
        print(email)
        db.session.commit()
        return redirect(url_for('regular',evento=evento))


#Ruta que le permite al administrador del sistema eliminar el comentario deseado de un evento "x"
@app.route('/comentario/eliminar/<id>')
@login_required
def deleteComment(id):
    if not current_user.is_admin==False:
        flash('Forbidden route, unable to access!')
        return redirect(url_for('index'))

    else:
        comentario = db.session.query(Comentario).get(id)
        eventID= comentario.eventoId
        db.session.delete(comentario)
        db.session.commit()
        flash('El comentario ha sido borrado con exito!','warning')
        return redirect(url_for('eventoad',id=eventID))



"""La ruta no tiene template todavia y no esta en uso
@app.route('/usuario/eliminar/<id>')
@login_required
def deleteUsuario(id):
    if current_user.is_admin==True:
        usuario = db.session.query(Usuario).get(id)
        db.session.delete(usuario)
        db.session.commit()
        return redirect(url_for('listarUsuarios'))
    else:
        flash('Forbidden route, unable to access!')
        return redirect(url_for('index'))
"""



app.run(debug=True)
