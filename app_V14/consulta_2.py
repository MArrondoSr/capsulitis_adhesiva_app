import sqlite3

# Conexión y configuración
con = sqlite3.connect("db_casos_capsulitis.db")
con.row_factory = sqlite3.Row
cur = con.cursor()

# Obtener todos los pacientes
cur.execute("SELECT * FROM pacientes")
filas = cur.fetchall()

print(f"Cantidad de pacientes: {len(filas)}")

fumadores = 0
for fila in filas:
    if fila["fumador"] == 1:
        fumadores += 1

total = len(filas)
print(f"Fumadores: {fumadores}, Total: {total}")

porcentaje_fumadores = (fumadores / total) * 100
print(f"Porcentaje de fumadores: {porcentaje_fumadores:.2f}%")

import matplotlib.pyplot as plt

fumadores = 0
for fila in filas:
    if fila["fumador"] == 1:
        fumadores += 1

no_fumadores = total - fumadores

# Datos para el gráfico
labels = ["Fumadores", "No Fumadores"]
valores = [fumadores, no_fumadores]
colors = ["#ff9999","#66b3ff"]

plt.pie(valores, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
plt.title("Porcentaje de Fumadores")
plt.show()
