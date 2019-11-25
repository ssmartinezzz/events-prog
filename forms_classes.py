# - *- coding: utf- 8 - *-
from flask_wtf import FlaskForm #Importa funciones de formulario
from wtforms import StringField, TextField , HiddenField, PasswordField, TextAreaField, SelectField, SubmitField #Importa campos
from wtforms.fields.html5 import EmailField,DateField,TimeField,DateTimeField #Importa campos HTML
from wtforms import validators #Importa validaciones
from flask_wtf.file import FileField, FileRequired, FileAllowed #Importa funciones, validaciones y campos
from app import app, db

#Clase de Registro
class Registerform(FlaskForm): #Creamos una clase que hereda FlaskForm , parte de flask_wtf.

    #Función de validación de nombre de usuario
    def nombre_usuario(form,field):
        #Verificar que no contenga guiones bajors o numeral
        if (field.data.find("_")!= -1) or (field.data.find("#")!= -1) :
            #Mostrar error de validación
             raise validators.ValidationError("El nombre de usuario solo puede contener letras, números y .")
    def cuenta_existente(form,field):
        if Usuario.query.filter_by(email=field.data).first():
            raise ValidationError("Se ha registrado una cuenta con dicho mail")

    def apellido_usuario(form,field):
        #Verificar que no contenga guiones bajors o numeral
        if (field.data.find("_")!= -1) or (field.data.find("#")!= -1) :
            #Mostrar error de validación
             raise validators.ValidationError("El apellido solo puede contener letras, números y .")




    nombre = StringField('Nombre',
    [
        #Definición de validaciones
        validators.Required(message = "Completar nombre"),
        validators.length(min=4, max=25, message='La longitud del nombre de usuario no es válida'),
        #Validación definida por el usuario
        nombre_usuario

    ])

    apellido = StringField('Apellido',
    [
        validators.Required(message = "Completar apellido"),
        apellido_usuario
    ])


    #Definición de campo de texto

    #Definición de campo de contraseña
    password = PasswordField('Contraseña', [
        validators.Required(),
         #El campo de contraseña debe coincidir con el de confirmuar
        validators.EqualTo('confirmar', message='La contraseña no coincide')
    ])

    confirmar = PasswordField('Repetir contraseña')

    #Definición de campo de correo
    email = EmailField('Correo',
    [
        validators.Required(message = "Completar email"),
        validators.Email( message ='Formato de mail incorrecto') #metodo de FlaskForm que nos permite validar que un mail este en formato correcto

    ])

    submit = SubmitField("Registrarse") #Campos para enviar.


class Logform(FlaskForm):

        email = TextField('Email',
        [
            validators.Required(message = "Email requerido"),
            validators.length(min=4, max=40, message='La longitud del nombre de usuario no es válida'),
            #Validación definida por el usuario

        ])

        #Definición de campo de contraseña
        password = PasswordField('Contraseña', [
            validators.Required(message="Introduzca su contraseña"),
             #El campo de contraseña debe coincidir con el de confirmuar
            #validators.EqualTo('confirmar', message='La contraseña no coincide')
        ])
        submit = SubmitField("Iniciar sesion")


class Navegationform(FlaskForm):
        fechainicio = DateField('Fecha',
        [
            validators.Optional() #no es obligatorio cada vez que se filtre un evento hacerlo por fechas por eso optional
        ])

        fechafinal= DateField('Fecha',
        [
            validators.Optional() # Los validadores de las fechas son opcionales, ya que no es obligatorio cada vez que se filtre un evento hacerlo por fechas
        ])
        lista_opciones = [ #Definimos las diferentes opciones por que no se pueden definir directamente en SelectField, debemos crear la tupla para que choices la detecte
        ('null','Seleccione una categoría'),
        ('Deportivo','Deportivo'),
        ('Aprendizaje','Aprendizaje'),
        ('Fiesta','Fiesta'),
        ('Otro','Otro')
    ]
    #Definición de campo select
        opciones = SelectField('Opción', choices=lista_opciones) #Propiedad que es una secuencia de valores | cartel

        submit = SubmitField("Filtrar")
class Commentsform(FlaskForm):
    comentario = StringField('Comentario',
    [
        #Definición de validaciones
        validators.Required(message = "Comentario")
    ])
    fechahora= DateField('Fecha:')
    submit = SubmitField("Enviar")


class Eventform(FlaskForm):
    def opcional(field):
        field.validators.insert(0,validators.Optional())
        #Definición de campo String
    titulo = StringField('Título',
        [
            #Definición de validaciones
            validators.Required(message = "Ingrese el nombre del evento/titulo")
        ])

        #Definición de campo fecha
    fechaevento = DateField('Fecha',
        [
            validators.DataRequired(message="Ingrese una fecha válida")
        ])
    hora=TimeField("Hora del evento",
        [
            validators.Required(message="Completar fecha del evento")
        ])
    tipos_evento = [ #Defino las opciones que puede tomar el selectField
    ('Deportivo','Deportivo'),
    ('Aprendizaje','Aprendizaje'),
    ('Fiesta','Fiesta'),
    ('Otro','Otro')
    ]
    opciones = SelectField('Tipo de evento', choices=tipos_evento) #Propiedad que es una secuencia de valores | cartel
        #Definición de campo de archivo
    imagen = FileField(validators=[ #Tipo de field para archivos
            FileRequired(),
            #Validación de tipo de archivo
            FileAllowed(['jpg', 'png'], 'El archivo debe ser una imagen jpg o png')
        ])
    desc = TextAreaField('Descripcion')
    #Definición de campo submit
    enviar = SubmitField("Enviar")
