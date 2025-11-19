import flet as ft
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime
from cls_boton import Boton005

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
    def generar_grafico(e):
        filtros = {
            "sexo": sexo_dropdown.value,
            "edad_minima": edad_text.value,
            "hombro": hombro_dropdown.value,
            "sesiones_minimas": sesiones_text.value,
            "duracion_minima": duracion_text.value,
            "condiciones": [cb.label.lower() for cb in checkboxes if cb.value]
        }

        print("Filtros aplicados:", filtros)

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()

        query = "SELECT * FROM pacientes WHERE 1=1"
        params = []

        if filtros["sexo"]:
            query += " AND sexo = ?"
            params.append(filtros["sexo"])
        if filtros["edad_minima"]:
            query += " AND edad >= ?"
            params.append(int(filtros["edad_minima"]))
        if filtros["hombro"]:
            query += " AND ms_afec = ?"
            params.append(filtros["hombro"])
        if filtros["sesiones_minimas"]:
            query += " AND sesiones >= ?"
            params.append(int(filtros["sesiones_minimas"]))

        cur.execute(query, params)
        filas = cur.fetchall()

        if filtros["duracion_minima"]:
            min_duracion = int(filtros["duracion_minima"])
            filtradas = []
            for f in filas:
                fecha_ing = datetime.strptime(f[7], "%d-%m-%Y")
                fecha_alta = datetime.strptime(f[8], "%d-%m-%Y")
                semanas = (fecha_alta - fecha_ing).days // 7
                if semanas >= min_duracion:
                    filtradas.append(f)
            filas = filtradas

        for cond in filtros["condiciones"]:
            filas = [f for f in filas if f[checks_labels.index(cond)+9] == 1]

        total = len(filas)
        con.close()

        if total == 0:
            page.snack_bar = ft.SnackBar(ft.Text("No se encontraron registros con esos filtros."))
            page.snack_bar.open = True
            page.update()
            return

        labels = ["Cumplen filtros", "No cumplen"]
        sizes = [total, contar_total() - total]
        colors = ["#19177C", "#9FA8DA"]

        plt.figure(figsize=(5, 4))
        plt.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors)
        plt.title("Distribución según filtros")
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        buffer.close()
        plt.close()

        print(f"Longitud base64: {len(img_base64)}")

        # Reemplazamos el contenido del contenedor
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
