"""
Utiliza el patrón observador para registrar los nuevos ingresos de la base de datos
en el archivo lista_de_ingresos.txt
"""
from datetime import datetime
import os
import flet as ft

class Sujeto:
    def __init__(self):
        self.observadores = []

    def agregar(self, obj):
        self.observadores.append(obj)

    def notificar(self, *args):
        for observador in self.observadores:
            observador.update(*args)


class Observador:
    def update(self, *args):
        raise NotImplementedError("Método update() no implementado.")


class ConcreteObserverA(Observador):
    def __init__(self, sujeto, vista):
        self.sujeto = sujeto
        self.vista = vista
        self.sujeto.agregar(self)

    def update(self, ingreso, num_hc, apellido):
        try:
            with open("lista_de_ingresos.txt", "a", encoding="utf-8") as archivo:
                archivo.write(
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                    f"Alta registrada en fecha {ingreso}. Paciente H.C. {num_hc}, apellido: {apellido}\n")
                self.vista.mostrar_aviso(
                    "✅  Alta registrada en archivo", 
                    color=ft.Colors.GREEN)
        except Exception as e:
            self.vista.mostrar_aviso(
                f"❌ No se pudo registrar el alta en archivo: {e}", 
                color=ft.Colors.RED
            )