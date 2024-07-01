import tkinter as tk
from tkinter import scrolledtext, Button, messagebox
import json
import re

# Función para cargar la base de datos de jugadores desde un archivo JSON
def cargar_base_datos():
    try:
        with open('jugadores.json', 'r') as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        messagebox.showerror("Error", "El archivo de base de datos 'jugadores.json' no se encuentra.")
        return {"jugadores": []}
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Error al leer la base de datos JSON.")
        return {"jugadores": []}

sinonimos = {
    "edad": ["edad", "años", "cuantos años tiene", "que edad tiene"],
    "altura": ["altura", "estatura", "que tan alto es", "cual es su altura","cuanto mide","mide"],
    "peso": ["peso", "cuanto pesa","pesa"],
    "clubes": ["clubes", "equipos", "club", "equipo", "en que equipos ha jugado", "en que clubes ha jugado","donde ha jugado"],
    "premios": ["premios", "galardones", "que premios ha ganado"],
    "goles": ["goles", "cuantos goles ha marcado", "cuantos goles tiene"]
}

# Función para buscar el jugador por nombre o apellido o ambos
# Función para buscar el jugador por nombre completo
def buscar_jugador(frase, base_datos):
    frase = frase.lower()
    jugadores_encontrados = []
    for jugador in base_datos['jugadores']:
        nombre = jugador['nombre'].lower()
        # Verificar si cada palabra del nombre del jugador está en la frase
        if all(palabra in frase for palabra in nombre.split()):
            jugadores_encontrados.append(jugador)
    return jugadores_encontrados



# Función para manejar el envío de mensajes
def enviar_mensaje(event=None):
    mensaje = entrada_mensaje.get()
    if mensaje.strip() == "":
        return

    chat_texto.config(state=tk.NORMAL)
    chat_texto.insert(tk.END, "Usuario: " + mensaje + "\n")

    if mensaje.lower() == "salir":
        ventana.quit()
        return

    respuesta = procesar_consulta(mensaje)
    if respuesta is not None:
        chat_texto.insert(tk.END, "\n" + "Bot: " + respuesta + "\n")
        if not respuesta.startswith("Bot: No entendí"):
            chat_texto.insert(tk.END, "Bot: ¿Deseas realizar otra consulta? Ingresa tu pregunta o escribe 'salir' para terminar.\n\n")
    else:
        chat_texto.insert(tk.END, "Bot: No entendí tu consulta. Por favor, intenta de nuevo.\n")

    chat_texto.config(state=tk.DISABLED)
    entrada_mensaje.delete(0, tk.END)


# Función para normalizar la consulta del usuario
def normalizar_consulta(consulta):
    consulta = consulta.lower()  # Convertir a minúsculas
    consulta = re.findall(r"[\w']+|[.,!?;]", consulta)  # Separar palabras y signos de puntuación
    return consulta

def normalizar_sinonimos(palabra):
    for clave, sinonimos_lista in sinonimos.items():
        if palabra in sinonimos_lista:
            return clave
    return palabra

def buscar_jugadores_por_club(nombre_club):
    nombre_club = nombre_club.lower()
    jugadores_en_club = [jugador['nombre'] for jugador in base_datos['jugadores'] if nombre_club in (club.lower() for club in jugador['clubes'])]
    if jugadores_en_club:
        return f"Jugadores que han estado en el {nombre_club.title()}: {', '.join(jugadores_en_club)}"
    else:
        return f"No se encontró ningún jugador que haya estado en {nombre_club.title()}."


def procesar_consulta_listas(mensaje):
    patrones_listas = {
        "goles": re.compile(r'.*lista.* (\d+) jugadores.* con más goles', re.IGNORECASE),
        "edad_jovenes": re.compile(r'.*lista.* (\d+) jugadores.* más jóvenes', re.IGNORECASE),
        "edad_viejos": re.compile(r'.*lista.* (\d+) jugadores.* más viejos', re.IGNORECASE),
        "club": re.compile(r'.*quienes han jugado en el (.+)', re.IGNORECASE)
    }

    for clave, patron in patrones_listas.items():
        match = patron.search(mensaje)
        if match:
            if clave == "goles":
                cantidad = int(match.group(1))
                return listar_jugadores_por_goles(cantidad, reverse=True)
            elif clave == "edad_jovenes":
                cantidad = int(match.group(1))
                return listar_jugadores_por_edad(cantidad, reverse=False)
            elif clave == "edad_viejos":
                cantidad = int(match.group(1))
                return listar_jugadores_por_edad(cantidad, reverse=True)
            elif clave == "club":
                nombre_club = match.group(1)
                return buscar_jugadores_por_club(nombre_club)

    return None


