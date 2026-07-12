import os
import random
import re
import zipfile
from datetime import datetime

import requests
from moviepy.editor import (
    ColorClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
)
from PIL import Image

# ---------- CONFIGURACIÓN ----------
# Preguntar cantidad de videos
try:
    NUM_VIDEOS = int(os.environ.get("NUM_VIDEOS", ""))
except (TypeError, ValueError):
    while True:
        try:
            NUM_VIDEOS = int(input("¿Cuántos videos quieres generar? (1-50): "))
            if 1 <= NUM_VIDEOS <= 50:
                break
            print("Ingresa un número entre 1 y 50.")
        except ValueError:
            print("Debes escribir un número.")

# Preguntar temática
THEME = os.environ.get("THEME", "").strip()
if not THEME:
    THEME = input("Temática (escribe 'todo' para aleatorio, o un tema específico): ").strip()

# Preguntar nombre del ZIP
ZIP_NAME = os.environ.get("ZIP_NAME", "").strip()
if not ZIP_NAME:
    default_zip = f"Videos-{datetime.now().strftime('%Y%m%d')}.zip"
    ZIP_NAME = input(f"Nombre del archivo ZIP de salida (por defecto '{default_zip}'): ").strip()
    if not ZIP_NAME:
        ZIP_NAME = default_zip

# Lista de 20 temas
TEMAS = [
    "amistad", "familia", "tristeza", "alegría", "motivación",
    "amor", "superación", "viajes", "naturaleza", "música",
    "arte", "ciencia", "historia", "filosofía", "deportes",
    "salud", "comida", "moda", "tecnología", "espiritualidad"
]

if THEME.lower() == "todo":
    temas_elegidos = random.sample(TEMAS, 7)
else:
    temas_elegidos = [THEME] * 7

temas_elegidos = temas_elegidos[:NUM_VIDEOS]

