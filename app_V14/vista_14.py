"""VISTA: crea dos GUI utilizando Flet. En la primera se cargan y visualizan los datos del paciente cuando ingresa al tratamiento 
(primera sesión); en la segunda se carga esa primera sesión y en cada sesión subsiguiente, cuando se modifica la tabla en la ventana 1
se agrega la sesión correspondiente con su fecha y valores de funcionalidad y dolor y la imagen correspondiente.
De una ventana a la otra se pasa con los botones Principal y Sesiones.
El usuario puede acceder a la base, grabar, borrar, consultar y/o modificar datos en la misma a través de campos de entrada y 
la tabla de la ventana principal que muestra el contenido de la tabla Pacientes en la base. 
En la segunda ventana (Sesiones) puede consultar el historial de cada paciente, buscando por número de HC o por apellido, 
ver cómo evolucionaron sus valores, las imagenes de cada sesión y generar un gráfico de barras con esos valores de funcionalidad
y dolor a lo largo del tiempo.
Se muestran las alertas de error e indicaciones en una ventana de avisos."""

import flet as ft
from datetime import datetime
import re
from modelo_14 import DataBase, Pacientes
from cls_boton import Boton001, Boton002, Boton003, Boton004
from regex_file import Regex_01
from clases_try import *
import shutil
import os
from decoradores import indicador_baja, indicador_modificacion
from modelo_14 import Sesiones
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64
from observador import Sujeto
import asyncio
from matplotlib.colors import LightSource
from matplotlib.artist import Artist
from io import BytesIO
import base64
import numpy as np
from cls_boton import Boton005
import plotly.graph_objects as go
from filtros_graf import BaseFilter, GaussianFilter, DropShadowFilter, LightFilter, FilteredArtistList, smooth1d, smooth2d, LightSource
from peewee import fn

