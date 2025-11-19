"""
Todos los botones que se usan en la interfaz gráfica son objetos de alguna de estas clases.

"""

import flet as ft

class Boton001(ft.Container):
    def __init__(self, texto, on_click_fn, top, left, width=120):
        super().__init__()
        self.button = ft.FilledButton(
            text = texto,
            style=ft.ButtonStyle(
                shape =ft.ContinuousRectangleBorder(radius=35),
                bgcolor=ft.Colors.TEAL_200,color=ft.Colors.WHITE,
                overlay_color=ft.Colors.BLACK,
                elevation=5,
                padding=5
            ),
            on_click=on_click_fn, 
            width=width
        )
        self.content = self.button
        self.top=top
        self.left=left


class Boton002(ft.Container):
    def __init__(self, texto, on_click_fn, top, left, icono=None, bgcolor=ft.Colors.BLUE):
        super().__init__()

        self.button = ft.CupertinoButton(
            content=ft.Row(
                controls=[
                    ft.Icon(icono, size=18) if icono else None,
                    ft.Text(texto, color=ft.Colors.BLACK, font_family="Arial", weight="bold")
                ],
                spacing=5
            ),
            bgcolor=bgcolor,
            border_radius=15,
            opacity_on_click=0.6,
            on_click=on_click_fn
        )

        self.content = ft.Container(
            content=self.button,
            padding=10,
            border=ft.border.all(2, ft.Colors.WHITE),
            shadow=ft.BoxShadow(
                blur_radius=8,
                color=ft.Colors.BLACK26,
                offset=ft.Offset(2, 2)
            ),
            border_radius=20
        )

        self.top = top
        self.left = left

class Boton003(ft.Container):
    def __init__(self, texto, on_click_fn, top, left, width=180):
        super().__init__()
        self.button = ft.FilledButton(
            text = texto,
            style=ft.ButtonStyle(
                shape =ft.ContinuousRectangleBorder(radius=35),
                bgcolor=ft.Colors.TEAL_200,color=ft.Colors.WHITE,
                overlay_color=ft.Colors.BLACK,
                elevation=5,
                padding=5
            ),
            on_click=on_click_fn, 
            width=width
        )
        self.content = self.button
        self.top=top
        self.left=left


class Boton004(ft.Container):
    def __init__(self, texto, on_click_fn, top, left, width=190):
        super().__init__()
        self.button = ft.FilledTonalButton(
            text = texto,
            icon=ft.Icons.ADD_TO_HOME_SCREEN,
            icon_color=ft.Colors.YELLOW,
            style=ft.ButtonStyle(
                shape =ft.ContinuousRectangleBorder(radius=15),
                bgcolor=ft.Colors.BLACK,color=ft.Colors.WHITE,
                overlay_color=ft.Colors.BLUE_400,
                elevation=25,
                padding=5,
            ),
            on_click=on_click_fn, 
            width=width
        )
        self.content = self.button
        self.top=top
        self.left=left
        

# class Boton005(ft.Container):
#     def __init__(self, texto, on_click_fn, top, left, width=200):
#         super().__init__()
#         self.button = ft.FilledButton(
#             text=texto,
#             style=ft.ButtonStyle(
#                 shape=ft.ContinuousRectangleBorder(radius=35),
#                 bgcolor=ft.Colors.TEAL_200,
#                 color=ft.Colors.WHITE,
#                 overlay_color=ft.Colors.BLACK,
#                 elevation=5,
#                 padding=5,
#             ),
#             width=width
#         )
#         self.content = self.button
#         self.top = top
#         self.left = left
#         self.on_click = on_click_fn  # FIX


class Boton005(ft.Container):
    def __init__(self, texto, on_click_fn, top, left, width=200):
        super().__init__()
        self.button = ft.FilledButton(
            text=texto,
            style=ft.ButtonStyle(
                shape=ft.ContinuousRectangleBorder(radius=35),
                bgcolor=ft.Colors.TEAL_200, color=ft.Colors.WHITE,
                overlay_color=ft.Colors.BLACK,
                elevation=5,
                padding=5,
            ),
            on_click=on_click_fn,  # PASAMOS DIRECTO
            width=width
        )
        self.content = self.button
        self.top = top
        self.left = left


   