# ---------- TEXTO ESCRITO POR MÍ (YO, EL ASISTENTE) ----------
# Aquí tienes frases para cada tema. El script las mezclará para formar párrafos.
TEXTOS = {
    "amistad": [
        "Un amigo es alguien que te conoce y te quiere tal como eres.",
        "La amistad verdadera no se mide por el tiempo, sino por la calidad.",
        "Un buen amigo está contigo en las buenas y en las malas.",
        "La risa compartida con un amigo es la mejor medicina.",
        "Los amigos son la familia que elegimos.",
        "Un amigo te levanta cuando caes y celebra tus victorias.",
        "La confianza es el pilar de toda gran amistad.",
        "Caminar con un amigo hace el viaje más ligero.",
        "Un abrazo de un amigo vale más que mil palabras.",
        "Los amigos hacen que los días grises sean soleados.",
        "La lealtad es el tesoro de una amistad duradera.",
        "Escuchar es el mayor regalo que le das a un amigo."
    ],
    "familia": [
        "La familia es el primer lugar al que pertenecemos.",
        "El amor de una familia es el refugio del alma.",
        "En la familia encontramos nuestro mayor apoyo.",
        "Los lazos de sangre son fuertes, pero los del corazón son eternos.",
        "Una familia unida es una fortaleza inquebrantable.",
        "Los recuerdos en familia son los más preciados.",
        "La familia te enseña a volar y siempre te espera con los brazos abiertos.",
        "Cada miembro de la familia es una pieza única en el rompecabezas.",
        "El respeto y el amor construyen una familia feliz.",
        "La familia es donde comienza la vida y el amor nunca termina.",
        "Compartir la mesa con la familia es compartir la vida.",
        "Los abrazos de familia curan cualquier herida."
    ],
    "tristeza": [
        "La tristeza es una nube que pasa, no el cielo entero.",
        "Está bien sentirse triste, es parte de ser humano.",
        "Las lágrimas riegan las semillas de la fortaleza.",
        "En la tristeza encontramos la oportunidad de crecer.",
        "Permítete sentir tristeza, pero no te quedes en ella.",
        "La tristeza nos enseña a valorar la alegría.",
        "Después de la tormenta siempre llega la calma.",
        "La tristeza es un maestro silencioso.",
        "No estás solo en tu tristeza, muchos te entienden.",
        "De las cenizas de la tristeza nace la esperanza.",
        "Aceptar la tristeza es el primer paso para superarla.",
        "Un día de tristeza es solo un día en una vida larga."
    ],
    "alegría": [
        "La alegría es la luz que ilumina el camino.",
        "Una sonrisa puede cambiar el día de alguien.",
        "La alegría se contagia cuando se comparte.",
        "Encuentra alegría en las pequeñas cosas.",
        "La alegría es la mejor actitud ante la vida.",
        "Reír es el sonido del alma feliz.",
        "La alegría no depende de lo que tienes, sino de cómo miras.",
        "Rodearte de alegría te hace más fuerte.",
        "La alegría es un imán para las cosas buenas.",
        "Cada día tiene un motivo para alegrarse.",
        "La alegría es el combustible del corazón.",
        "Baila, ríe y disfruta; la vida es corta."
    ],
    "motivación": [
        "El éxito comienza con la decisión de intentarlo.",
        "Cada pequeño paso te acerca a tu sueño.",
        "No mires atrás, solo avanza hacia adelante.",
        "Tú eres más fuerte de lo que crees.",
        "El fracaso es solo una lección para mejorar.",
        "La disciplina te lleva a donde la motivación no puede.",
        "Hoy es el mejor día para empezar.",
        "Cree en ti y todo será posible.",
        "Los grandes logros nacen de pequeños esfuerzos.",
        "Persiste hasta que lo imposible se vuelva posible.",
        "Tu actitud determina tu altitud.",
        "No esperes la oportunidad, créala tú mismo."
    ],
    "amor": [
        "El amor es la fuerza que mueve el mundo.",
        "Amar es dar sin esperar nada a cambio.",
        "El amor verdadero trasciende el tiempo y la distancia.",
        "El amor se demuestra con hechos, no con palabras.",
        "El amor propio es el primer paso para amar a otros.",
        "Cuando amas, todo se vuelve más hermoso.",
        "El amor es un viaje sin destino, solo el camino.",
        "Amar es aceptar al otro tal como es.",
        "El amor incondicional es el más puro.",
        "Dos almas que se aman crean su propio universo.",
        "El amor es la respuesta a todas las preguntas.",
        "Cada día es una nueva oportunidad para amar."
    ],
    "superación": [
        "Los obstáculos están para ser superados.",
        "Cada caída te enseña a levantarte más fuerte.",
        "La superación es el camino hacia la mejor versión de ti.",
        "No hay límites cuando tienes determinación.",
        "Aprende de tus errores y sigue adelante.",
        "El único fracaso es no intentarlo.",
        "La resiliencia construye el carácter.",
        "Siempre hay una luz al final del túnel.",
        "Superar miedos es el mayor logro.",
        "La paciencia y el esfuerzo todo lo pueden.",
        "Cada día es una batalla que puedes ganar.",
        "La superación personal es un viaje de por vida."
    ],
    "viajes": [
        "Viajar es la única inversión que te hace más rico.",
        "El mundo es un libro, y los viajes son sus páginas.",
        "Cada destino tiene una historia que contar.",
        "Viajar abre la mente y el corazón.",
        "Las mejores historias nacen en los viajes.",
        "Perderse en un lugar nuevo es la mejor manera de encontrarse.",
        "Cada viaje te cambia para siempre.",
        "La aventura está ahí fuera, solo hay que buscarla.",
        "Viajar es soñar con los ojos abiertos.",
        "Los recuerdos de viaje son el tesoro más valioso.",
        "Explorar lo desconocido te da perspectiva.",
        "El viaje es más importante que el destino."
    ],
    "naturaleza": [
        "La naturaleza es el mejor regalo de la vida.",
        "El canto de los pájaros es la música del alma.",
        "Cuidar la naturaleza es cuidarnos a nosotros mismos.",
        "El bosque te enseña que todo tiene su tiempo.",
        "El mar calma las tormentas del espíritu.",
        "Las montañas te recuerdan lo grande que es el mundo.",
        "La naturaleza nunca se equivoca.",
        "Un paseo al aire libre renueva el alma.",
        "La Tierra es nuestra casa, hay que protegerla.",
        "En la naturaleza encuentras paz y sabiduría.",
        "Los árboles son los guardianes del tiempo.",
        "El sol, la luna y el viento son nuestros compañeros eternos."
    ],
    "música": [
        "La música es el idioma del corazón.",
        "Una canción puede cambiar tu estado de ánimo.",
        "La música une a las personas sin importar su origen.",
        "Los acordes son la poesía del alma.",
        "La música te acompaña en los mejores y peores momentos.",
        "Cada nota tiene un sentimiento detrás.",
        "Tocar un instrumento es tocar el alma.",
        "La música es el refugio del espíritu.",
        "Las canciones son los latidos de la vida.",
        "Sin música, la vida sería un error.",
        "La música te transporta a otros mundos.",
        "Ritmo y melodía son la esencia de la felicidad."
    ],
    "arte": [
        "El arte es la expresión más pura del ser humano.",
        "Una pintura vale más que mil palabras.",
        "El arte refleja la belleza del mundo interior.",
        "Crear es el acto más liberador.",
        "Cada obra de arte tiene un alma propia.",
        "El arte nos conecta con lo más profundo.",
        "La creatividad no tiene límites.",
        "Un lienzo es un universo de posibilidades.",
        "El arte transforma la realidad.",
        "Los colores hablan sin hacer ruido.",
        "El arte es un puente entre culturas.",
        "Crear arte es crear vida."
    ],
    "ciencia": [
        "La ciencia es la búsqueda de la verdad.",
        "El conocimiento nos hace libres.",
        "Cada descubrimiento abre nuevas puertas.",
        "La curiosidad es el motor de la ciencia.",
        "La ciencia explica el universo y nuestra existencia.",
        "Los científicos son los exploradores del mundo moderno.",
        "La tecnología mejora nuestras vidas.",
        "La ciencia nunca deja de avanzar.",
        "Una pregunta lleva a una respuesta que genera más preguntas.",
        "La ciencia es la poesía de la realidad.",
        "Observar, preguntar y experimentar es el camino.",
        "La ciencia nos enseña a maravillarnos con lo simple."
    ],
    "historia": [
        "La historia es el espejo del presente.",
        "Aprender del pasado para construir el futuro.",
        "Los héroes del pasado inspiran nuestro hoy.",
        "Cada civilización deja su huella.",
        "La historia nos enseña lecciones inolvidables.",
        "Recordar es vivir de nuevo.",
        "El pasado es un maestro silencioso.",
        "Los grandes imperios surgen y caen, pero sus ideas perduran.",
        "La historia está llena de ejemplos de valentía.",
        "No conocemos el futuro sin conocer el pasado.",
        "El tiempo es el mejor narrador.",
        "Nuestra historia es el libro de nuestra identidad."
    ],
    "filosofía": [
        "Piensa, luego existes.",
        "La vida es el viaje de un alma en busca de sentido.",
        "La filosofía es el amor por la sabiduría.",
        "Cuestionar todo es el principio del conocimiento.",
        "La felicidad está en la virtud.",
        "El tiempo es un río que fluye sin cesar.",
        "La mente es el único límite real.",
        "La verdad se esconde en las preguntas.",
        "Vivir sin reflexionar es no haber vivido.",
        "La filosofía da alas al pensamiento.",
        "El ser humano es un ser en busca de significado.",
        "La razón es nuestra guía."
    ],
    "deportes": [
        "El deporte forja el carácter.",
        "Cada entrenamiento te acerca a la meta.",
        "La disciplina y el esfuerzo son la clave.",
        "El trabajo en equipo lleva al éxito.",
        "La derrota te enseña humildad.",
        "La victoria es el premio al sacrificio.",
        "El deporte une a las personas.",
        "Superar tus marcas es el mejor premio.",
        "El sudor es la recompensa del esfuerzo.",
        "Jugar con pasión es jugar con el corazón.",
        "Los deportes enseñan respeto y tolerancia.",
        "Cada partido es una nueva oportunidad."
    ],
    "salud": [
        "La salud es el mayor tesoro.",
        "Cuerpo sano, mente sana.",
        "Una buena alimentación es el primer medicamento.",
        "El ejercicio es vida.",
        "Dormir bien es esencial para el equilibrio.",
        "La salud mental es tan importante como la física.",
        "Pequeños hábitos crean grandes cambios.",
        "Escucha a tu cuerpo, él te habla.",
        "La prevención es la mejor cura.",
        "El agua es fuente de vida.",
        "La risa fortalece el sistema inmune.",
        "Cuidarse es quererse."
    ],
    "comida": [
        "La comida es el placer del paladar y el alma.",
        "Cocinar es un acto de amor.",
        "Los sabores nos transportan a otros tiempos.",
        "La mesa es el centro de la felicidad.",
        "Comer bien es vivir mejor.",
        "Cada cultura tiene sus delicias.",
        "La cocina une a las familias.",
        "Un buen plato es una obra de arte.",
        "Los ingredientes frescos son la base de todo.",
        "Compartir la comida es compartir la vida.",
        "Los sabores caseros son los más reconfortantes.",
        "La gastronomía es una experiencia completa."
    ],
    "moda": [
        "La moda es la expresión de la personalidad.",
        "Viste como te sientas bien.",
        "Los colores reflejan tu estado de ánimo.",
        "La moda es arte que se lleva puesto.",
        "La elegancia está en la sencillez.",
        "Cada prenda cuenta una historia.",
        "La moda cambia, pero el estilo permanece.",
        "La confianza es el mejor accesorio.",
        "La creatividad en la moda no tiene límites.",
        "La moda es una forma de comunicación.",
        "Lo importante no es la ropa, sino quién la lleva.",
        "La pasarela está en la calle."
    ],
    "tecnología": [
        "La tecnología nos conecta con el mundo.",
        "La innovación es la clave del futuro.",
        "La tecnología facilita nuestras vidas.",
        "El progreso tecnológico no se detiene.",
        "La inteligencia artificial abre nuevas fronteras.",
        "Los dispositivos son herramientas para crear.",
        "La tecnología une a las personas a distancia.",
        "El futuro está en la innovación.",
        "La tecnología es un reflejo de nuestra creatividad.",
        "Aprender tecnología es aprender a crear.",
        "Los avances mejoran la salud y la comunicación.",
        "La era digital es solo el comienzo."
    ],
    "espiritualidad": [
        "La espiritualidad es el viaje interior.",
        "La paz está dentro de ti.",
        "Conectar con el alma es la mayor riqueza.",
        "La meditación calma la mente.",
        "El agradecimiento abre el corazón.",
        "La espiritualidad no es religión, es conexión.",
        "Tu interior es un universo por explorar.",
        "La energía fluye cuando estás en paz.",
        "La fe mueve montañas.",
        "El silencio es la voz del alma.",
        "Vivir el presente es un acto espiritual.",
        "La luz interior ilumina tu camino."
    ]
}