class VistaDos(Sujeto):
    def __init__(self, page):

        self.obj_db = DataBase(page)
        self.page = page
        self.selected_row_ref = ft.Ref[int]()  
        self.selected_row_ref_dos = ft.Ref[int]()  
        #self.page.on_route_change = self.route_change  
        self.page.go("/") 
        self.page.update()
        self.regex_app = Regex_01()
        #grafico_container = ft.Container(width=520, height=420, bgcolor="#F5F5F5", alignment=ft.alignment.center)
        ############ AGREGADO 
   
        # ─── Carpeta para imágenes ─────────────────
        self.CARPETA_IMAGENES = os.path.join(os.getcwd(), "imagenes_sesiones")
        if not os.path.exists(self.CARPETA_IMAGENES):
            os.makedirs(self.CARPETA_IMAGENES)

        self.file_picker = ft.FilePicker()
        self.ruta_imagen = ft.Text(value="", visible=False)  
        self.file_picker.on_result = self.on_file_picked
        self.page.overlay.append(self.file_picker)

    def archivos_seleccionados(self, e: ft.FilePickerResultEvent):
        if e.files:
            ruta_origen = e.files[0].path
            nombre_archivo = os.path.basename(ruta_origen)

            carpeta_destino = self.CARPETA_IMAGENES
            os.makedirs(carpeta_destino, exist_ok=True)

            ruta_destino = os.path.join(carpeta_destino, nombre_archivo)
            shutil.copy2(ruta_origen, ruta_destino)
            ruta_relativa = os.path.relpath(ruta_destino, os.getcwd())
            self.ruta_imagen.value = ruta_relativa
            self.ruta_imagen.update()  
 
    # def route_change(self, route):
    #     self.page.clean()

    #     if route == "/":
    #         if not hasattr(self, "gui_creada"):
    #             self.crear_gui()
    #             self.gui_creada = True
    #         self.mostrar_datos()

    #     elif route == "/paciente":
    #         if not hasattr(self, "gui_dos_creada"):
    #             self.crear_gui_dos()
    #             self.gui_dos_creada = True
    #         self.mostrar_datos_dos()

    #     elif route == "/graficos":
    #         if not hasattr(self, "vista_grafico_creada"):
    #             self.vista_grafico()
    #             self.vista_grafico_creada = True
    #         #self.mostrar_datos_dos()

    #     self.page.update()
     
    def calendarios(self):
        self.fecha_ing = ft.DatePicker(
                        first_date=datetime(year=2023, month=10, day=1),
                        last_date=datetime(year=2030, month=10, day=1),
                        on_change=self.agrega_fecha_01)

        self.fecha_alta = ft.DatePicker(
                        first_date=datetime(year=2023, month=10, day=1),
                        last_date=datetime(year=2030, month=10, day=1),
                        on_change=self.agrega_fecha_02)

        self.page.overlay.append(self.fecha_ing)
        self.page.overlay.append(self.fecha_alta)

    def abrir_fecha_ing(self):
        self.fecha_ing.open = True
        self.page.update()

    def abrir_fecha_alta(self):
        self.fecha_alta.open = True
        self.page.update()

    def crear_gui(self):
        """Genera la ventana principal con sus widgets"""        

        self.page.title = "Listado de pacientes Capsulitis Adhesiva"
        self.pantalla_completa = True
        self.calendarios()
        self.page.theme_mode =ft.ThemeMode.SYSTEM
        self.page.update()
     
        self.titulo_01 = ft.Container(
            ft.Text(
                "COMPLETE TODOS LOS CAMPOS CON LA INFORMACIÓN DEL PACIENTE", 
                size=17, 
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.BOLD,
                ), 
                top=0,
                left=20
            )
        self.titulo_02 = ft.Container(
            ft.Text(
                "INGRESE UN NÚMERO DE HISTORIA CLÍNICA O UN APELLIDO\n             EN LOS CAMPOS CORRESPONDIENTES Y", 
                size=17, 
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.BOLD,
                ), 
                top=123,
                left=490
            )
        self.selected_row_ref = ft.Ref[int]()  
        self.ruta_imagen = ft.TextField(visible=False)

        self.text_box_01 = ft.TextField(
            label="Historia Clínica", 
            width=100, 
            color='black',
            border_color='white',
            bgcolor=ft.Colors.YELLOW_200
        )

        self.text_box_02 = ft.TextField(
            label="Nombre", 
            width=150, 
            color='black',
            border_color='white',
            bgcolor=ft.Colors.YELLOW_200
        )

        self.text_box_03 = ft.TextField(
            label="Apellido", 
            width=200, 
            color='black',
            border_color='white',
            bgcolor=ft.Colors.YELLOW_200
        )

        self.text_box_04 = ft.Dropdown(
            width=150, 
            color='black',
            border_color='white',
            filled=False,
            options=[
                ft.dropdown.Option(
                    "Sexo"
                ),
                ft.dropdown.Option(
                    "Masculino"
                ),
                ft.dropdown.Option(
                    "Femenino"
                )],
                value="Sexo")
        
        self.text_box_05 = ft.Dropdown(
            width=110, 
            color='black',
            border_color='white',
            filled=False,
            options=[
                ft.dropdown.Option(
                    'Edad'
                )]+[
                ft.dropdown.Option(i) for i in range(15, 101)],
                value="Edad"
            )
        
        self.text_box_06 = ft.Dropdown(
            width=170, 
            color='black',
            border_color='white',
            filled=False,
            options=[
                ft.dropdown.Option(
                    "Hombro"
                ),
                ft.dropdown.Option(
                    "Derecho D"
                ),
                ft.dropdown.Option(
                    "Derecho ND"
                ),
                ft.dropdown.Option(
                    "Izquierdo D"
                ),
                ft.dropdown.Option(
                    "Izquierdo ND"
                )
            ], 
            value="Hombro"
        )
        
        self.boton_fecha_ing = ft.Container(
            ft.ElevatedButton(
                " ", 
                icon=ft.Icons.CALENDAR_MONTH, 
                on_click=lambda e: self.abrir_fecha_ing(),
            ),
            width=30, 
            height=30, 
            top=0,
            left=1085
        )

        self.boton_fecha_alta = ft.Container(
            ft.ElevatedButton(
                " ", 
                icon=ft.Icons.CALENDAR_MONTH, 
                on_click=lambda e: self.abrir_fecha_alta(),
            ),
            width=30, 
            height=30,
            top=0,
            left=1225
        )
        
        self.text_box_07 = ft.TextField(
            label="Fecha Ingreso", 
            width=120, 
            color='black',
            border_color='white',
            bgcolor=ft.Colors.YELLOW_200
        )

        self.text_box_08 = ft.TextField(
            label="Fecha Alta", 
            width=120, 
            color='black',
            border_color='white',
            bgcolor=ft.Colors.YELLOW_200
        )

        self.row_1 = ft.Row(
            controls=[
                self.text_box_01, 
                self.text_box_02, 
                self.text_box_03, 
                ft.Container(
                    content=self.text_box_04,
                    bgcolor=ft.Colors.YELLOW_200, 
                    padding=0, 
                    border_radius=5
                ),
                ft.Container(
                    content=self.text_box_05, 
                    bgcolor=ft.Colors.YELLOW_200, 
                    padding=0, 
                    border_radius=5
                ), 
                ft.Container(
                    content=self.text_box_06, 
                    bgcolor=ft.Colors.YELLOW_200, 
                    padding=0, 
                    border_radius=5
                ), 
                self.text_box_07, 
                self.text_box_08
            ],
            spacing=15
        )

        self.row_1_container = ft.Container(
            content=self.row_1,
            top=25,
            left=20
        )
    
        self.check_01 = ft.Checkbox(label="Diabetes")
        self.check_02 = ft.Checkbox(label="Hipotiroidismo")
        self.check_03 = ft.Checkbox(label="Climaterio")
        self.check_04 = ft.Checkbox(label="Cicatriz Queloide")
        self.check_05 = ft.Checkbox(label="Antidepresivos")
        self.check_06 = ft.Checkbox(label="Conflictos Laborales / Familiares")
        self.check_07 = ft.Checkbox(label="Trast. Ansiedad")
        self.check_08 = ft.Checkbox(label="Fumador")

        self.row_2 = ft.Row(
            controls=[
                self.check_01, 
                self.check_02, 
                self.check_03, 
                self.check_04, 
                self.check_05, 
                self.check_06, 
                self.check_07, 
                self.check_08,
            ],
            spacing=15
        )

        self.row_2_container = ft.Container(
            content=self.row_2,
            top=85,
            left=20,
            bgcolor=ft.Colors.YELLOW_200,
            width=1200, 
            border_radius=5
        )

        self.titulo_11 = ft.Container(
            ft.Text(
                "Sesiones", 
                size=15, 
                color=ft.Colors.WHITE, 
                weight=ft.FontWeight.BOLD
            ),
            top=127,
            left=20
        )

        self.text_box_11 = ft.Dropdown(
            label="",
            width=80, 
            color='black',
            border_color='white',
            filled=False,
            options=[
                ft.dropdown.Option(i) for i in range(0, 50)
            ],
            value=0
        )

        self.titulo_12 = ft.Container(
            ft.Text(
                "Funcionalidad", 
                size=15, 
                color=ft.Colors.WHITE, 
                weight=ft.FontWeight.BOLD
            ), 
            top=127,
            left=119
        )

        self.text_box_12 = ft.Dropdown(
            label="",
            width=80, 
            color='black',
            border_color='white',
            filled=False,
            options=[
                ft.dropdown.Option(i) for i in range(0, 11)
            ],
            value=0
        )

        self.titulo_13 = ft.Container(
            ft.Text(
                "Dolor", 
                size=15, 
                color=ft.Colors.WHITE, 
                weight=ft.FontWeight.BOLD
            ), 
            top=127,
            left=255
        )

        self.text_box_13 = ft.Dropdown(
            label="",
            width=80, 
            color='black',
            border_color='white',
            filled=False,
            options=[
                ft.dropdown.Option(i) for i in range(0, 11)
            ],
            value=0
        )

        self.boton_07 = ft.FilledButton(
            content=ft.Icon(
                name=ft.Icons.TOUCH_APP, 
                color=ft.Colors.WHITE, 
                size=30
            ), 
            width=55, 
            height=55, 
            style = ft.ButtonStyle(
                shape =ft.CircleBorder(), 
                bgcolor=ft.Colors.TEAL_200,
                color=ft.Colors.WHITE,
                overlay_color=ft.Colors.BLACK,
                elevation=10,
                padding=5
            ),
            on_click=lambda e: self.consulta()
        )

        self.titulo_04 = ft.Row(
            controls=[
                ft.Icon(
                    name=ft.Icons.ARROW_LEFT, 
                    color=ft.Colors.WHITE, 
                    size=30
                ),
                ft.Text(
                    "CLICK PARA CONSULTAR", 
                    size=17,
                    color=ft.Colors.WHITE, 
                    weight=ft.FontWeight.BOLD
                ),
            ],
            spacing=5, 
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        self.row_5 = ft.Row(
            controls=[
                self.boton_07, 
                self.titulo_04,
            ],
            spacing=20
        )

        self.row_5_container = ft.Container(
            content=self.row_5,
            top=155,
            left=500,
            width=600
        )

        self.row_3 = ft.Row(
            controls=[
                ft.Container(
                    content=self.text_box_11, 
                    bgcolor=ft.Colors.YELLOW_200, 
                    padding=0, 
                    border_radius=5
                ),
                ft.Container(
                    content=self.text_box_12, 
                    bgcolor=ft.Colors.YELLOW_200, 
                    padding=0, 
                    border_radius=5
                ),
                ft.Container(
                    content=self.text_box_13, 
                    bgcolor=ft.Colors.YELLOW_200, 
                    padding=0, 
                    border_radius=5
                )
            ],
            spacing=30
        )

        self.row_3_container = ft.Container(
            content=self.row_3,
            top=150,
            left=20
        )

        self.avisos = ft.Text(
            " ", 
            color=ft.Colors.WHITE, 
            weight=ft.FontWeight.NORMAL,
            style=ft.TextStyle(size=25)
        )

        self.row_4 = ft.Row(controls=[self.avisos])

        self.fondo = ft.Stack(
            controls=[
                ft.Card(
                    content=ft.Container(
                        content=self.row_4,
                        width=820, 
                        height=70,
                        bgcolor=ft.Colors.WHITE60,
                        border_radius=8,
                        padding=10
                    ), 
                    elevation=10,
                    top=220, 
                    left=470
                )
            ], 
            width=1500, 
            height=1000
        ) 
       
        self.boton_01 = Boton001("Guardar", self.agregar_fila, top=220, left=20)
        self.boton_02 = Boton001("Borrar", lambda e: self.borrar_fila(), top=220, left=145)
        self.boton_03 = Boton001("Editar", lambda e: self.cargar_datos_para_modificar(self.data_table), top=260, left=20)
        self.boton_04 = Boton001("Actualizar",lambda e: self.actualizar_datos(), top=260, left=145)
        self.boton_05 = Boton001("Ver Todos", lambda e: self.mostrar_datos(), top=220, left=270)
        self.boton_06 = Boton001("Limpiar Pantalla", lambda e: self.limpiar(), top=260, left=270)
        self.boton_09 = Boton004("Ir a Pantalla Sesiones", lambda e: self.page.go("/paciente"), top=150, left=1270)
        self.boton_10 = Boton001("Cargar Imagen", lambda e: self.file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["jpg", "png", "jpeg"]
        ), top=160, left=350)
        
        boton_cerrar_sesion = Boton002(
            "CERRAR SESIÓN",
            lambda e: self.page.go("/login"), 
            top=23,
            left=1270,
            icono=ft.Icons.LOGOUT
        )

        self.form_vars = {
                    "num_hc": self.text_box_01,
                    "nombre": self.text_box_02,
                    "apellido": self.text_box_03,
                    "sexo": self.text_box_04,
                    "edad": self.text_box_05,
                    "ms_afec": self.text_box_06,
                    "ingreso": self.text_box_07,
                    "alta": self.text_box_08,
                    "diabetes": self.check_01,
                    "hipotir": self.check_02,
                    "climaterio": self.check_03,
                    "queloide": self.check_04,
                    "depresion": self.check_05,
                    "conflictos": self.check_06,
                    "ansiedad": self.check_07,
                    "fumador": self.check_08,
                    "sesiones": self.text_box_11,
                    "funcionalidad": self.text_box_12,
                    "dolor": self.text_box_13,
                    "imagen_path": self.ruta_imagen,
                }
        
        self.data_table = ft.DataTable(
            bgcolor=ft.Colors.BLUE_GREY_100,
            border=ft.border.all(width=5, color = ft.Colors.WHITE),
            border_radius=10,
            vertical_lines=ft.Border(5, ft.Colors.WHITE),
            columns=[
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "ID", 
                            style=ft.TextStyle(
                                size=10, 
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK,
                            ), 
                            text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "H.C",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                            ), 
                            text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "Nombre",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                                ), 
                                text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "Apellido",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                                ), 
                                text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "Sexo",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                                ), 
                                text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "Edad",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                                ), 
                                text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "Hombro",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                                ), 
                                text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "Ingreso",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                                ), 
                                text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "Alta",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                                ), 
                                text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "Diabetes",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                                ), 
                                text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "Hipotir.",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                                ), 
                                text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "Climat.",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                                ), 
                                text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "Cic. Quel",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                                ), 
                                text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "Antidepr.",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                                ), 
                                text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "Confl.",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                                ), 
                                text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "T. Ans.",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                                ), 
                                text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "Fumador",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                                ), 
                                text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "Sesiones",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                                ), 
                                text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "Funcion.",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                                ), 
                                text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text(
                            "Dolor",
                            style=ft.TextStyle(
                                size=10,
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.BLACK
                                ), 
                                text_align=ft.TextAlign.CENTER,
                        )
                    )
                ),
            ],

            column_spacing=30,
            rows=[],  
        )

        self.scrollable_area = ft.Column(
            controls=[self.data_table],
            scroll=ft.ScrollMode.ALWAYS,
            expand=True
        )

        self.data_table_container = ft.Container(
            content=self.scrollable_area, 
            top=330, 
            left=10, 
            width=1500, 
            height=400
        )
            
        stack = ft.Stack(
            controls=[
                self.titulo_01,
                self.row_1_container, 
                self.boton_fecha_ing,
                self.boton_fecha_alta,
                self.row_2_container,
                self.row_3_container,
                self.titulo_11,
                self.titulo_12,
                self.titulo_13,
                self.titulo_02,
                self.data_table_container,
                self.boton_01,
                self.boton_02,
                self.boton_03,
                self.boton_04,
                self.boton_05,
                self.boton_06,
                self.boton_09, 
                self.boton_10,
                self.fondo,
                self.ruta_imagen,
                self.row_5_container,
                boton_cerrar_sesion
            ]
        )

        self.mostrar_datos()
        return stack

    def crear_gui_dos(self):
        """
        Genera la pantalla secundaria (Sesiones) con sus widgets. Allí se puede hacer el seguimiento de cada paciente a lo
        largo del tiempo; seleccionando una fila los datos generales, que están cargados en la pantalla principal, se 
        muestran también acá, en la parte inferior, para no tener que volver atrás en caso de necesitar esa información.
        En una ventana se muestran las imagenes de cada sesión o los gráficos, según se solicite.
        """ 

        self.page.clean()
        self.page.title = "Historial de Sesiones - Capsulitis Adhesiva"
        self.pantalla_completa = True
        self.calendarios()
        self.page.theme_mode =ft.ThemeMode.SYSTEM
        self.page.update()
        self.imagen_viewer = ft.Image(
            src=None,
            width=300,
            height=300,
            visible=False
        )

        self.imagen_container = ft.Container(
            content=self.imagen_viewer,
            left=660,
            top=200,
            width=850,
            height=500,
            border=ft.border.all(2, ft.Colors.RED), 
            border_radius=10,
            padding=10,
            bgcolor=ft.Colors.GREY_200  
        )

        self.titulo_01 = ft.Container(
            ft.Text(
                "HISTORIAL E INFORMACIÓN DE SESIONES DEL PACIENTE", 
                size=25, 
                color=ft.Colors.ORANGE_900,
                weight=ft.FontWeight.BOLD
            ), 
            top=0,
            left=20
        )

        self.selected_row_ref = ft.Ref[int]()  

        self.text_box_hc = ft.TextField(
            label=
            "Historia Clínica", 
            width=100, 
            color='black',
            border_color='white',
            bgcolor=ft.Colors.YELLOW_200
        )

        self.text_box_ap = ft.TextField(
            label=
            "Apellido", 
            width=150, 
            color='black',
            border_color='white',
            bgcolor=ft.Colors.YELLOW_200
        )

        self.text_elegir = ft.Dropdown(
            width=100, 
            color='black',
            border_color='black',
            filled=False,
            options=[
                ft.dropdown.Option(
                    "Num. de H.C."
                ),
                ft.dropdown.Option(
                    "Apellido"
                )
            ],
            value=
            ""
        )
        
        self.row_100 = ft.Row(
            controls=[
                self.text_elegir,
                self.text_box_hc,
                self.text_box_ap
            ],
            spacing=
            20
        )
        
        self.row_100_container = ft.Container(
            content=
            self.row_100,
            top=40,
            left=20
        )

        self.boton_07 = ft.FilledButton(
            content=ft.Icon(
                name=ft.Icons.TOUCH_APP, 
                color=ft.Colors.WHITE, 
                size=30
            ), 
            width=55, 
            height=55,
            style = ft.ButtonStyle(
                shape=
                ft.CircleBorder(), 
                bgcolor=ft.Colors.TEAL_200,
                color=ft.Colors.WHITE,           
                overlay_color=ft.Colors.BLACK,
                elevation=10,
                padding=5
            ),
            on_click=lambda e: self.consulta_sesiones()
        )

        self.titulo_04 = ft.Row(
            controls=[
                ft.Icon(
                    name=ft.Icons.ARROW_LEFT, 
                    color=ft.Colors.BLACK, 
                    size=30
                ),
                ft.Text(
                    "CLICK PARA FILTRAR POR NUM. DE H.C. ó POR APELLIDO", 
                    size=17, 
                    color=ft.Colors.BLACK, 
                    weight=ft.FontWeight.BOLD
                ),
            ],
            spacing=5, 
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        self.row_5 = ft.Row(
            controls=[
                self.boton_07, 
                self.titulo_04
            ],
            spacing=20
        )
        
        self.row_5_container = ft.Container(
            content=self.row_5,
            top=40,
            left=430,
            width=600
        )
        
        self.label_datos_paciente = ft.Text(
            "DATOS DEL PACIENTE CONSULTADO:", 
            size=20, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLACK
        )

        self.label_cont_1 = ft.Container(
            content=ft.Row(
                [self.label_datos_paciente]
            ), 
            top=695,
            left=10
        )

        self.label_hc = ft.Text(
            "Hist. Clínica", 
            size=15, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLACK
        )

        self.label_cont_2 = ft.Container(
            content=ft.Row(
                [self.label_hc]
            ), 
            top=720,
            left=10
        )

        self.text_hc = ft.TextField(
            label="", 
            read_only=True, 
            width=75, 
            height=45,
            bgcolor=ft.Colors.BLUE_100
        )
        
        self.label_nombre = ft.Text(
            "Nombre", 
            size=15, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLACK
        )

        self.label_cont_3 = ft.Container(
            content=ft.Row(
                [self.label_nombre]
            ), 
            top=720,
            left=114
        )

        self.text_nombre=ft.TextField(
            label="", 
            read_only=True, 
            width=120,
            height=45, 
            bgcolor=ft.Colors.BLUE_100
        )

        self.label_apellido=ft.Text(
            "Apellido", 
            size=15, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLACK
        )

        self.label_cont_4=ft.Container(
            content=ft.Row(
                [self.label_apellido]
            ), 
            top=720,
            left=260
        )

        self.text_apellido=ft.TextField(
            label="", 
            read_only=True, 
            width=120,
            height=45, 
            bgcolor=ft.Colors.BLUE_100
        )
        
        self.label_sexo=ft.Text(
            "Sexo", 
            size=15, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLACK
        )

        self.label_cont_5=ft.Container(
            content=ft.Row(
                [self.label_sexo]
            ), 
            top=720,
            left=405
        )

        self.text_sexo=ft.TextField(
            label="", 
            read_only=True, 
            width=100,
            height=45, 
            bgcolor=ft.Colors.BLUE_100
        )

        self.label_edad=ft.Text(
            "Edad", 
            size=15, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLACK
        )

        self.label_cont_6=ft.Container(
            content=ft.Row(
                [self.label_edad]
            ), 
            top=720,
            left=525
        )

        self.text_edad=ft.TextField(
            label="", 
            read_only=True, 
            width=50, 
            height=45,
            bgcolor=ft.Colors.BLUE_100
        )

        self.label_ms=ft.Text(
            "Hombro", 
            size=15, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLACK
        )

        self.label_cont_7=ft.Container(
            content=ft.Row(
                [self.label_ms]
            ), 
            top=720,
            left=595
        )

        self.text_ms_afec=ft.TextField(
            label="", 
            read_only=True, 
            width=125, 
            height=45,
            bgcolor=ft.Colors.BLUE_100
        )

        self.label_ingreso=ft.Text(
            "Fecha Ingreso", 
            size=15, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLACK
        )

        self.label_cont_8=ft.Container(
            content=ft.Row(
                [self.label_ingreso]
            ), 
            top=720,
            left=735
        )

        self.text_ingreso=ft.TextField(
            label="", 
            read_only=True, 
            width=120,
            height=45, 
            bgcolor=ft.Colors.BLUE_100
        )

        self.label_diabetes=ft.Text(
            "Diabetes", 
            size=15, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLACK
        )

        self.label_cont_9=ft.Container(
            content=ft.Row(
                [self.label_diabetes]
            ), 
            top=720,
            left=865
        )

        self.text_diabetes=ft.TextField(
            label="", 
            read_only=True, 
            width=60, 
            height=45,
            bgcolor=ft.Colors.BLUE_100
        )

        self.label_hip=ft.Text(
            "Hipotir.", 
            size=15, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLACK
        )

        self.label_cont_10=ft.Container(
            content=ft.Row(
                [self.label_hip]
            ), 
            top=720,
            left=945
        )

        self.text_hipot=ft.TextField(
            label="", 
            read_only=True, 
            width=60, 
            height=45,
            bgcolor=ft.Colors.BLUE_100
        )

        self.label_climaterio=ft.Text(
            "Climat.", 
            size=15, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLACK
        )

        self.label_cont_11=ft.Container(
            content=ft.Row(
                [self.label_climaterio]
            ), 
            top=720,
            left=1025
        )

        self.text_climaterio=ft.TextField(
            label="", 
            read_only=True, 
            width=60, 
            height=45,
            bgcolor=ft.Colors.BLUE_100
        )

        self.label_queloide=ft.Text(
            "Queloide", 
            size=15, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLACK
        )

        self.label_cont_12=ft.Container(
            content=ft.Row(
                [self.label_queloide]
            ), 
            top=720,
            left=1100
        ) 
        
        self.text_queloide=ft.TextField(
            label="", 
            read_only=True, 
            width=60, 
            height=45,
            bgcolor=ft.Colors.BLUE_100
        )

        self.label_depre=ft.Text(
            "Antidepr.", 
            size=15, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLACK
        )

        self.label_cont_13=ft.Container(
            content=ft.Row(
                [self.label_depre]
            ), 
            top=720,
            left=1185
        )

        self.text_depre=ft.TextField(
            label="", 
            read_only=True, 
            width=60, 
            height=45,
            bgcolor=ft.Colors.BLUE_100
        )

        self.label_conflictos=ft.Text(
            "Confl.", 
            size=15, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLACK
        )

        self.label_cont_14=ft.Container(
            content=ft.Row(
                [self.label_conflictos]
            ), 
            top=720,
            left=1265
        )

        self.text_conflictos=ft.TextField(
            label="", 
            read_only=True, 
            width=60, 
            height=45,
            bgcolor=ft.Colors.BLUE_100
        )

        self.label_ansiedad=ft.Text(
            "Tr. Ansied.", 
            size=15, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLACK
        )

        self.label_cont_15=ft.Container(
            content=ft.Row(
                [self.label_ansiedad]
            ), 
            top=720,
            left=1335
        )

        self.text_ansiedad=ft.TextField(
            label="", 
            read_only=True, 
            width=60, 
            height=45,
            bgcolor=ft.Colors.BLUE_100
        )

        self.label_fumador=ft.Text(
            "Fumador", 
            size=15, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLACK
        )

        self.label_cont_16=ft.Container(
            content=ft.Row(
                [self.label_fumador]
            ), 
            top=720,
            left=1420
        )

        self.text_fumador=ft.TextField(
            label="", 
            read_only=True, 
            width=60, 
            height=45,
            bgcolor=ft.Colors.BLUE_100
        )
        
        self.row_datos_paciente_01=ft.Row(
            controls=[
                self.text_hc, 
                self.text_nombre, 
                self.text_apellido
            ], 
            spacing=25
        )

        self.row_datos_paciente_02=ft.Row(
            controls=[
                self.text_sexo, 
                self.text_edad, 
                self.text_ms_afec, 
                self.text_ingreso
            ], 
            spacing=20
        )

        self.row_datos_paciente_03=ft.Row(
            controls=[
                self.text_diabetes, 
                self.text_hipot, 
                self.text_climaterio,
                self.text_queloide
            ], 
            spacing=20
        )

        self.row_datos_paciente_04=ft.Row(
            controls=[
                self.text_depre, 
                self.text_conflictos, 
                self.text_ansiedad, 
                self.text_fumador
            ], 
            spacing=20
        )

        self.row_datos_paciente_container_01=ft.Container(
            content=ft.Column(
                [self.row_datos_paciente_01]
            ), 
            top=740, 
            left=10
        )

        self.row_datos_paciente_container_02=ft.Container(
            content=ft.Column(
                [self.row_datos_paciente_02]
            ),
            top=740, 
            left=400
        )

        self.row_datos_paciente_container_03=ft.Container(
            content=ft.Column(
                [self.row_datos_paciente_03]
            ), 
            top=740, 
            left=865
        )

        self.row_datos_paciente_container_04=ft.Container(
            content=ft.Column(
                [self.row_datos_paciente_04]
            ),
            top=740, 
            left=1185
        )
        
        self.avisos=ft.Text(
            " ", 
            color=ft.Colors.WHITE, 
            weight=ft.FontWeight.NORMAL,
            style=ft.TextStyle(
                size=25
            )
        )

        self.row_4=ft.Row(controls=[self.avisos])

        self.fondo=ft.Stack(
            controls=[
                ft.Card(
                    content=ft.Container(
                        content=self.row_4,
                        width=820, 
                        height=70,
                        bgcolor=ft.Colors.WHITE60,
                        border_radius=8,
                        padding=10
                    ), 
                    elevation=10,
                    top=100, 
                    left=450
                )
            ], 
            width=1500, 
            height=1000
        )
   
        self.boton_01=Boton001("Ver Gráfico", lambda e: self.generar_grafico(e), top=105, left=20)
        self.boton_02=Boton001("Borrar", lambda e: self.borrar_sesion(), top=105, left=145)
        self.boton_03=Boton004("Ir a Pantalla Gráficos", lambda e: self.page.go("/graficos"), top=65, left=1250)
        self.boton_04=Boton001("SIN USO",lambda e: self.funcion_03(), top=145, left=145)
        self.boton_05=Boton001("Ver Todos", lambda e: self.mostrar_datos_dos(), top=105, left=270)
        self.boton_06=Boton001("Limpiar Pantalla", lambda e: self.limpiar_dos(), top=145, left=270)
        self.boton_08=Boton004("Volver a Principal", lambda e: self.page.go("/"), top=25, left=1250)
                      
        self.data_table_dos=ft.DataTable(
            bgcolor=ft.Colors.BLUE_GREY_100,
            border=ft.border.all(
                width=5, 
                color=ft.Colors.WHITE
            ),
            border_radius=10,
            vertical_lines=ft.Border(5,ft.Colors.WHITE),
            columns=[
            ft.DataColumn(
                label=ft.Container(
                    content=ft.Text(
                        "ID",
                        style=ft.TextStyle(
                            size=10,
                            weight=ft.FontWeight.BOLD, 
                            color=ft.Colors.BLACK
                        ), 
                        text_align=ft.TextAlign.CENTER
                    )
                )
            ),
            ft.DataColumn(
                label=ft.Container(
                    content=ft.Text(
                        "H.C",
                        style=ft.TextStyle(
                            size=10,
                            weight=ft.FontWeight.BOLD, 
                            color=ft.Colors.BLACK
                        ), 
                        text_align=ft.TextAlign.CENTER
                    )
                )
            ),
            ft.DataColumn(
                label=ft.Container(
                    content=ft.Text(
                        "Nombre",
                        style=ft.TextStyle(
                            size=10,
                            weight=ft.FontWeight.BOLD, 
                            color=ft.Colors.BLACK
                        ), 
                        text_align=ft.TextAlign.CENTER
                    )
                )
            ),
            ft.DataColumn(
                label=ft.Container(
                    content=ft.Text(
                        "Apellido",
                        style=ft.TextStyle(
                            size=10,
                            weight=ft.FontWeight.BOLD, 
                            color=ft.Colors.BLACK
                        ), 
                        text_align=ft.TextAlign.CENTER
                    )
                )
            ),
            ft.DataColumn(
                label=ft.Container(
                    content=ft.Text(
                        "Fecha",
                        style=ft.TextStyle(
                            size=10,
                            weight=ft.FontWeight.BOLD, 
                            color=ft.Colors.BLACK
                        ), 
                        text_align=ft.TextAlign.CENTER
                    )
                )
            ),
            ft.DataColumn(
                label=ft.Container(
                    content=ft.Text(
                        "Sesion Num.",
                        style=ft.TextStyle(
                            size=10,
                            weight=ft.FontWeight.BOLD, 
                            color=ft.Colors.BLACK
                        ), 
                        text_align=ft.TextAlign.CENTER
                    )
                )
            ),
            ft.DataColumn(
                label=ft.Container(
                    content=ft.Text(
                        "Funcion.",
                        style=ft.TextStyle(
                            size=10,
                            weight=ft.FontWeight.BOLD, 
                            color=ft.Colors.BLACK
                        ), 
                        text_align=ft.TextAlign.CENTER
                    )
                )
            ),
            ft.DataColumn(
                label=ft.Container(
                    content=ft.Text(
                        "Dolor",
                        style=ft.TextStyle(
                            size=10,
                            weight=ft.FontWeight.BOLD, 
                            color=ft.Colors.BLACK
                        ), 
                        text_align=ft.TextAlign.CENTER
                    )
                )
            ),
            ],
            column_spacing=30,
            rows=[],  
        )

        self.scrollable_area_dos=ft.Column(controls=[self.data_table_dos],scroll=ft.ScrollMode.ALWAYS,expand=True)
        self.data_table_dos_container=ft.Container(content=self.scrollable_area_dos,top=200,left=10,width=1500,height=500)

        try:
            datos_sesion = {
                "num_hc": self.form_vars["num_hc"].value,
                "nombre": self.form_vars["nombre"].value,
                "apellido": self.form_vars["apellido"].value,
                "fecha": self.form_vars["ingreso"].value,           
                "sesiones": self.form_vars["sesiones"].value,
                "funcionalidad": self.form_vars["funcionalidad"].value,
                "dolor": self.form_vars["dolor"].value,
                "imagen_path": self.form_vars["imagen_path"].value,
            }

            self.obj_db.insertar_en_sesiones(**datos_sesion)
        except Exception as e:
            print("Error al insertar en sesiones:", e)
            
        stack_dos=ft.Stack(
            controls=[
                self.titulo_01, 
                self.row_100_container, 
                self.data_table_dos_container,
                self.boton_01,
                self.boton_02,
                self.boton_03,
                self.boton_04,
                self.boton_05,
                self.boton_06, 
                self.fondo,
                self.boton_08, 
                self.row_5_container,
                self.row_datos_paciente_container_01,
                self.row_datos_paciente_container_02,
                self.row_datos_paciente_container_03,
                self.row_datos_paciente_container_04,
                self.label_cont_1,
                self.label_cont_2,
                self.label_cont_3,
                self.label_cont_4,
                self.label_cont_5,
                self.label_cont_6,
                self.label_cont_7,
                self.label_cont_8,
                self.label_cont_9,
                self.label_cont_10,
                self.label_cont_11,
                self.label_cont_12,
                self.label_cont_13,
                self.label_cont_14,
                self.label_cont_15,
                self.label_cont_16,
                self.imagen_container,
            ]
        )
        self.mostrar_datos_dos()
        return stack_dos

    def vista_grafico(self):  

        self.titulo = ft.Text("   Análisis de Pacientes", size=28, weight="bold", color="white")
        self.row_7 = ft.Row(
            controls=[
                self.titulo
            ]
        )

        self.row_7_container = ft.Container(
            content=ft.Column(
                [self.row_7]
            ), 
            top=20, 
            left=20,
            width=600,
            height=60,
            bgcolor="#19177C",
            border_radius=10
        )
        # --- Elementos de filtro ---
        self.sexo_dropdown = ft.Dropdown(
            label="Sexo",
            options=[ft.dropdown.Option("Masculino"), ft.dropdown.Option("Femenino")],
            width=170,
            border_color='white',
            bgcolor=ft.Colors.YELLOW_200
        )

        self.edad_text = ft.TextField(
            label="Edad mínima", 
            width=100,
            border_color='white',
            bgcolor=ft.Colors.YELLOW_200
        )

        self.row_8 = ft.Row(
            controls=[
                ft.Container(
                content=self.sexo_dropdown,
                bgcolor=ft.Colors.YELLOW_200, 
                padding=0, 
                border_radius=5
                ), 
                ft.Container(
                content=self.edad_text,
                bgcolor=ft.Colors.YELLOW_200, 
                padding=0, 
                border_radius=5
                )
            ], spacing=20)

        self.row_8_container = ft.Container(
            content=self.row_8, 
            top=100, 
            left=20
        )

        self.hombro_dropdown = ft.Dropdown(
            label="Hombro",
            options=[
                ft.dropdown.Option("Derecho D"),
                ft.dropdown.Option("Derecho ND"),
                ft.dropdown.Option("Izquierdo D"),
                ft.dropdown.Option("Izquierdo ND"),
            ],
            width=170
        )
        
        self.sesiones_text = ft.TextField(label="Sesiones mínimas", width=100)

        self.row_9 = ft.Row(
        controls=[
            ft.Container(
            content=self.hombro_dropdown,
            bgcolor=ft.Colors.YELLOW_200, 
            padding=0, 
            border_radius=5
            ), 
            ft.Container(
            content=self.sesiones_text,
            bgcolor=ft.Colors.YELLOW_200, 
            padding=0, 
            border_radius=5
            )
        ], 
        spacing=20
        )

        self.row_9_container = ft.Container(
            content=self.row_9, 
            top=160, 
            left=20
        )

        self.duracion_text = ft.TextField(label="Duración mínima (semanas)", width=100)

        self.row_10 = ft.Row(
            controls=[
            ft.Container(
            content=self.duracion_text,
            bgcolor=ft.Colors.YELLOW_200, 
            padding=0, 
            border_radius=5
            )
            ]
        )

        self.row_10_container = ft.Container(
            content=self.row_10,
            top=220,
            left=20
        )

        checks_labels = ["diabetes", "hipotir", "climaterio", "queloide", "depresion", "conflictos", "ansiedad", "fumador"]
        self.checkboxes = [ft.Checkbox(label=l.capitalize()) for l in checks_labels]
        self.checks_grid = ft.Column(self.checkboxes, wrap=True, spacing=5)
        self.checks_container = ft.Container(
            content=self.checks_grid,
            top=290,
            left=20,
            bgcolor=ft.Colors.YELLOW_200,
            width=120
        )

        self.boton_generar = Boton005("Generar gráfico", lambda e: self.generar_grafico_torta(e), top=600, left=25)
        self.boton_volver = Boton004("Volver a Principal", lambda e: self.page.go("/"),top=680, left=30)

        self.grafico_container = ft.Container(width=800, height=600, bgcolor="#F5F5F5",border_radius=10,top=100,left=400)

        stack_tres=ft.Stack(
            controls=[
                self.row_7_container,
                self.row_8_container,
                self.row_9_container,
                self.row_10_container,
                self.checks_container,
                self.grafico_container,
                self.boton_generar,
                self.boton_volver,
            ],
        )
        return stack_tres

    
    def generar_grafico_torta(self,e):
            
        filtros = {
            "sexo": self.sexo_dropdown.value,
            "edad_minima": self.edad_text.value,
            "hombro": self.hombro_dropdown.value,
            "sesiones_minimas": self.sesiones_text.value,
            "duracion_minima": self.duracion_text.value,
            "condiciones": [cb.label for cb in self.checkboxes if cb.value]  # Mantener capitalización
        }

        print("Filtros aplicados:", filtros)

        # Construir texto descriptivo
        filtros_aplicados = []
        if filtros["sexo"]: filtros_aplicados.append(f"Sexo: {filtros['sexo']}")
        if filtros["edad_minima"]: filtros_aplicados.append(f"Edad ≥ {filtros['edad_minima']}")
        if filtros["hombro"]: filtros_aplicados.append(f"Hombro: {filtros['hombro']}")
        if filtros["sesiones_minimas"]: filtros_aplicados.append(f"Sesiones ≥ {filtros['sesiones_minimas']}")
        if filtros["duracion_minima"]: filtros_aplicados.append(f"Duración ≥ {filtros['duracion_minima']} sem.")
        if filtros["condiciones"]: filtros_aplicados.append(f"Condiciones: {', '.join(filtros['condiciones'])}")

        texto_filtros = " + ".join(filtros_aplicados) if filtros_aplicados else "Sin filtros"

        consulta = Pacientes.select()

        if filtros["sexo"]:
            consulta = consulta.where(Pacientes.sexo == filtros["sexo"])
        if filtros["edad_minima"]:
            consulta = consulta.where(Pacientes.edad >= int(filtros["edad_minima"]))
        if filtros["hombro"]:
            consulta = consulta.where(Pacientes.ms_afec == filtros["hombro"])
        if filtros["sesiones_minimas"]:
            consulta = consulta.where(Pacientes.sesiones >= int(filtros["sesiones_minimas"]))

        for cond in filtros["condiciones"]:
            if hasattr(Pacientes, cond):
                consulta = consulta.where(getattr(Pacientes, cond) == True)

        filas = list(consulta)

        # Filtrar por duración mínima
        if filtros["duracion_minima"]:
            min_duracion = int(filtros["duracion_minima"])
            filtradas = []
            for f in filas:
                fecha_ing = datetime.strptime(f.ingreso, "%d-%m-%Y")
                fecha_alta = datetime.strptime(f.alta, "%d-%m-%Y")
                semanas = (fecha_alta - fecha_ing).days // 7
                if semanas >= min_duracion:
                    filtradas.append(f)
            filas = filtradas

        total = len(filas)

        if total == 0:
            self.page.snack_bar = ft.SnackBar(ft.Text("No se encontraron registros con esos filtros."))
            self.page.snack_bar.open = True
            self.page.update()
            return

        total_general = self.contar_total()
        porcentaje = (total / total_general) * 100

        # Datos para gráfico
        labels = ["Cumplen filtros", "No cumplen"]
        sizes = [total, total_general - total]
        colors = ["#19177C", "#9FA8DA"]

        # --- Gráfico con efecto luz/sombra ---
        fig, ax = plt.subplots(figsize=(6, 5))
        explode = (0.1, 0)
        pies = ax.pie(sizes, explode=explode, colors=colors, startangle=90)

        # Aplicar luz
        light_filter = LightFilter(9)
        for p in pies[0]:
            p.set_agg_filter(light_filter)
            p.set_rasterized(True)
            p.set(ec="none", lw=2)

        # Aplicar sombra
        shadow = FilteredArtistList(pies[0], DropShadowFilter(9, offsets=(3, -4), alpha=0.7))
        ax.add_artist(shadow)
        shadow.set_zorder(pies[0][0].get_zorder() - 0.1)

        # Título principal
        ax.set_title("Incidencia en el total de casos", fontsize=14)

        # Texto dinámico con filtros + porcentaje
        ax.text(0, -1.3, f"{texto_filtros}\n({porcentaje:.1f}%)", 
                ha='center', va='center', fontsize=10, wrap=True)

        # Guardar imagen en memoria
        buffer = BytesIO()
        plt.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        buffer.close()
        plt.close(fig)

        self.grafico_container.content = ft.Image(src_base64=img_base64, width=500, height=400, fit=ft.ImageFit.CONTAIN)
        self.grafico_container.update()



    def contar_total(self):
        return Pacientes.select().count()
        
    
        """ 
        Acá comienzan las  FUNCIONES DE LA VISTA 
        """

    def set_selected_row(self, index, table, ref):
        if table.page: 
            for i, row in enumerate(table.rows):
                row.selected = i == index
            ref.current = index
            table.update()

            self.mostrar_aviso(f"Fila {index + 1} seleccionada", ft.Colors.GREEN)

    def agrega_fecha_01(self,e):
        self.text_box_07.value = e.control.value.strftime("%d-%m-%Y") 

        self.page.update()  

    def agrega_fecha_02(self,e):
        self.text_box_08.value = e.control.value.strftime("%d-%m-%Y")
        
        self.page.update()  

    def on_file_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            ruta_origen = e.files[0].path
            nombre_archivo = os.path.basename(ruta_origen)
    
            carpeta_destino = self.CARPETA_IMAGENES
            os.makedirs(carpeta_destino, exist_ok=True)
            
            ruta_destino = os.path.join(carpeta_destino, nombre_archivo)
    
            shutil.copy2(ruta_origen, ruta_destino)
    
            self.ruta_imagen.value = ruta_destino
    
    def mostrar_aviso(self, mensaje:str, color=ft.Colors.RED, size=25):

            """
            Maneja el texto de los avisos de error, advertencia,etc.
            """
            self.avisos.value = mensaje
            self.avisos.color = color
            self.avisos.style = ft.TextStyle(size=size)

            self.page.update()
   
    async def agregar_fila(self,e):
        """
        Guarda los datos en la base. Utiliza el patrón observador para registrar 
        hora, fecha, num_hc y apellido de cada ingreso nuevo en un archivo .txt.
        """
        self.num_hc = str(self.form_vars["num_hc"].value).strip()
        self.apellido = str(self.form_vars["apellido"].value).strip()
        self.ingreso = str(self.form_vars["ingreso"].value).strip()
    
        if not self.regex_app.numero_hc_valido(self.num_hc):
            self.mostrar_aviso(
                'ERROR: H.C. debe ser un número de hasta 6 dígitos', 
                ft.Colors.RED
            )
            return

        datos_paciente = {}
        for campo, control in self.form_vars.items():
            valor = control.value
            if isinstance(control, ft.Checkbox):
                datos_paciente[campo] = True if valor else False
            elif campo in ["edad", "sesiones", "funcionalidad", "dolor"]:
                try:
                    datos_paciente[campo] = int(valor)
                except ValueError:
                    self.mostrar_aviso(f"ERROR: '{campo}' debe ser un número", ft.Colors.RED)
                    return
            else:
                datos_paciente[campo] = valor.strip() if isinstance(valor, str) else valor

        try:
            self.obj_db.insertar_paciente_si_no_existe(**datos_paciente)

            ruta_absoluta = self.form_vars["imagen_path"].value
            if ruta_absoluta:
                ruta_relativa = os.path.relpath(ruta_absoluta, os.getcwd())
            else:
                ruta_relativa = ""

            datos_sesion = {
                "num_hc": datos_paciente["num_hc"],
                "nombre": datos_paciente["nombre"],
                "apellido": datos_paciente["apellido"],
                "fecha": datos_paciente["ingreso"],  
                "sesiones": datos_paciente["sesiones"],
                "funcionalidad": datos_paciente["funcionalidad"],
                "dolor": datos_paciente["dolor"],
                "imagen_path": ruta_relativa
            }
            
            exito_sesion, mensaje_sesion = self.obj_db.insertar_en_sesiones(**datos_sesion)

            if not exito_sesion:
                self.mostrar_aviso(mensaje_sesion, ft.Colors.RED)
                self.notificar(datos_paciente["ingreso"], datos_paciente["num_hc"], datos_paciente["apellido"])
            else:
                self.mostrar_aviso(mensaje_sesion + "  Aguarde 3 seg.", ft.Colors.GREEN)

            await asyncio.sleep(1)

            self.mostrar_aviso(mensaje_sesion + "  Aguarde 2 seg.", ft.Colors.GREEN)

            await asyncio.sleep(1)

            self.mostrar_aviso(mensaje_sesion + "  Aguarde 1 seg.", ft.Colors.GREEN)

            await asyncio.sleep(1)

            self.mostrar_datos()
            self.limpiar_campos()
            self.mostrar_aviso('✅ Los datos se cargaron correctamente', ft.Colors.GREEN)
            if not exito_sesion:
                self.mostrar_aviso('No se insertó la sesión (datos incompletos)', ft.Colors.RED)
        except Exception as e:
            self.mostrar_aviso('❌Error en la inserción', ft.Colors.RED), e
            self.limpiar_campos()

        except Paciente_existe:
            self.mostrar_aviso('ERROR: el número de H.C. ya existe en la base de datos', ft.Colors.RED)
  
    def mostrar_datos(self): 
                    
        """
        Presenta en pantalla la tabla con todos los campos cargados en la hoja Pacientes de la base.
        """
        self.mostrar_aviso("Para modificar, click en el paciente + Botón 'Editar'", color=ft.Colors.GREEN)
        self.data_table.rows.clear()
        rows = self.obj_db.obtener_pacientes()
        
        for i, row in enumerate(rows):

            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(
                                "Sí" if isinstance(cell, bool) and cell else "No" if isinstance(cell, bool) else str(cell),
                                style=ft.TextStyle(size=11, color=ft.Colors.BLACK),
                                text_align=ft.TextAlign.CENTER
                            )
                        )for cell in row.values()
                    ],                      
                    on_select_changed=lambda e, index=i: self.set_selected_row(index, self.data_table, self.selected_row_ref)

                )        
            )
        self.page.update()

    def limpiar_campos(self):
        """
        Deja en blanco los campos del formulario sin afectar la tabla de datos.
        """
        for key, mi_widget in self.form_vars.items():
            if key == "imagen_path":
                mi_widget.value = ""
                continue

            if isinstance(mi_widget, ft.Checkbox):
                mi_widget.value = False
            elif isinstance(mi_widget, ft.TextField):
                mi_widget.value = ""
            elif isinstance(mi_widget, ft.Dropdown):
                if mi_widget.options:
                    mi_widget.value = mi_widget.options[0].key
            mi_widget.update()

        self.mostrar_aviso("")

    def limpiar(self):
        """
            Deja en blanco los campos y oculta la tabla de datos
            """
        self.data_table.rows.clear()
        self.page.update()
        self.mostrar_aviso("")
        self.limpiar_campos()
        self.page.update()

    def cargar_datos_para_modificar(self, data_table):
        """
        Carga los datos de la fila en los campos de la pantalla para su edición
        """
            
        if self.selected_row_ref.current is not None and self.selected_row_ref.current < len(self.data_table.rows):
            self.fila = data_table.rows[self.selected_row_ref.current]
            self.id_a_modificar = self.fila.cells[0].content.value       
                
            row = self.obj_db.obtener_datos_paciente_por_id(self.id_a_modificar)
            if row:
                campos = list(self.form_vars.keys()) 
                for i, campo in enumerate(campos):
                    if campo == "imagen_path":
                        continue
                    valor = getattr(row, campo)

                    if isinstance(self.form_vars[campo], ft.Checkbox):
                        self.form_vars[campo].value = bool(valor)
                    if isinstance(self.form_vars[campo], ft.TextField):
                        self.form_vars[campo].value = valor
                    if isinstance(self.form_vars[campo], ft.Dropdown):
                        self.form_vars[campo].value = valor
                    
                self.mostrar_aviso('EDITE Y HAGA CLICK EN BOTON "Actualizar"\nPARA GUARDAR LOS CAMBIOS', ft.Colors.GREEN, size=18)
                self.page.update()

    @indicador_modificacion
    def actualizar_datos(self):
        """
        Una vez editados los datos en los campos, actualiza el registro en la base de datos.
        También guarda los cambios, creando la fila con los nuevos valores en la tabla Sesiones.
        """
        item = self.selected_row_ref.current
        if item is None:
            return

        self.mi_id = int(self.data_table.rows[item].cells[0].content.value.strip())
        self.n_num_hc = str(self.form_vars["num_hc"].value).strip()

        if not self.regex_app.numero_hc_valido(self.n_num_hc):
            self.mostrar_aviso('ERROR: H.C. debe ser un número de hasta 6 dígitos', ft.Colors.RED)
            return

        valores_sql = {}

        for campo, widget in self.form_vars.items():
            if isinstance(widget, ft.Checkbox):
                valor = bool(widget.value)
            elif isinstance(widget, (ft.TextField, ft.Text, ft.Dropdown)):
                valor = widget.value.strip() if isinstance(widget.value, str) else widget.value
            else:
                valor = widget if isinstance(widget, str) else ""

            if campo in ["edad", "sesiones", "funcionalidad", "dolor"]:
                try:
                    valor = int(valor)
                except (ValueError, TypeError):
                    self.mostrar_aviso(f"ERROR: '{campo}' debe ser un número", ft.Colors.RED)
                    return

            valores_sql[campo] = valor

        valores_sql["num_hc"] = self.n_num_hc
        if "ingreso" in valores_sql:
            valores_sql.pop("ingreso")

        exito, mensaje = self.obj_db.actualizar_paciente_en_base(self.mi_id, valores_sql)

        if exito:
            ruta_absoluta = self.form_vars["imagen_path"].value
            if ruta_absoluta:
                ruta_relativa = os.path.relpath(ruta_absoluta, os.getcwd())
            else:
                ruta_relativa = ""

            datos_sesion = {
                "num_hc": valores_sql["num_hc"],
                "nombre": valores_sql["nombre"],
                "apellido": valores_sql["apellido"],
                "fecha": self.form_vars["ingreso"].value.strip(),  
                "sesiones": valores_sql["sesiones"],
                "funcionalidad": valores_sql["funcionalidad"],
                "dolor": valores_sql["dolor"],
                "imagen_path": ruta_relativa
            }

            self.obj_db.insertar_en_sesiones(**datos_sesion)

            self.data_table.rows.clear()
            self.mostrar_datos()
            self.limpiar_campos()
            self.mostrar_aviso('LOS DATOS HAN SIDO MODIFICADOS', ft.Colors.GREEN)
        else:
            self.mostrar_aviso('ERROR: Ese número de H.C. ya está asignado', ft.Colors.RED)

    @indicador_baja
    def borrar_fila(self): 
        """
        Borra la fila en la base de datos. Mediante un decorador se registra fecha, hora y datos de cada borrado.
        El decorador también usa una capa socket para conectarse a un servidor y enviarle esos mismos datos que se guardan
        en un archivo backup_datos_borrados.txt
        """
        if self.selected_row_ref.current is not None and self.selected_row_ref.current < len(self.data_table.rows):
            fila = self.data_table.rows[self.selected_row_ref.current]
            num_hc_a_borrar = fila.cells[0].content.value  
            self.obj_db.borrar_paciente(num_hc_a_borrar)
            self.selected_row_ref.current = None
            self.page.update()   
            self.mostrar_datos()
            self.mostrar_aviso(
                'Los datos fueron borrados del registro', 
                ft.Colors.GREEN
            )
                
        else:
            self.mostrar_aviso(
                'Debe seleccionar una fila para borrar', 
                ft.Colors.RED
            )

    def consulta(self):
            """
            Permite ingresar un número de H.C. o un apellido en los campos de entrada correspondientes
            y muestra en pantalla los datos, si existen en la base. Caso contrario, indica el error.
            """
            self.num_hc = self.text_box_01.value.strip()
            self.apellido = self.text_box_03.value.strip()
            hc = self.num_hc if Regex_01.numero_hc_valido(self.num_hc) else None


            if not self.num_hc and not self.apellido:
                self.mostrar_aviso(
                    "Por favor, ingrese un número de H.C. válido o un apellido.", 
                    ft.Colors.RED
                )
                return
                    
            try:
                hc = self.num_hc if Regex_01.numero_hc_valido(self.num_hc) else None
                rows = self.obj_db.consultar_paciente(hc, self.apellido)
                self.data_table.rows.clear()

                if not rows:
                    self.mostrar_aviso(
                        "ERROR: no se encontraron coincidencias en la base de datos", 
                        ft.Colors.RED
                    )
                    self.page.update()  
                    return

                def on_select(index):
                    self.selected_row_ref.current = index
                    self.cargar_datos_para_modificar(self,self.data_table)
                    self.mostrar_aviso(
                        'EDITE Y HAGA CLICK EN BOTON "Actualizar"', 
                        ft.Colors.GREEN
                    )

                for i, row in enumerate(rows):
                    self.data_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(
                                    ft.Text(
                                    "Sí" if getattr(row, campo) is True 
                                    else "No" if getattr(row, campo) is False 
                                    else str(getattr(row, campo)),
                                    color = ft.Colors.BLACK
                                    )
                                )
                                for campo in row.__data__.keys()
                            ],
                            on_select_changed=lambda e, index=i: self.set_selected_row(index, self.data_table, self.selected_row_ref)

                        )
                    )

                self.limpiar_campos()
                self.mostrar_aviso(
                    "Consulta solicitada en pantalla\nPara modificar datos, click en el paciente + Botón 'Editar'", 
                    ft.Colors.GREEN, 
                    size=18)
                
                self.page.update()

            except Exception as e:
                self.mostrar_aviso(
                    f"Error al consultar pacientes: {e}", 
                    ft.Colors.RED
                )

