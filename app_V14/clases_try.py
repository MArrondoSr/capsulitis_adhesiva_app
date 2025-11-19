"""Clases excepciones (heredan de Exception)""" 

class Paciente_existe(Exception):
     pass

class Paciente_no_existe(Exception):
     pass

class Sesion_no_existe(Exception):
     pass

class Error_interno_db(Exception):
     pass

class HC_duplicada(Exception):
     pass

class Usuario_pass_incorrecto(Exception):
     pass