# ---------- FUNCIONES ----------
def obtener_frases_para_tema(tema, cantidad):
    """Toma frases del tema y las mezcla, devuelve una lista."""
    frases = TEXTOS.get(tema, TEXTOS["motivación"])
    # Si no hay suficientes, repetir
    while len(frases) < cantidad:
        frases = frases + frases
    seleccionadas = random.sample(frases, cantidad)
    return seleccionadas

def construir_parrafos_locales(tema, num_parrafos):
    """
    Construye párrafos a partir de las frases.
    Cada párrafo tendrá entre 3 y 5 líneas.
    """
    # Calcular cuántas frases necesito en total
    # Cada párrafo tiene de 3 a 5 líneas, así que tomo un promedio de 4
    lineas_por_parrafo = random.randint(3, 5)
    total_frases_necesarias = num_parrafos * lineas_por_parrafo

    frases = obtener_frases_para_tema(tema, total_frases_necesarias)

    # Mezclar para que no siempre salgan en el mismo orden
    random.shuffle(frases)

    parrafos = []
    indice = 0
    for _ in range(num_parrafos):
        # Este párrafo tendrá entre 3 y 5 líneas
        lineas_este_parrafo = random.randint(3, 5)
        # Asegurar que no nos pasemos del total
        if indice + lineas_este_parrafo > len(frases):
            lineas_este_parrafo = len(frases) - indice
        if lineas_este_parrafo <= 0:
            break
        lineas = frases[indice:indice + lineas_este_parrafo]
        indice += lineas_este_parrafo
        parrafo_texto = " ".join(lineas)
        parrafos.append(parrafo_texto)

    # Si me faltan párrafos, relleno con frases de respaldo
    while len(parrafos) < num_parrafos:
        parrafos.append("Sigue adelante, cada día es una nueva oportunidad para brillar.")
    
    return parrafos