########## FUNCIONES DE LA SEGUNDA PANTALLA (SESIONES o gui_dos)  ###################################################
    def obtener_datos_sesiones(self, num_hc, apellido):
        '''
        Esta función retorna los datos necesarios para generar el gráfico.
        '''
        query = Sesiones.select()

        if num_hc:
            query = query.where(Sesiones.num_hc == num_hc)
        elif apellido:
            query = query.where(Sesiones.apellido.contains(apellido))

        query = query.order_by(Sesiones.fecha)

        sesiones = list(query)
        fechas = [s.fecha for s in sesiones]
        funcionalidades = [s.funcionalidad for s in sesiones]
        dolores = [s.dolor for s in sesiones]

        return fechas, funcionalidades, dolores

    def generar_grafico(self, e):
        """
        Crea un gráfico de barras para comparara la evolución de los valores de 
        dolor y funcionalidad a lo loargo de las sesiones.
        """
        self.num_hc = self.text_box_hc.value.strip()
        self.apellido = self.text_box_ap.value.strip()

        if not self.num_hc and not self.apellido:
            self.mostrar_aviso("Por favor, ingrese un número de H.C. o un apellido.", ft.Colors.RED)
            return

        fechas, funcionalidades, dolores = self.obtener_datos_sesiones(self.num_hc, self.apellido)

        if not fechas:
            self.mostrar_aviso("❌ No hay sesiones registradas para ese paciente", ft.Colors.RED)
            return

        self.mostrar_grafico(fechas, funcionalidades, dolores)

    def mostrar_grafico(self, fechas, funcionalidades, dolores):
        """
        Muestra el gráfico en la pantalla.
        """
        import numpy as np

        x = np.arange(len(fechas))  
        width = 0.4  

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(x - width/2, funcionalidades, width, label="Funcionalidad", color="tab:blue")
        ax.bar(x + width/2, dolores, width, label="Dolor", color="tab:red")

        ax.set_xlabel("Fecha")
        ax.set_ylabel("Valor")
        ax.set_title("Evolución del Paciente")
        ax.set_xticks(x)
        ax.set_xticklabels(fechas, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, axis="y", linestyle="--", alpha=0.5)

        fig.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        imagen_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        buffer.close()
        plt.close(fig)

        imagen = ft.Image(
            src_base64=imagen_base64,
            width=380,
            height=500,
            fit=ft.ImageFit.CONTAIN
        )

        self.imagen_container.content = imagen
        self.imagen_container.update()

    def funcion_02(): pass
    def funcion_03(): pass  #Los botones que las llaman existen pero todavía no tienen utilidad 

    def mostrar_datos_dos(self):
        """
        Muestra todas las filas cargadas en la tabla Sesiones.
        """
        self.limpiar_campos_dos()
        self.mostrar_aviso("Click en la fila para ver foto de sesión y datos del paciente", color=ft.Colors.GREEN)
        self.data_table_dos.rows.clear()
        rows = self.obj_db.obtener_sesiones()
        self.lista_sesiones_mostradas = rows
        for i, row in enumerate(rows):
            self.data_table_dos.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row.id))),
                        ft.DataCell(ft.Text(row.num_hc)),
                        ft.DataCell(ft.Text(row.nombre)),
                        ft.DataCell(ft.Text(row.apellido)),
                        ft.DataCell(ft.Text(row.fecha)),
                        ft.DataCell(ft.Text(str(row.sesiones))),
                        ft.DataCell(ft.Text(str(row.funcionalidad))),
                        ft.DataCell(ft.Text(str(row.dolor))),
                    ],
                    on_select_changed=lambda e, index=i: self.on_click_sesion(index)
            )
        )
        self.page.update()

    def borrar_sesion(self): 
        """
        Borra la sesión seleccionada en la base de datos y en la pantalla Sesiones.
        """
        if self.selected_row_ref_dos.current is not None and self.selected_row_ref_dos.current < len(self.data_table_dos.rows):
            fila = self.data_table_dos.rows[self.selected_row_ref_dos.current]
            sesion_a_borrar = fila.cells[0].content.value  
            self.obj_db.borrar_fila_sesion(sesion_a_borrar)
            self.selected_row_ref_dos.current = None
            self.page.update()  
            self.mostrar_datos_dos()
            self.mostrar_aviso(
                'La sesión fue borrada del registro', 
                ft.Colors.GREEN
            )
                
        else:
            self.mostrar_aviso(
                'Debe seleccionar una fila para borrar', 
                ft.Colors.RED
            )            
    
    def on_click_sesion(self, index: int):
        """
        Al hacer click en una fila se muestra la imagen correspondiente y en la parte inferior
        de la pantalla se cargan todos los datos del paciente seleccionado.
        """
        self.set_selected_row(index, self.data_table_dos, self.selected_row_ref_dos)

        self.mostrar_imagen_de_sesion(index, self.lista_sesiones_mostradas)
        
        sesion = self.lista_sesiones_mostradas[index]
        num_hc = sesion.num_hc
        apellido = sesion.apellido

        paciente = self.obj_db.obtener_datos_paciente_por_hc_apellido(num_hc,apellido)

        if paciente:
            self.text_hc.value = str(paciente.num_hc)
            self.text_nombre.value = paciente.nombre
            self.text_apellido.value = paciente.apellido
            self.text_sexo.value = paciente.sexo
            self.text_edad.value = str(paciente.edad)
            self.text_ms_afec.value = paciente.ms_afec
            self.text_ingreso.value = paciente.ingreso
            self.text_diabetes.value = "Sí" if paciente.diabetes else "No"
            self.text_hipot.value = "Sí" if paciente.hipotir else "No"
            self.text_climaterio.value = "Sí" if paciente.climaterio else "No"
            self.text_queloide.value = "Sí" if paciente.queloide else "No"
            self.text_depre.value = "Sí" if paciente.depresion else "No"
            self.text_conflictos.value = "Sí" if paciente.conflictos else "No"
            self.text_ansiedad.value = "Sí" if paciente.ansiedad else "No"
            self.text_fumador.value = "Sí" if paciente.fumador else "No"

            self.cargar_datos_gui_dos()
            self.mostrar_aviso(f"Paciente {paciente.nombre} {paciente.apellido}", ft.Colors.GREEN, size=18)
            self.page.update()
    
    def mostrar_imagen_de_sesion(self, index, lista_sesiones):
        try:
            sesion = lista_sesiones[index]
            ruta_relativa = sesion.imagen_path

            if ruta_relativa and os.path.exists(ruta_relativa):
                ruta_absoluta = os.path.join(os.getcwd(), ruta_relativa)
                self.imagen_viewer.src = ruta_absoluta
                self.imagen_viewer.visible = True
            else:
                self.imagen_viewer.visible = False
                self.imagen_viewer.src = ""

            self.imagen_viewer.update()

        except Exception as e:
            self.mostrar_aviso(f"Error al cargar imagen: {e}", ft.Colors.RED)
   
    def consulta_sesiones(self):
        self.imagen_viewer.src = ""
        self.imagen_viewer.visible = False
        self.imagen_container.content = self.imagen_viewer  
        self.imagen_container.update()


        self.num_hc = self.text_box_hc.value.strip()
        self.apellido = self.text_box_ap.value.strip()

        if not self.num_hc and not self.apellido:
            self.mostrar_aviso("Por favor, ingrese un número de H.C. o un apellido.", ft.Colors.RED)
            return

        try:
            if self.num_hc and not self.regex_app.numero_hc_valido(self.num_hc):
                raise ValueError("Número de H.C. inválido")

            rows = self.obj_db.obtener_historial_sesiones(
                hc_buscado=self.num_hc if self.num_hc else None,
                apellido_buscado=self.apellido if not self.num_hc else None
            )
            self.lista_sesiones_mostradas = rows 
            self.data_table_dos.rows.clear()

            if not rows:
                self.mostrar_aviso("No se encontraron sesiones para este paciente.", ft.Colors.RED)
                self.page.update()
                return

            for i, row in enumerate(rows):
                
                self.data_table_dos.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(row.id))),
                            ft.DataCell(ft.Text(row.num_hc)),
                            ft.DataCell(ft.Text(row.nombre)),
                            ft.DataCell(ft.Text(row.apellido)),
                            ft.DataCell(ft.Text(row.fecha)),
                            ft.DataCell(ft.Text(str(row.sesiones))),
                            ft.DataCell(ft.Text(str(row.funcionalidad))),
                            ft.DataCell(ft.Text(str(row.dolor))),
                        ],
                        on_select_changed=lambda e, index=i: self.on_click_sesion(index)
                    )
                )

            self.mostrar_aviso("Historial cargado correctamente", ft.Colors.GREEN, size=18)
            self.cargar_datos_gui_dos()
            self.page.update()
            

        except Exception as e:
            self.mostrar_aviso(f"Error al consultar sesiones: {e}", ft.Colors.RED)

    def cargar_datos_gui_dos(self):
        criterio = self.text_elegir.value  
        hc_buscado = self.text_box_hc.value.strip()
        apellido_buscado = self.text_box_ap.value.strip()

        if criterio == "Num. de H.C." and not hc_buscado:
            self.mostrar_aviso("Ingrese un número de H.C. válido.", ft.Colors.RED)
            return
        elif criterio == "Apellido" and not apellido_buscado:
            self.mostrar_aviso("Ingrese un apellido válido.", ft.Colors.RED)
            return

        row = self.obj_db.obtener_datos_paciente_por_hc_apellido(
            hc_buscado=hc_buscado if criterio == "Num. de H.C." else None,
            apellido_buscado=apellido_buscado if criterio == "Apellido" else None
        )

        if not row:
            self.mostrar_aviso("No se encontraron datos con ese criterio de búsqueda.", ft.Colors.RED)
            return

        self.text_hc.value = str(row.num_hc)
        self.text_nombre.value = row.nombre
        self.text_apellido.value = row.apellido
        self.text_sexo.value = row.sexo
        self.text_edad.value = str(row.edad)
        self.text_ms_afec.value = row.ms_afec
        self.text_ingreso.value = row.ingreso
        self.text_diabetes.value = "Sí" if row.diabetes else "No"
        self.text_hipot.value = "Sí" if row.hipotir else "No"
        self.text_climaterio.value = "Sí" if row.climaterio else "No"
        self.text_queloide.value = "Sí" if row.queloide else "No"
        self.text_depre.value = "Sí" if row.depresion else "No"
        self.text_conflictos.value = "Sí" if row.conflictos else "No"
        self.text_ansiedad.value = "Sí" if row.ansiedad else "No"
        self.text_fumador.value = "Sí" if row.fumador else "No"

        self.mostrar_aviso(f"Historial de sesiones del paciente {self.text_nombre.value} {self.text_apellido.value}", ft.Colors.GREEN, size=18)
        self.page.update()
    
    def limpiar_dos(self):
        self.data_table_dos.rows.clear()
        self.mostrar_aviso("")
        self.limpiar_campos_dos()

        self.imagen_viewer.visible = False
        self.imagen_viewer.src = None
        if self.imagen_viewer.page:  
            self.imagen_viewer.update()
        self.imagen_container.content = None 
        self.imagen_container.update()

        self.page.update()

    def limpiar_campos_dos(self):
        campos = [
            self. text_box_hc, 
            self. text_box_ap, 
            self.text_hc, 
            self.text_nombre, 
            self.text_apellido, 
            self.text_sexo, 
            self.text_edad,
            self.text_ms_afec, 
            self.text_ingreso, 
            self.text_diabetes, 
            self.text_hipot,
            self.text_climaterio, 
            self.text_queloide,
            self.text_depre, 
            self.text_conflictos, 
            self.text_ansiedad, 
            self.text_fumador,
            self.imagen_container
        ]
        for campo in campos:
            campo.value = ""
        self.page.update()