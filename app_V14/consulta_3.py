import sqlite3

# Conexión y configuración
con = sqlite3.connect("db_casos_capsulitis.db")
con.row_factory = sqlite3.Row
cur = con.cursor()

def contar_condiciones(cur, condiciones=None):
    """
    condiciones: dict opcional con pares {columna: valor}
    Ejemplo: {"fumador": 1, "sexo": "M"}
    """
    query = "SELECT * FROM pacientes"
    params = []

    if condiciones:
        filtros = []
        for col, val in condiciones.items():
            filtros.append(f"{col} = ?")
            params.append(val)
        query += " WHERE " + " AND ".join(filtros)
        query += " AND edad >= ?"
        params.append(60)

    cur.execute(query, params)
    filas = cur.fetchall()
    return len(filas)

total = contar_condiciones(cur)  # todos los pacientes
fumadores = contar_condiciones(cur, {"fumador": 1})
hombres_fumadores = contar_condiciones(cur, {"fumador": 1, "sexo": "M"})
print(f"Total: {total}, Fumadores: {fumadores}, Hombres fumadores: {hombres_fumadores}")

def generar_grafico(etiqueta, valor, total):
    import matplotlib.pyplot as plt
    labels = [etiqueta, f"No {etiqueta}"]
    valores = [valor, total - valor]
    colors = ["#ff9999", "#66b3ff"]

    plt.pie(valores, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title(f"Distribución: {etiqueta}")
    plt.show()

