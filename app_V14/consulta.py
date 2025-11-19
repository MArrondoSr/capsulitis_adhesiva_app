import sqlite3

con = sqlite3.connect("db_casos_capsulitis.db")

con.row_factory = sqlite3.Row  # Habilita acceso por nombre
cur = con.cursor()

cur.execute("SELECT * FROM pacientes WHERE id = 1")
fila = cur.fetchone()

campos_booleanos = ["diabetes", "hipotir", "climaterio", "queloide", "depresion", "conflictos", "ansiedad", "fumador"]

# Crear un diccionario limpio
diccionario = {}
for clave in fila.keys():
    valor = fila[clave]
    if clave in campos_booleanos:
        diccionario[clave] = "Sí" if valor == 1 else "No"
    else:
        diccionario[clave] = valor

# Mostrar el resultado
for clave, valor in diccionario.items():
    print(f"{clave}: {valor}")