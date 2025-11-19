"""MODELO: crea la base Sqlite si no existe y en ella tres tablas (Usuario, Pacientes y Sesiones).
En la primera se guardan los usuarios y contraseñas habilitados. Las otras dos están relacionadas: cuando se modifica una fila en Pacientes
se genera una nueva fila de ese paciente en Sesiones."""

from peewee import *
from clases_try import *
from datetime import datetime
from observador import Sujeto

db = SqliteDatabase('db_casos_capsulitis.db')

class BaseModel(Model):
    class Meta:
        database = db

class Usuario(BaseModel):
    usuario = CharField(unique=True)
    password = CharField()  

class Pacientes(BaseModel):
    num_hc = CharField(unique = True)
    nombre = CharField()
    apellido = CharField()
    sexo = CharField()
    edad = IntegerField()
    ms_afec = CharField()
    ingreso = CharField()
    alta = CharField()
    diabetes = BooleanField(default=False)
    hipotir = BooleanField(default=False)
    climaterio = BooleanField(default=False)
    queloide = BooleanField(default=False)
    depresion = BooleanField(default=False)
    conflictos = BooleanField(default=False)
    ansiedad = BooleanField(default=False)
    fumador = BooleanField(default=False)
    sesiones = IntegerField()
    funcionalidad = IntegerField()
    dolor = IntegerField()

class Sesiones(BaseModel):
    num_hc = CharField()
    nombre = CharField()
    apellido = CharField()
    fecha = CharField(default=lambda: datetime.now().strftime("%d/%m/%Y"))
    sesiones = IntegerField()
    funcionalidad = IntegerField()
    dolor = IntegerField()
    imagen_path = CharField(null=True)

def iniciar_bd():
    db.connect()
    db.create_tables([Usuario, Pacientes, Sesiones], safe=True)  

class Paciente:
    def __init__(self):
        self.observadores = []

    def agregar(self, observador):
        self.observadores.append(observador)

    def notificar(self, *args):
        for obs in self.observadores:
            obs.update(*args)


class DataBase(Sujeto):
    def __init__(self, page):
        super().__init__()
        self.page = page

    def registrar_usuario(self, usuario, password):
        try:
            if Usuario.select().where(Usuario.usuario == usuario).exists():
                return False, "❌ Usuario ya existe"
           
            Usuario.create(usuario=usuario, password=password)
            return True, "✅ Usuario registrado con éxito"
        except Exception as e:
            return False, f"Error: {e}"
        
    def validar_usuario(self, usuario, password):
        """
        Verifica si el usuario y la contraseña existen en la base de datos.
        """
        try:
            usuario_db = Usuario.select().where(
                Usuario.usuario == usuario,
                Usuario.password == password
            ).first()
            return usuario_db is not None
        except Exception:
            return False

    def insertar_en_sesiones(self, **datos):
        try:
            campos_clave = ["num_hc", "nombre", "apellido", "sesiones", "funcionalidad", "dolor"]
            for campo in campos_clave:
                valor = datos.get(campo)
                if valor is None:
                    return False, f"Campo obligatorio faltante: {campo}"
                if isinstance(valor, str) and valor.strip() == "":
                    return False, f"Campo obligatorio vacío: {campo}"

            if "fecha" not in datos or not datos["fecha"]:
                datos["fecha"] = datetime.now().strftime("%d/%m/%Y")

            Sesiones.create(**datos)
            return True, "Sesión insertada correctamente"
        except Exception as e:
            return False, f"Error al insertar sesión: {e}"

    def insertar_paciente_si_no_existe(self, **datos):
        if Pacientes.select().where(Pacientes.num_hc == datos['num_hc']).exists():
            raise Paciente_existe("Ya existe un paciente con ese número de HC")

        Pacientes.create(**datos)
        self.notificar(datos["ingreso"], datos["num_hc"], datos["apellido"])

        return 
    
    def obtener_sesiones(self):
        return Sesiones.select()    

    def obtener_pacientes(self):
        return Pacientes.select().dicts()
    
    def borrar_paciente(self, id_paciente):
        try:
            paciente = Pacientes.get(Pacientes.id == id_paciente)
            if paciente:
                paciente.delete_instance()
                return 
            
        except DoesNotExist:
            raise Paciente_no_existe()
    
    def borrar_fila_sesion(self, id_sesion): 
        try:
            sesion = Sesiones.get(Sesiones.id == id_sesion)
            if sesion:
                sesion.delete_instance()
                return 
            
        except DoesNotExist:
            raise Sesion_no_existe()
    
    def consultar_paciente(self, num_hc=None, apellido=None):
        if num_hc:
            return Pacientes.select().where(Pacientes.num_hc == num_hc)
        elif apellido:
            return Pacientes.select().where(Pacientes.apellido == apellido)
        else:
            return []

    def obtener_datos_paciente_por_hc_apellido(self,hc_buscado=None, apellido_buscado=None):
        if hc_buscado:
           return Pacientes.get_or_none(Pacientes.num_hc == hc_buscado)
        
        elif apellido_buscado:
            return Pacientes.get_or_none(Pacientes.apellido == apellido_buscado)
        
        return None
    
    def obtener_datos_paciente_por_id(self, id_a_modificar):
        return Pacientes.get(Pacientes.id == id_a_modificar)
    
    def actualizar_paciente_en_base(self, mi_id, valores):
        """
        Actualiza la base y verifica que la fila seleccionada y modificada no repita un número
        de H.C. antes de aplicar los cambios.
        """
        
        try:
            paciente = Pacientes.get_by_id(mi_id)
            
            if Pacientes.select().where(Pacientes.num_hc == valores['num_hc'], Pacientes.id != mi_id).exists():
                raise HC_duplicada()

            for campo, valor in valores.items():
                setattr(paciente, campo, valor)

            paciente.save()
            return True, "Paciente actualizado correctamente" 

        except DoesNotExist:
            raise Paciente_no_existe()
        
        except HC_duplicada:
            return False, "Número de HC duplicado"

        except Exception as e:
            raise Error_interno_db
        
    def obtener_historial_sesiones(self, hc_buscado=None, apellido_buscado=None):
        """
        Filtra las filas para mostrar en la pantalla solo las
        del paciente seleccionado (por número de HC o apellido).
        """
        query = Sesiones.select()

        if hc_buscado:
            query = query.where(Sesiones.num_hc == hc_buscado)
        elif apellido_buscado:
            query = query.where(Sesiones.apellido.contains(apellido_buscado))

        return list(query)