# Función para procesar la consulta del usuario
# Función para procesar la consulta del usuario
def procesar_consulta(mensaje):
    global jugador_seleccionado

    # Primero, ver si es una consulta de lista
    respuesta_listas = procesar_consulta_listas(mensaje)
    if respuesta_listas:
        return respuesta_listas

    # Normalizar y obtener todas las palabras de la consulta
    palabras = normalizar_consulta(mensaje)

    # Buscar jugadores mencionados en la consulta
    jugadores_mencionados = []
    for jugador in base_datos['jugadores']:
        nombre_completo = jugador['nombre'].lower()
        if nombre_completo in mensaje.lower():
            jugadores_mencionados.append(jugador)

    if len(jugadores_mencionados) == 0:
        return "No se encontró ningún jugador con esos nombres. Por favor, intenta de nuevo."
    elif len(jugadores_mencionados) == 1:
        jugador_seleccionado = jugadores_mencionados[0]
        # Identificar las acciones solicitadas
        acciones = set()
        for palabra in palabras:
            palabra_normalizada = normalizar_sinonimos(palabra)
            if palabra_normalizada in ["edad", "altura", "peso", "clubes", "premios", "goles"]:
                acciones.add(palabra_normalizada)

        if acciones:
            return obtener_info_jugador(jugador_seleccionado, acciones)
        else:
            return f"Se encontró a {jugador_seleccionado['nombre']}. ¿Qué deseas saber sobre él? (edad, altura, peso, clubes, premios, goles)"
    else:
        # Para cada jugador encontrado, buscar la información solicitada
        respuesta = ""
        for jugador in jugadores_mencionados:
            acciones = set()
            for palabra in palabras:
                palabra_normalizada = normalizar_sinonimos(palabra)
                if palabra_normalizada in ["edad", "altura", "peso", "clubes", "premios", "goles"]:
                    acciones.add(palabra_normalizada)
            if acciones:
                respuesta += f"Información sobre {jugador['nombre']}:\n"
                for accion in acciones:
                    respuesta += obtener_info_jugador(jugador, {accion}) + "\n"
            else:
                respuesta += f"Se encontró a {jugador['nombre']}. ¿Qué deseas saber sobre él? (edad, altura, peso, clubes, premios, goles)\n"

        return respuesta.strip()

    return "No se encontró ningún jugador con esos nombres. Por favor, intenta de nuevo."



def listar_jugadores_por_goles(cantidad, reverse=False):
    jugadores_ordenados = sorted(base_datos['jugadores'], key=lambda x: x['goles'], reverse=reverse)
    lista_jugadores = [f"{i+1}. {jugador['nombre']} ({jugador['goles']} goles)" for i, jugador in enumerate(jugadores_ordenados[:cantidad])]
    return f"Los {cantidad} jugadores con más goles son:\n" + "\n".join(lista_jugadores)

def listar_jugadores_por_edad(cantidad, reverse=False):
    jugadores_ordenados = sorted(base_datos['jugadores'], key=lambda x: x['edad'], reverse=reverse)
    lista_jugadores = [f"{i+1}. {jugador['nombre']} ({jugador['edad']} años)" for i, jugador in enumerate(jugadores_ordenados[:cantidad])]
    return f"Los {cantidad} jugadores más {'viejos' if reverse else 'jóvenes'} son:\n" + "\n".join(lista_jugadores)

# Función para obtener información específica del jugador
def obtener_info_jugador(jugador, acciones):
    info = []
    for accion in acciones:
        if accion == "edad":
            info.append(f"{jugador['nombre']} tiene {jugador['edad']} años.")
        elif accion == "altura":
            info.append(f"{jugador['nombre']} mide {jugador['altura']}.")
        elif accion == "peso":
            info.append(f"{jugador['nombre']} pesa {jugador['peso']} kg.")
        elif accion == "clubes":
            info.append(f"{jugador['nombre']} ha jugado en los siguientes clubes: {', '.join(jugador['clubes'])}.")
        elif accion == "premios":
            info.append(f"{jugador['nombre']} ha ganado los siguientes premios: {', '.join(jugador['premios'])}.")
        elif accion == "goles":
            info.append(f"{jugador['nombre']} ha marcado {jugador['goles']} goles.")
    return " ".join(info)



# Función para comparar si dos jugadores han jugado en el mismo club
def comparar_jugadores(palabras):
    if len(palabras) < 5 or palabras[1] != 'en' or palabras[3] != 'club':
        return "Formato de consulta incorrecto. Usa: 'jugó en el mismo club que [nombre del jugador]'"

    nombre_jugador_comparar = " ".join(palabras[4:])
    jugador_comparar = buscar_jugador(nombre_jugador_comparar, base_datos)

    if len(jugador_comparar) == 0:
        return f"No se encontró ningún jugador con el nombre '{nombre_jugador_comparar}'."
    jugador_comparar = jugador_comparar[0]

    clubes_comunes = set(jugador_seleccionado['clubes']).intersection(jugador_comparar['clubes'])

    if clubes_comunes:
        return f"Sí, {jugador_seleccionado['nombre']} y {jugador_comparar['nombre']} han jugado en el mismo club: {', '.join(clubes_comunes)}."
    else:
        return f"No, {jugador_seleccionado['nombre']} y {jugador_comparar['nombre']} no han jugado en el mismo club."

