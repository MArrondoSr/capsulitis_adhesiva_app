# Registro y seguimiento del tratamiento de pacientes con Capsulitis Adhesiva

Aplicación desarrollada en **Python** con interfaz gráfica en **Flet** y arquitectura **MVC**, que permite registrar y seguir la evolución de pacientes con **Síndrome de Hombro Congelado / Capsulitis Adhesiva**.

La app funciona como una **Historia Clínica especializada**, registrando datos del paciente, antecedentes clínicos, evolución sesión por sesión (dolor y funcionalidad), imágenes del movimiento y estadísticas sobre grupos de pacientes.

---

## 🩺 Introducción y fundamentación clínica

El **Síndrome de Hombro Congelado** o **Capsulitis Adhesiva** es una patología caracterizada por dolor progresivo y limitación funcional del hombro. En muchos casos su origen es desconocido, por lo que resulta fundamental registrar y analizar los **antecedentes clínicos y condiciones previas** de cada paciente para identificar posibles factores asociados.

La experiencia clínica sugiere que ciertos antecedentes —como diabetes, hipotiroidismo, climaterio, cicatriz queloide, trastornos de ansiedad, depresión, conflictos laborales o familiares, o el hábito de fumar— pueden influir en el desarrollo, duración y severidad del cuadro. Sin embargo, demostrar estas asociaciones requiere **datos empíricos ordenados, comparables y analizables**.

Una correcta recolección y análisis de esta información permite:

- Detectar patrones repetidos en pacientes con evoluciones similares  
- Evaluar la eficacia del tratamiento kinesiólogico precoz e incruento  
- Anticipar el diagnóstico clínico incluso antes de la confirmación por imágenes  
- Evitar que el cuadro se agrave y, en muchos casos, **evitar una intervención quirúrgica**

---

## 🎯 Objetivo del proyecto

La aplicación pretende funcionar como una **Historia Clínica digital** para Capsulitis Adhesiva que permita:

- Registrar datos generales del paciente (nombre, edad, sexo, lado afectado, dominancia, etc.)  
- Guardar antecedentes clínicos relevantes (diabetes, hipotiroidismo, climaterio, etc.)  
- Hacer seguimiento sesión por sesión de **dolor** y **funcionalidad**  
- Asociar **imágenes** del movimiento en cada sesión  
- Generar **gráficos individuales** de evolución  
- Generar **gráficos estadísticos** sobre grupos de pacientes según distintos filtros  

En esta etapa el sistema permite ingresar, borrar, consultar y modificar datos del paciente, así como registrar la evolución del tratamiento y visualizar estadísticas simples.

---

## ✨ Funcionalidades principales

- **Gestión de pacientes**
  - Alta, baja, modificación y consulta
  - Datos de identificación y contacto
  - Lado del hombro afectado y dominancia

- **Registro clínico**
  - Antecedentes marcados como *True/False*:
    - Diabetes
    - Hipotiroidismo
    - Climaterio
    - Cicatriz queloide
    - Depresión / antidepresivos
    - Conflictos laborales / familiares
    - Trastornos de ansiedad
    - Fumador, etc.

- **Sesiones de tratamiento**
  - Registro por sesión de:
    - Fecha
    - Número de sesión
    - Escala de dolor
    - Escala de funcionalidad
  - Asociación de **imágenes** para documentar el rango de movimiento

- **Historial y gráficos individuales**
  - Historial de sesiones por paciente
  - Gráfico de barras de evolución de dolor y funcionalidad

- **Estadísticas de pacientes**
  - Filtros por:
    - Sexo
    - Rango etario
    - Hombro afectado
    - Duración mínima del tratamiento
    - Presencia/ausencia de determinados antecedentes
  - Gráficos con incidencia de distintos grupos sobre el total

- **Persistencia de datos**
  - Base de datos **SQLite** (`db_casos_capsulitis.db`) accesible vía **Peewee**
  - Archivos **TXT** para logs:
    - `lista_de_ingresos.txt`
    - `datos_borrados.txt`
    - `login.txt`
  - Si se eliminan los archivos de datos, la app los vuelve a crear al iniciar (en las condiciones previstas)

---

## 🧱 Arquitectura y tecnologías

- **Lenguaje:** Python 3.11  
- **Arquitectura:** MVC (Modelo – Vista – Controlador)  
- **UI:** [Flet](https://flet.dev/)  
- **Base de datos:** SQLite (`db_casos_capsulitis.db`)  
- **ORM:** Peewee  
- **Gráficos:** Matplotlib  
- **Documentación técnica:** Sphinx  

Archivos principales (en `app_14/`):

- `controlador_14.py` – coordina la lógica y la vista (punto de entrada recomendado)  
- `modelo_14.py` – acceso a datos y lógica de negocio  
- `vista_14.py` – construcción de la interfaz en Flet  
- Archivos auxiliares (`decoradores.py`, `observador.py`, `filtros_graf.py`, etc.) organizan responsabilidades específicas.

---

## 📂 Estructura del proyecto

```text
.
├── app_14/
│   ├── __pycache__/                # caché de Python (se ignora en git)
│   ├── assets/                     # recursos estáticos (iconos, etc.)
│   ├── imagenes_sesiones/          # imágenes de movimiento por sesión
│   ├── storage/                    # datos auxiliares usados por Flet
│   ├── controlador_14.py           # punto de entrada de la aplicación
│   ├── modelo_14.py
│   ├── vista_14.py
│   ├── db_casos_capsulitis.db      # base de datos SQLite
│   ├── lista_de_ingresos.txt
│   ├── datos_borrados.txt
│   ├── login.txt
│   ├── filtros_graf.py
│   ├── pantalla_grafico_2.py
│   ├── pantalla_grafico_3.py
│   ├── decoradores.py
│   ├── observador.py
│   ├── (otros .py auxiliares y de prueba)
│
├── Documentacion/                  # documentación generada con Sphinx
│   └── index.html
│   └── ... (resto de archivos HTML/CSS/JS)
│
├── pantallas/                      # capturas usadas en este README
│   ├── pantalla_1.png
│   ├── pantalla_2.png
│   ├── pantalla_3.png
│   └── pantalla_4.png
│
├── README.md
├── LICENSE
└── .gitignore

📄 License

Este proyecto está licenciado bajo Creative Commons Attribution – NonCommercial – ShareAlike 4.0 International (CC BY-NC-SA 4.0).
Podés usarlo, estudiarlo y modificarlo, siempre que:

menciones al autor original,

no lo utilices con fines comerciales,

y compartas cualquier obra derivada bajo la misma licencia.

Más información: https://creativecommons.org/licenses/by-nc-sa/4.0/