def descargar_imagen_pexels(tema, intentos=3):
    """Descarga una imagen desde Pexels usando la clave de API."""
    API_KEY = os.environ.get("PEXELS_API_KEY")
    if not API_KEY:
        raise ValueError("Falta la variable de entorno PEXELS_API_KEY. Configúrala en GitHub Secrets.")

    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": API_KEY}
    
    for _ in range(intentos):
        try:
            params = {
                "query": tema,
                "per_page": 15,
                "page": random.randint(1, 5)
            }
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            fotos = data.get("photos", [])
            if fotos:
                foto = random.choice(fotos)
                img_url = foto.get("src", {}).get("large", foto.get("src", {}).get("original"))
                if img_url:
                    img_data = requests.get(img_url, timeout=10).content
                    with open("temp_img.jpg", "wb") as f:
                        f.write(img_data)
                    # Verificar que se descargó bien
                    with Image.open("temp_img.jpg") as img:
                        if img.size[0] > 100 and img.size[1] > 100:
                            return True
        except Exception as e:
            print(f"Error con Pexels, reintentando... {e}")
            continue
    return False

def generar_video(tema, indice):
    print(f"Generando video {indice+1}: {tema}")

    # 1. Construir párrafos localmente (6 a 8 párrafos)
    num_parrafos = random.randint(6, 8)
    parrafos = construir_parrafos_locales(tema, num_parrafos)

    # 2. Unir todos los párrafos en una sola lista de líneas para el video
    #    MoviePy mostrará el texto continuo con saltos de línea
    lineas_totales = []
    for parrafo in parrafos:
        # Dividir cada párrafo en oraciones para mostrarlas como líneas
        # Simple: separar por puntos y seguir
        oraciones = re.split(r'(?<=[.!?])\s+', parrafo)
        for o in oraciones:
            if o.strip():
                lineas_totales.append(o.strip())
    
    # Si hay muy pocas líneas, añadir algunas genéricas
    while len(lineas_totales) < 15:
        lineas_totales.append("Disfruta cada instante de esta vida.")
    
    # 3. Descargar imagen de fondo desde Pexels
    fondo_ok = descargar_imagen_pexels(tema)
    if not fondo_ok:
        print("No se pudo descargar imagen de Pexels, usando fondo negro.")
        background = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=1)
    else:
        background = ImageClip("temp_img.jpg")

    # 4. Duración del video (70-85 segundos)
    segundos_por_linea = 2.5
    duracion = max(70, min(85, len(lineas_totales) * segundos_por_linea))
    background = background.set_duration(duracion)

    # 5. Rectángulo oscuro en la parte inferior (30% de la altura)
    rect_height = int(1920 * 0.30)
    rect_y = 1920 - rect_height
    dark_rect = ColorClip(size=(1080, rect_height), color=(0, 0, 0), duration=duracion)
    dark_rect = dark_rect.set_opacity(0.6)
    dark_rect = dark_rect.set_position(("center", rect_y))

    # 6. Texto
    texto_video = "\n".join(lineas_totales)
    txt_clip = TextClip(
        texto_video,
        fontsize=50,
        color='white',
        stroke_color='black',
        stroke_width=2,
        font='Arial',
        method='caption',
        size=(900, None),
        align='center'
    )
    txt_clip = txt_clip.set_duration(duracion)
    txt_clip = txt_clip.set_position(("center", rect_y + 50))

    # 7. Componer
    video = CompositeVideoClip([background, dark_rect, txt_clip])
    video = video.set_duration(duracion)

    # 8. Guardar
    filename = f"video_{indice+1}_{tema.replace(' ', '_')}.mp4"
    video.write_videofile(filename, fps=24, codec='libx264', audio_codec='aac', threads=4)
    print(f"Video guardado: {filename}")
    return filename

# ---------- EJECUCIÓN ----------
if __name__ == "__main__":
    print("Iniciando generación de videos con texto local e imágenes de Pexels...")
    archivos_generados = []
    for i, tema in enumerate(temas_elegidos):
        try:
            archivo = generar_video(tema, i)
            archivos_generados.append(archivo)
        except Exception as e:
            print(f"Error al generar video {i+1}: {e}")

    if archivos_generados:
        with zipfile.ZipFile(ZIP_NAME, 'w') as zipf:
            for arch in archivos_generados:
                zipf.write(arch)
                os.remove(arch)
        print(f"ZIP creado: {ZIP_NAME}")
    else:
        print("No se generó ningún video.")

    if os.path.exists("temp_img.jpg"):
        os.remove("temp_img.jpg")