# Función para buscar jugadores por club
def buscar_jugadores_por_club(nombre_club):
    nombre_club = nombre_club.lower()
    jugadores_en_club = [jugador['nombre'] for jugador in base_datos['jugadores']
                        if nombre_club in [club.lower() for club in jugador['clubes']]]
    if jugadores_en_club:
        return f"Jugadores que han estado en el {nombre_club.title()}: {', '.join(jugadores_en_club)}"
    else:
        return f"No se encontró ningún jugador que haya estado en {nombre_club.title()}."

# Crear la ventana
ventana = tk.Tk()
ventana.title("Chat Interactivo de Futbolistas")
ventana.geometry("500x700")
ventana.configure(bg="#add8e6")

# Función para centrar la ventana en la pantalla
def centrar_ventana(ventana):
    ventana.update_idletasks()
    ancho_ventana = ventana.winfo_width()
    alto_ventana = ventana.winfo_height()
    x_pos = (ventana.winfo_screenwidth() // 2) - (ancho_ventana // 2)
    y_pos = (ventana.winfo_screenheight() // 2) - (alto_ventana // 2)
    ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{x_pos}+{y_pos}")

# Calcular y centrar la ventana en la pantalla
centrar_ventana(ventana)

# Crear un Label para el título de la ventana
titulo_label = tk.Label(ventana, text="Chat Interactivo de Futbolistas", fg='#4682B4', bg='#add8e6', font='Helvetica 14 bold', justify=tk.CENTER, wraplength=480)
titulo_label.pack(padx=10, pady=10)

# Crear área de texto para mostrar el chat
chat_texto = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, width=60, height=30)
chat_texto.config(state=tk.DISABLED)
chat_texto.pack(padx=10, pady=10)

# Crear entrada de texto para que el usuario escriba sus mensajes
entrada_mensaje = tk.Entry(ventana, width=60)
entrada_mensaje.pack(padx=10, pady=10)

# Función para salir
def salir_programa(event=None):
    ventana.destroy()

# Función para enviar mensaje (vinculada al botón y la tecla Enter)
def enviar_mensaje(event=None):
    mensaje = entrada_mensaje.get()
    if mensaje.strip() == "":
        return

    chat_texto.config(state=tk.NORMAL)
    chat_texto.insert(tk.END, "Usuario: " + mensaje + "\n")

    if mensaje.lower() == "salir":
        ventana.quit()
        return

    respuesta = procesar_consulta(mensaje)
    if respuesta is not None:
        chat_texto.insert(tk.END, "\n"+"Bot: " + respuesta + "\n")
        if not respuesta.startswith("Bot: No entendí"):
            chat_texto.insert(tk.END, "Bot: ¿Deseas realizar otra consulta? Ingresa tu pregunta o escribe 'salir' para terminar.\n\n")
    else:
        chat_texto.insert(tk.END, "Bot: No entendí tu consulta. Por favor, intenta de nuevo.\n")

    chat_texto.config(state=tk.DISABLED)
    entrada_mensaje.delete(0, tk.END)

# Crear botón para enviar mensaje
boton_enviar = Button(ventana, text="Enviar", command=enviar_mensaje)
boton_enviar.pack(padx=10, pady=10)

# Crear botón para salir
boton_salir = Button(ventana, text="Salir", command=salir_programa)
boton_salir.pack(padx=60, pady=10)

# Cargar la base de datos de jugadores
base_datos = cargar_base_datos()

# Variable global para almacenar el jugador seleccionado
jugador_seleccionado = None

# Mensaje inicial de bienvenida
mensaje_bienvenida = """
Bot: ¡Hola! Soy el Bot Interactivo de Futbolistas. Puedes preguntarme sobre jugadores de fútbol y te daré información detallada.
Escribe 'deseo ver una lista de los [N] jugadores con mas goles', 'deseo ver una lista de los [N] jugadores mas jovenes' o 'deseo ver una lista de los [N] jugadores mas viejos'.
También puedes buscar un jugador por su nombre y preguntar por detalles específicos como la edad, altura, peso, clubes, premios o goles.
Para salir en cualquier momento, escribe 'salir'.
¡Disfruta consultando!
""" + "\n"

# Función para mostrar el mensaje inicial de bienvenida
def mostrar_bienvenida():
    chat_texto.config(state=tk.NORMAL)
    chat_texto.insert(tk.END, mensaje_bienvenida)
    chat_texto.config(state=tk.DISABLED)

# Mostrar mensaje de bienvenida al inicio
mostrar_bienvenida()

# Función principal de ejecución de la interfaz gráfica
ventana.mainloop()

