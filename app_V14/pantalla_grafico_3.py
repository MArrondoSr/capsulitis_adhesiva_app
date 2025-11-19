import flet as ft
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from matplotlib.artist import Artist
from io import BytesIO
import base64
import numpy as np
from datetime import datetime
from cls_boton import Boton005
import plotly.graph_objects as go
import webbrowser
import os

DB_PATH = "db_casos_capsulitis.db"

def main(page: ft.Page):
    page.title = "Análisis de Pacientes"
    page.window_width = 950
    page.window_height = 800
    page.bgcolor = ft.Colors.BLUE_GREY
    

    # ----- ENCABEZADO -----
    header = (
        ft.Text("  Análisis Comparativos de Pacientes", size=28, weight="bold", color="white")
        
    )

    header_container = ft.Container(
                content=header,
                top=20,
                left=20,
                width=600,
                height=60,
                bgcolor="#19177C",
                border_radius=10
            )
    # ----- CAMPOS FILTRO -----
    sexo_dropdown = ft.Dropdown(
        label="Sexo",
        options=[ft.dropdown.Option("Masculino"), ft.dropdown.Option("Femenino")],
        width=170, 
        color='black',
        border_color='white',
        bgcolor=ft.Colors.YELLOW_200
    )

    edad_text = ft.TextField(
        label="Edad mínima", 
        width=100,
        color='black',
        border_color='white',
        bgcolor=ft.Colors.YELLOW_200)

    row_1 = ft.Row(
        controls=[
            ft.Container(
                content=sexo_dropdown,
                bgcolor=ft.Colors.YELLOW_200, 
                padding=0, 
                border_radius=5
            ), 
            ft.Container(
                content=edad_text,
                bgcolor=ft.Colors.YELLOW_200, 
                padding=0, 
                border_radius=5
            )
        ], spacing=20)

    row_1_container = ft.Container(
            content=row_1,
            top=100,
            left=20,
    )

    hombro_dropdown = ft.Dropdown(
        label="Hombro Afectado",
        options=[
            ft.dropdown.Option("Derecho D"),
            ft.dropdown.Option("Derecho ND"),
            ft.dropdown.Option("Izquierdo D"),
            ft.dropdown.Option("Izquierdo ND"),
        ],
        width=170,
    )

    sesiones_text = ft.TextField(label="Sesiones mínimas", width=100)

    row_2 = ft.Row(
        controls=[
            ft.Container(
            content=hombro_dropdown,
            bgcolor=ft.Colors.YELLOW_200, 
            padding=0, 
            border_radius=5
            ), 
            ft.Container(
            content=sesiones_text,
            bgcolor=ft.Colors.YELLOW_200, 
            padding=0, 
            border_radius=5
            )
        ], spacing=20)

    row_2_container = ft.Container(
            content=row_2,
            top=160,
            left=20
        )

    duracion_text = ft.TextField(label="Duración mínima (semanas)", width=100)
    row_3 = ft.Row(
        controls=[
            ft.Container(
            content=duracion_text,
            bgcolor=ft.Colors.YELLOW_200, 
            padding=0, 
            border_radius=5
            )
        ])
    
    row_3_container = ft.Container(
            content=row_3,
            top=220,
            left=20
        )


    checks_labels = [
        "diabetes", "hipotir", "climaterio", "queloide",
        "depresion", "conflictos", "ansiedad", "fumador"
    ]
    checkboxes = [ft.Checkbox(label=label.capitalize()) for label in checks_labels]
    checks_grid = ft.Column(checkboxes, wrap=True, spacing=5)
    checks_container = ft.Container(
            content=checks_grid,
            top=290,
            left=20,
            bgcolor=ft.Colors.YELLOW_200,
            width=120
        )
    # Contenedor para el gráfico
    grafico_container = ft.Container(width=800, height=600, bgcolor="#F5F5F5",top=100, left=400, border_radius=10)

    # ----- FUNCIONES -----
    # --- Filtros para efectos ---
    class BaseFilter:
        def get_pad(self, dpi): return 0
        def process_image(self, padded_src, dpi): raise NotImplementedError
        def __call__(self, im, dpi):
            pad = self.get_pad(dpi)
            padded_src = np.pad(im, [(pad, pad), (pad, pad), (0, 0)], "constant")
            tgt_image = self.process_image(padded_src, dpi)
            return tgt_image, -pad, -pad

    class GaussianFilter(BaseFilter):
        def __init__(self, sigma, alpha=0.5, color=(0, 0, 0)):
            self.sigma, self.alpha, self.color = sigma, alpha, color
        def get_pad(self, dpi): return int(self.sigma * 3 / 72 * dpi)
        def process_image(self, padded_src, dpi):
            tgt_image = np.empty_like(padded_src)
            tgt_image[:, :, :3] = self.color
            tgt_image[:, :, 3] = smooth2d(padded_src[:, :, 3] * self.alpha, self.sigma / 72 * dpi)
            return tgt_image

    class DropShadowFilter(BaseFilter):
        def __init__(self, sigma, alpha=0.3, color=(0, 0, 0), offsets=(0, 0)):
            self.gauss_filter = GaussianFilter(sigma, alpha, color)
            self.offsets = offsets
        def get_pad(self, dpi):
            return max(self.gauss_filter.get_pad(dpi), int(max(self.offsets) / 72 * dpi))
        def process_image(self, padded_src, dpi):
            t1 = self.gauss_filter.process_image(padded_src, dpi)
            a1 = np.roll(t1, int(self.offsets[0] / 72 * dpi), axis=1)
            a2 = np.roll(a1, -int(self.offsets[1] / 72 * dpi), axis=0)
            return a2
        
    class LightFilter(BaseFilter):
        """Apply LightSource filter"""

        def __init__(self, sigma, fraction=1):
            """
            Parameters
            ----------
            sigma : float
                sigma for gaussian filter
            fraction: number, default: 1
                Increases or decreases the contrast of the hillshade.
                See `matplotlib.colors.LightSource`

            """
            self.gauss_filter = GaussianFilter(sigma, alpha=1)
            self.light_source = LightSource()
            self.fraction = fraction

        def get_pad(self, dpi):
            return self.gauss_filter.get_pad(dpi)

        def process_image(self, padded_src, dpi):
            t1 = self.gauss_filter.process_image(padded_src, dpi)
            elevation = t1[:, :, 3]
            rgb = padded_src[:, :, :3]
            alpha = padded_src[:, :, 3:]
            rgb2 = self.light_source.shade_rgb(rgb, elevation,
                                            fraction=self.fraction,
                                            blend_mode="overlay")
            return np.concatenate([rgb2, alpha], -1)
    
    class FilteredArtistList(Artist):
        def __init__(self, artist_list, filter):
            super().__init__()
            self._artist_list, self._filter = artist_list, filter
        def draw(self, renderer):
            renderer.start_rasterizing()
            renderer.start_filter()
            for a in self._artist_list: a.draw(renderer)
            renderer.stop_filter(self._filter)
            renderer.stop_rasterizing()

    def smooth1d(x, window_len):
        s = np.r_[2 * x[0] - x[window_len:1:-1], x, 2 * x[-1] - x[-1:-window_len:-1]]
        w = np.hanning(window_len)
        y = np.convolve(w / w.sum(), s, mode='same')
        return y[window_len - 1:-window_len + 1]

    def smooth2d(A, sigma=3):
        window_len = max(int(sigma), 3) * 2 + 1
        A = np.apply_along_axis(smooth1d, 0, A, window_len)
        A = np.apply_along_axis(smooth1d, 1, A, window_len)
        return A

    def generar_grafico(e):
        filtros = {
            "sexo": sexo_dropdown.value,
            "edad_minima": edad_text.value,
            "hombro": hombro_dropdown.value,
            "sesiones_minimas": sesiones_text.value,
            "duracion_minima": duracion_text.value,
            "condiciones": [cb.label for cb in checkboxes if cb.value]  # Mantener capitalización
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

        # Consulta SQL
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        query = "SELECT * FROM pacientes WHERE 1=1"
        params = []

        if filtros["sexo"]:
            query += " AND sexo = ?"; params.append(filtros["sexo"])
        if filtros["edad_minima"]:
            query += " AND edad >= ?"; params.append(int(filtros["edad_minima"]))
        if filtros["hombro"]:
            query += " AND ms_afec = ?"; params.append(filtros["hombro"])
        if filtros["sesiones_minimas"]:
            query += " AND sesiones >= ?"; params.append(int(filtros["sesiones_minimas"]))

        cur.execute(query, params)
        filas = cur.fetchall()
        con.close()

        total = len(filas)
        if total == 0:
            page.snack_bar = ft.SnackBar(ft.Text("No se encontraron registros con esos filtros."))
            page.snack_bar.open = True
            page.update()
            return

        total_general = contar_total()
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

        grafico_container.content = ft.Image(src_base64=img_base64, width=500, height=400, fit=ft.ImageFit.CONTAIN)
        grafico_container.update()



    def contar_total():
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM pacientes")
        total = cur.fetchone()[0]
        con.close()
        return total

    # boton_generar = ft.ElevatedButton(
    #     "Generar gráfico", bgcolor="#19177C", color="white", width=200, on_click=generar_grafico)

    boton_generar = Boton005("Generar Gráfico", lambda e: generar_grafico(e), top=600, left=25)
    

    # boton_container = ft.Container(
    #         content=boton_generar,
    #         top=600,
    #         left=20
       # )

    stack = ft.Stack(
            controls=[
            header_container,
            row_1_container,
            row_2_container,
            row_3_container,
            #ft.Text("Condiciones", size=18, weight="bold"),
            checks_container,
            boton_generar,
            #boton_container,
            grafico_container
        ],
        # spacing=20,
        # horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    page.add(stack)

ft.app(target=main)
