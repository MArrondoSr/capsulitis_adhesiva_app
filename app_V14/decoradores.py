from datetime import datetime
import socket

def indicador_login(usuario_input):
    '''
    Genera y escribe en un archivo .txt en cada ingreso a la aplicación, registrando fecha, hora y usuario.
    '''
    def decorador(funcion):
        def envoltura(e, *args, **kwargs):
            resultado = funcion(e,*args, **kwargs)
            try:
                usuario = usuario_input.value.strip()

                with open("login.txt", "a", encoding="utf-8") as archivo:
                    archivo.write(
                        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                        f"Se conectó el usuario {usuario or 'desconocido'}.\n")
            except Exception as e:
                print(f"[ERROR DECORADOR]: No se pudo identificar al usuario -> {e}")
            return resultado
        return envoltura
    return decorador


def indicador_baja(funcion):
    '''
    Cuando se borra un campo de la base de datos genera dos archivos .txt con los datos principales que se borraron, fecha y hora.
    Uno de los .txt se genera y actualiza en la máquina local, el otro, de backup, en el servidor con el que se conecta.
    '''
    def envoltura(self, *args, **kwargs):
        try:
            if self.selected_row_ref.current is not None:
                fila = self.data_table.rows[self.selected_row_ref.current]
                num_hc_borrado = fila.cells[1].content.value  
                nombre_borrado = fila.cells[2].content.value  
                apellido_borrado = fila.cells[3].content.value  

                mensaje = (
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                    f"Se borraron los datos del paciente {apellido_borrado}, {nombre_borrado}, con Num. H.C. {num_hc_borrado}."
                )

                with open("datos_borrados.txt", "a", encoding="utf-8") as archivo:
                    archivo.write(mensaje + "\n")

                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect(("192.168.0.247", 456))  # OJO ACA CON LA IP Y EL PUERTO, DEBEN SER LOS CORRECTOS
                        s.sendall(mensaje.encode("utf-8"))
                except Exception as err:
                    print(f"[ERROR ENVÍO AL SERVIDOR]: {err}")

        except Exception as e:
            print(f"[ERROR DECORADOR]: No se pudo borrar -> {e}")
        return funcion(self, *args, **kwargs)
    return envoltura

def indicador_modificacion(funcion):
    '''
    Imprime en consola el aviso de que se ha modificado una fila dela base de datos.
    '''
    def envoltura(*args):
        valor=funcion(*args)
        print("Se modificó una fila en la base de datos")
        return valor
    return envoltura