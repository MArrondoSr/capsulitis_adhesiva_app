"""CONTROLADOR: crea una ventana para loguearse a la aplicación y pasar a la ventana principal (Pacientes).
Se asegura de que las ventanas de Flet estén funcionales antes de ser visibles, para evitar errores.
Un decorador en el botón de ingreso registra el usuario y la fecha de cada login en un archivo .txt"""

import flet as ft
from vista_14 import VistaDos
from modelo_14 import iniciar_bd, DataBase
from cls_boton import Boton002
from decoradores import indicador_login
from clases_try import *
import observador

class Controlador:
    """
    Esta es la clase principal
    """

    def __init__(self, root):
        self.root_controlador = root
        self.obj_db = VistaDos(self.root_controlador)
        self.el_observador = observador.ConcreteObserverA(self.obj_db.obj_db)

    def main(page: ft.Page):
        page.window.center()
        iniciar_bd()

        vista = VistaDos(page) 
        observador.ConcreteObserverA(vista.obj_db, vista)  

        obj_db_dos = DataBase(page)


        logueado = False

        def ingresar_al_sistema(e, usuario):
            nonlocal logueado
            logueado = True
            # vista.route_change("/")
            # vista.route_change("/paciente")
            # vista.route_change("/")  
            page.go("/")
            

        def login_view(page):
            page.title = "PANTALLA DE LOGIN"
            
            usuario_input = ft.TextField(
                label="Usuario", 
                width=250
            
            )
            password_input = ft.TextField(
                label="Contraseña", 
                password=True, 
                can_reveal_password=True, 
                width=250
            )

            mensaje = ft.Text(
                "", 
                color=ft.Colors.RED, 
                font_family="Arial", 
                size=18, 
                weight="bold"
            )

            def verificar_login(e):
                usuario = usuario_input.value.strip()
                password = password_input.value.strip()

                if obj_db_dos.validar_usuario(usuario, password):
                    funcion_logueo = indicador_login(usuario_input)(
                        lambda e: ingresar_al_sistema(e, usuario)
                    )
                    funcion_logueo(e)
                else:
                    mensaje.value = "❌ Usuario o contraseña incorrectos"
                    mensaje.color = ft.Colors.RED
                    mensaje.update()
                        
            def on_registrar_click(e):
                nuevo_usuario = nuevo_usuario_input.value.strip()
                new_password = new_password_input.value.strip()

                if not nuevo_usuario or not new_password:
                    nuevo_mensaje.value = "Complete todos los campos"
                    nuevo_mensaje.color = ft.Colors.RED
                    nuevo_mensaje.update()
                    return

                exito, mensaje_texto = obj_db_dos.registrar_usuario(nuevo_usuario, new_password)
                nuevo_mensaje.value = mensaje_texto
                nuevo_mensaje.color = ft.Colors.GREEN if exito else ft.Colors.RED
                nuevo_mensaje.update()
                
                if exito:
                    nuevo_usuario_input.value = ""
                    new_password_input.value = ""
                    nuevo_usuario_input.update()
                    new_password_input.update()
            
            boton_ingresar = Boton002(
                "INGRESAR", 
                lambda e: verificar_login(e), 
                top=250, 
                left=100,
                icono=ft.Icons.LOGIN
            )

            nuevo_usuario_input = ft.TextField(
                label="Nombre de Usuario", 
                width=250
            
            )
            new_password_input = ft.TextField(
                label="Contraseña", 
                password=True, 
                can_reveal_password=True, 
                width=250
            )

            nuevo_mensaje = ft.Text(
                "", 
                color=ft.Colors.GREEN, 
                font_family="Arial", 
                size=18, 
                weight="bold"
            )

            boton_registrar = Boton002(
                "REGISTRAR", 
                on_registrar_click, 
                top=560, 
                left=100,
                icono=ft.Icons.SAVE
            )

            return ft.View(
                route="/login",
                controls=[
                    ft.Stack(
                        controls=[
                            ft.Container(
                                content=ft.Text(
                                    "Bienvenido\nIngrese con su Usuario y Contraseña",
                                    color=ft.Colors.BLACK,
                                    font_family="Arial",
                                    size=30,
                                    weight="bold",
                                    text_align=ft.TextAlign.LEFT,
                                ),
                                top=100,
                                left=400
                            ),
                            ft.Container(
                                content=ft.Text(
                                    "¿Primer ingreso? Regístrese con un nombre de usuario y una contraseña",
                                    color=ft.Colors.BLACK,
                                    font_family="Arial",
                                    size=30,
                                    weight="bold",
                                    text_align=ft.TextAlign.LEFT,
                                ),
                                top=350,
                                left=100
                            ),
                            ft.Container(content=usuario_input, top=100, left=100, bgcolor="white"),
                            ft.Container(content=password_input, top=160, left=100, bgcolor="white"),
                            ft.Container(content=mensaje, top=220, left=100, ink_color="red"),
                            boton_ingresar,
                            ft.Container(content=nuevo_usuario_input, top=410, left=100, bgcolor="white"),
                            ft.Container(content=new_password_input, top=470, left=100, bgcolor="white"),
                            ft.Container(content=nuevo_mensaje, top=525, left=100, ink_color="red"),
                            boton_registrar,
                        ],
                        width=2000,
                        height=900,
                    )
                ]
            )

        def route_change(e):
            page.views.clear()

            # --- LOGIN ---
            if page.route == "/login":
                view = login_view(page)
                view.bgcolor = ft.Colors.YELLOW_200
                page.views.append(view)

            # --- SESIONES ---
            elif page.route == "/":
                if not logueado:
                    page.go("/login")
                    return
                stack = vista.crear_gui()
                view = ft.View(
                    route="/",
                    controls=[stack],
                    bgcolor=ft.Colors.BLUE_GREY
                )
                page.views.append(view)

                def despues_de_montar(_):
                    vista.mostrar_datos()
                    page.update()

                page.on_view_pop = despues_de_montar

            # --- PACIENTES ---
            elif page.route == "/paciente":
                if not logueado:
                    page.go("/login")
                    return
                stack = vista.crear_gui_dos()
                view = ft.View(
                    route="/paciente",
                    controls=[stack],
                    bgcolor=ft.Colors.ORANGE_200
                )
                page.views.append(view)

                def despues_de_montar_paciente(_):
                    vista.mostrar_datos_dos()
                    page.update()

                page.on_view_pop = despues_de_montar_paciente

            # --- GRÁFICOS ---
            elif page.route == "/graficos":
                if not logueado:
                    page.go("/login")
                    return
                stack = vista.vista_grafico()
                view = ft.View(
                    route="/graficos",
                    controls=[stack],
                    bgcolor=ft.Colors.BLUE_GREY
                )
                page.views.append(view)

            page.update()


        # Configurar la app
        page.route = "/login"
        page.on_route_change = route_change
        page.go("/login")



    ft.app(target=main)
