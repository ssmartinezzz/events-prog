# -*- coding: utf-8 -*-
from funciones import *
from flask import Flask
from flask import render_template
from flask_wtf import CSRFProtect  # importar para proteccion CSRF
from flask import flash  # importar para mostrar mensajes flash
# importar para permitir redireccionar y generar url
from flask import redirect, url_for
from forms_classes import *  # importar clase de formulario
import datetime  # importar funciones de fecha
# Importa seguridad nombre de archivo
from werkzeug.utils import secure_filename
import os.path
from app import db
from models import *

app = Flask(__name__)
csrf = CSRFProtect(app)
app.secret_key = 'esta_es_la_clave_secreta'

def mysql_query(query):
    return query.statement.compile(compile_kwargs={"literal_binds": True})

@app.route('/')
@app.route('/<int:pag>', methods=["POST", "GET"])
def index(pag=1):
    formularionav=Navegation()
    pag_tam = 6
    eventos = Evento.query.order_by(Evento.fecha).paginate(pag,pag_tam,error_out=False)
    if formularionav.validate_on_submit():
        flash('Aplicando filtros')
        navbar(formularionav)
        return redirect(url_for('index'))
    return render_template('index.html', formularionav=formularionav,eventos=eventos)
# Ruta para el inicio de sesion
@app.route('/iniciar', methods=["POST", "GET"])
def logIn():
    formulariolog = Logeo()  # Instanciar formulario de registro
    if formulariolog.validate_on_submit():  # Si el formulario ha sido enviado y es validado correctamente
        flash('Usuario Logeado exitosamente')  # Mostrar mensaje
        getUser(formulariolog)  # Imprimir datos por consola
        return redirect(url_for('index'))
    return render_template('login.html', formulariolog=formulariolog)


# RUTA PARA REGISTRO DE UN NUEVO USUARIO
@app.route('/registro', methods=["POST", "GET"])
def registro():
    formulario = Registro()  # Instanciar formulario de registro
    if formulario.validate_on_submit():  # Si el formulario ha sido enviado y es validado correctamente
        flash('Usuario registrado exitosamente')  # Mostrar mensaje
        mostrar_datos(formulario)  # Imprimir datos por consola
        createUser(formulario.nombre.data,formulario.apellido.data,formulario.email.data,formulario.password.data,admin=False)
        return redirect(url_for('index'))
    return render_template('registro.html', formulario=formulario)


@app.route('/menu')
def menu():
    return render_template('main-menu.html')


@app.route('/mis-eventos')
def eventos():
    listaeventos=db.session.query(Evento).filter(Evento.usuarioId==282).all()

    return render_template('my-events.html',listaeventos=listaeventos)

# RUTA Y DUNCION PARA LA CREACION DE UN EVENTO
@app.route('/creacion', methods=["POST", "GET"])
def crear():
    formulario = EventoCrear()
    if formulario.validate_on_submit():
        f = formulario.imagen.data  # Obtener imagen
        filename = secure_filename(f.filename)
        f.save(os.path.join('static/Fondo/', filename))
        flash("Evento creado exitosamente!")
        showEve(formulario)
        createEvent(formulario.titulo.data,formulario.fechaevento.data,formulario.hora.data,formulario.desc.data,filename,formulario.opciones.data,280)
        return redirect(url_for('crear'))
    return render_template('create-event.html', formulario=formulario, destino="crear")

#Ruta que nos permite actualizar los datos de un evento traido de db, donde al ser igualados y llenados en el formulario podemos efectuar los cambios
@app.route('/update', methods=["POST", "GET"])
def actualizar():
    evento = db.session.query(Evento).get(108)
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
        createEvent(formulario.titulo.data,formulario.fechaevento.data,formulario.hora.data,formulario.desc.data,formulario.imagen.data,formulario.opciones.data,203)
        return redirect(url_for('index'))
    else:
            formulario.titulo.data=evento.nombre
            formulario.fechaevento.data=evento.fecha
            formulario.hora.data=evento.hora
            formulario.opciones.data=evento.tipo
            formulario.desc.data=evento.descripcion
            formulario.imagen.data=evento.imagen
    return render_template('create-event.html', formulario=formulario, destino="actualizar")


# RUTA Y FUNCION PARA LISTAR LOS EVENTOS CON LOS COMENTARIOS Y CREARLOS
@app.route('/evento/<id>', methods=["POST", "GET"])
def mostrarevento(id):
    listaeventos = listar_eventos()
    evento = db.session.query(Evento).get(id)
    listacomentarios = comentarios() #Este es el csv
    formulario = Comentarios()
    if formulario.validate_on_submit():
        flash('Comentario Enviado')
        pCommentary(formulario)
        return redirect(url_for('mostrarevento',id=evento['eventoId']))

    return render_template('evento.html', formulario=formulario, id=id, evento=evento, listacomentarios=listacomentarios, mostrarevento=mostrarevento,listaeventos=listaeventos)


@app.route('/user')
def user():
    return render_template('evento.html', id=id, evento=evento, listacomentarios=listacomentarios)

#Ruta que muestra el menu de opciones disponibles al administrador
@app.route('/admin/menu')
def menuadmin():
    return render_template('admin-menu.html')

#Ruta que le permite visibilizar los eventos disponibles a controlar.
@app.route('/admin/regular/')
def regular():
    listaeventos=db.session.query(Evento).filter(Evento.usuarioId==282).all()
    #evento=db.session.query(Evento).filter(Evento.eventoId==id).one()
    return render_template('admineventos.html',listaeventos=listaeventos)

#Ruta para que el admin regule un evento "x", y que en el mismo utilizando el formulario de hacer comentario pueda hacer un comentario.
@app.route('/admin/evento/<id>',methods=["POST","GET"])
def eventoad(id):
    #listaeventos=listar_eventos()
    formulario =Comentarios()
    comentadmin = comentarios()
    evento = db.session.query(Evento).get(id)
 #Este es el csv
    if formulario.validate_on_submit():
        flash('Comentario Enviado')
        pCommentary(formulario)
        return redirect(url_for('eventoad',id=evento['eventoId']))
    return render_template('event-adminview.html', comentadmin=comentadmin,id=id,evento=evento,formulario=formulario)

def deleteEvent(id):
    evento = db.session.query(Evento).get(id)
    db.session.delete(evento)
    db.session.commit()
    flash('Evento eliminado con exito!')
    return redirect(url_for('regular'))






@app.route('/comentario/list')
def listarComentarios():
    # EJ: persona/list
    comentarios = db.session.query(Comentario).all()
    return render_template('comentarios.html',comentarios=comentarios,filtro="")

@app.route('/comentario/crear/<comentarioId>/<texto>/<fechahora>')
def crearComentario(comentarioId,texto,fechahora):
    comentario = Comentario(comentarioId=comentarioId,texto=texto,fechahora=fechahora)
    db.session.add(comentario)
    db.session.commit()
    return render_template('comentario.html',comentario=comentario)

@app.route('/comentario/getById/<id>')
def getComentarioById(id):
    comentario =  db.session.query(Comentario).get(id)
    return render_template('comentario.html',comentario=comentario)

@app.route('/comentario/eliminar/<id>')
def eliminarComentario(id):
    comentario = db.session.query(Comentario).get(id)
    db.session.delete(comentario)
    db.session.commit()
    return redirect(url_for('listarComentarios'))

@app.route('/usuario/eliminar/<id>')
def deleteUsuario(id):
    usuario = db.session.query(Usuario).get(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('listarUsuarios'))



app.run(debug=True)
