# -*- coding: utf-8 -*-
import os
import sys
import requests
import re
import random
import argparse
import textwrap
import zipfile
import time
from datetime import datetime, timezone, timedelta
from moviepy.editor import ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============================================
# CONFIGURACIÓN
# ============================================
CLAVE_PEXELS = os.getenv("PEXELS_API_KEY")

if not CLAVE_PEXELS:
    print("ERROR: Falta la clave de Pexels.")
    print("Asegúrate de configurar PEXELS_API_KEY como secreto en GitHub.")
    sys.exit(1)

# ============================================
# LISTA DE TEMAS PREDEFINIDOS (20)
# ============================================
TEMAS_PREDEFINIDOS = [
    "Motivacion",
    "Constancia",
    "Superacion",
    "Gratitud",
    "Logros",
    "AmorPropio",
    "Esperanza",
    "Confianza",
    "Resiliencia",
    "Felicidad",
    "Proposito",
    "Optimismo",
    "Paz",
    "Actitud",
    "Crecimiento",
    "Cambio",
    "Libertad",
    "Aprendizaje",
    "Sabiduria",
    "Conexion"
]

# ============================================
# FRASES PARA CADA TEMA (20 temas)
# ============================================
FRASES_POR_TEMA = {
    "Motivacion": [
        "La motivación te da energía para empezar cada día.",
        "Tu entusiasmo contagia a las personas que te rodean.",
        "La fe en ti mismo abre puertas que parecían cerradas.",
        "El coraje te ayuda a enfrentar los miedos más profundos.",
        "La determinación te lleva a alcanzar metas lejanas.",
        "La disciplina convierte los sueños en hábitos diarios.",
        "La resiliencia te enseña a levantarte después de cada caída.",
        "La voluntad te permite seguir adelante cuando todo se complica.",
        "El impulso inicial es el paso más importante de cualquier viaje.",
        "La constancia transforma los pequeños esfuerzos en grandes logros."
    ],
    "Constancia": [
        "La constancia construye el éxito día tras día.",
        "La perseverancia te acerca a tus metas aunque el camino sea largo.",
        "Los hábitos diarios moldean tu carácter y tu futuro.",
        "La paciencia te ayuda a esperar el momento adecuado.",
        "El esfuerzo constante vence cualquier obstáculo.",
        "La rutina bien llevada te da estabilidad y progreso.",
        "La disciplina te mantiene enfocado en lo que importa.",
        "La constancia te impide rendirte cuando las cosas se ponen difíciles.",
        "La resistencia te permite seguir avanzando sin desfallecer.",
        "La perseverancia es el secreto de todas las grandes historias."
    ],
    "Superacion": [
        "Superarse es salir de tu zona de confort y crecer.",
        "Los errores te enseñan lecciones que ningún libro puede dar.",
        "Cada desafío te vuelve más fuerte y más sabio.",
        "La transformación personal empieza cuando decides cambiar.",
        "El aprendizaje continuo te convierte en una mejor versión de ti mismo.",
        "La fortaleza te permite recuperarte de las caídas más duras.",
        "La renovación te da la oportunidad de empezar de nuevo cada mañana.",
        "Mejorar cada día te lleva a lugares que nunca imaginaste.",
        "El progreso constante es el camino hacia la excelencia.",
        "El avance, por pequeño que sea, siempre suma."
    ],
    "Gratitud": [
        "Agradecer te cambia la perspectiva y te llena de paz.",
        "Dar las gracias te conecta con lo mejor de la vida.",
        "Valorar lo que tienes te hace más feliz y más humano.",
        "Reconocer lo bueno te ayuda a vivir mejor.",
        "Decir gracias abre tu corazón a la alegría.",
        "La generosidad florece cuando practicas la gratitud a diario.",
        "Ser humilde te recuerda que todo lo bueno es un regalo.",
        "La satisfacción nace cuando valoras cada pequeño momento.",
        "La alegría se multiplica cuando compartes tu agradecimiento.",
        "La paz interior llega cuando aceptas con gratitud lo que la vida te da."
    ],
    "Logros": [
        "Tus logros reflejan todo el esfuerzo que has invertido.",
        "Cada victoria, por pequeña que sea, merece ser celebrada.",
        "Las metas alcanzadas te impulsan a seguir soñando más alto.",
        "El éxito es el resultado de la constancia y el trabajo duro.",
        "Los triunfos te enseñan que todo esfuerzo tiene su recompensa.",
        "El progreso te muestra que estás en el camino correcto.",
        "La realización personal llega cuando cumples tus objetivos.",
        "Las conquistas diarias construyen tu historia de éxito.",
        "Los avances, aunque lentos, siempre te acercan a tu destino.",
        "Cumplir tus metas te llena de satisfacción y orgullo."
    ],
    "AmorPropio": [
        "Amarte a ti mismo es el primer amor verdadero.",
        "Aceptarte es el primer paso hacia la felicidad plena.",
        "Cuidarte te da la fuerza para cuidar de los demás.",
        "Perdonarte te permite seguir adelante sin culpas.",
        "Confiar en ti mismo es el cimiento de todo logro.",
        "Respetarte a ti mismo es la base de todas las relaciones.",
        "La libertad interior nace cuando te aceptas sin condiciones.",
        "La paz llega cuando dejas de juzgarte y empiezas a quererte.",
        "Tu dignidad te recuerda que mereces todo lo bueno de la vida.",
        "Ser fiel a tus principios te mantiene en tu esencia."
    ],
    "Esperanza": [
        "La esperanza ilumina los días más oscuros y te da fuerzas.",
        "La ilusión te mantiene vivo y con ganas de seguir adelante.",
        "La fe en el futuro te ayuda a superar cualquier adversidad.",
        "El optimismo abre puertas que el miedo y la duda mantienen cerradas.",
        "La confianza en que todo mejorará te da tranquilidad.",
        "La certeza de que hay un mañana mejor te impulsa a seguir.",
        "La luz de la esperanza siempre encuentra una rendija por donde entrar.",
        "La promesa de nuevos comienzos te renueva el alma.",
        "La convicción te sostiene cuando todo parece perdido.",
        "La seguridad de que todo tiene solución te da paz y serenidad."
    ],
    "Confianza": [
        "Confiar en ti mismo es la clave para tomar decisiones acertadas.",
        "La seguridad personal te permite enfrentar cualquier reto sin miedo.",
        "Saber lo que vales te da tranquilidad en momentos difíciles.",
        "La convicción te ayuda a mantener el rumbo cuando dudas.",
        "La fe en tus habilidades te impulsa a lograr lo que te propones.",
        "La determinación te lleva a cumplir tus metas sin rendirte.",
        "La firmeza te da la fortaleza para decir no cuando es necesario.",
        "La estabilidad emocional nace de la confianza en ti mismo.",
        "La certeza de que puedes hacerlo te da el valor para intentarlo.",
        "El respaldo de tu propia conciencia te hace sentir seguro."
    ],
    "Resiliencia": [
        "La resiliencia te ayuda a levantarte cada vez que caes.",
        "La fortaleza interior te permite soportar las tormentas de la vida.",
        "La resistencia te enseña a seguir adelante sin importar las dificultades.",
        "La tenacidad te da la fuerza para no rendirte nunca.",
        "La entereza te permite mantener la calma en medio del caos.",
        "La firmeza de carácter te ayuda a superar cualquier obstáculo.",
        "La constancia te convierte en una persona más fuerte y sabia.",
        "La determinación te impulsa a buscar soluciones, no problemas.",
        "El temple te da la serenidad para enfrentar lo inesperado.",
        "La perseverancia es el arma más poderosa contra la adversidad."
    ],
    "Felicidad": [
        "La felicidad se encuentra en los pequeños detalles de cada día.",
        "La alegría nace cuando aprendes a vivir el presente sin preocupaciones.",
        "La plenitud llega cuando aceptas quién eres y lo que tienes.",
        "La satisfacción te envuelve cuando valoras lo que la vida te da.",
        "El bienestar se construye con hábitos saludables y pensamientos positivos.",
        "La calma interior te permite disfrutar de cada momento sin prisas.",
        "La paz te llena cuando dejas de lado las preocupaciones innecesarias.",
        "El gozo te acompaña cuando compartes tu felicidad con los demás.",
        "La dicha se multiplica cuando agradeces lo que tienes.",
        "El contento es el resultado de vivir en armonía con tus valores."
    ],
    "Proposito": [
        "El propósito le da sentido y dirección a tu vida.",
        "La misión personal te guía hacia lo que realmente importa.",
        "La vocación te conecta con tu talento y tu pasión más profunda.",
        "La meta clara te ayuda a enfocar tus esfuerzos y energías.",
        "El objetivo te mantiene en el camino cuando las distracciones aparecen.",
        "El destino se construye con cada decisión que tomas a diario.",
        "La razón de ser te da la fuerza para seguir cuando todo falla.",
        "El norte te indica hacia dónde debes dirigir tus pasos.",
        "El anhelo te impulsa a buscar algo más grande que tú mismo.",
        "La aspiración te eleva y te lleva a lugares que nunca imaginaste."
    ],
    "Optimismo": [
        "El optimismo te ayuda a ver el lado positivo de cada situación.",
        "La esperanza te da la certeza de que todo va a mejorar.",
        "La fe te sostiene en los momentos de incertidumbre y duda.",
        "La confianza en el futuro te permite avanzar sin miedo.",
        "La positividad atrae buenas energías y personas a tu vida.",
        "La alegría se convierte en un hábito cuando eliges ver lo bueno.",
        "La luz del optimismo disipa las sombras de la preocupación.",
        "El entusiasmo te impulsa a actuar con energía y pasión.",
        "La ilusión te mantiene joven y con ganas de vivir cada día.",
        "La certeza de que todo irá bien te da paz y tranquilidad."
    ],
    "Paz": [
        "La paz interior te permite vivir con serenidad y equilibrio.",
        "La calma te ayuda a tomar decisiones sin dejarte llevar por el estrés.",
        "La tranquilidad llega cuando aprendes a soltar lo que no puedes controlar.",
        "La armonía te conecta con tu esencia y con el mundo que te rodea.",
        "La tranquilidad te da la claridad mental para resolver cualquier problema.",
        "La quietud te permite escuchar tu voz interior y actuar con sabiduría.",
        "La serenidad te envuelve cuando aceptas la vida tal como es.",
        "El equilibrio emocional es la clave para una vida plena y feliz.",
        "La amabilidad te ayuda a responder con calma ante la adversidad.",
        "La compasión hacia ti mismo es el primer paso para la paz interior."
    ],
    "Actitud": [
        "La actitud determina cómo enfrentas los desafíos de la vida.",
        "La disposición positiva te abre puertas que el pesimismo cierra.",
        "La postura mental influye en todo lo que haces y sientes.",
        "La mentalidad correcta te ayuda a superar cualquier obstáculo.",
        "El enfoque en lo positivo te da la fuerza para seguir adelante.",
        "La perspectiva optimista cambia la manera en que ves el mundo.",
        "La visión clara te permite ver oportunidades donde otros ven problemas.",
        "La orientación adecuada te mantiene en el camino correcto.",
        "El rumbo lo marcas tú con cada decisión y cada pensamiento.",
        "La forma de enfrentar las cosas es lo que realmente marca la diferencia."
    ],
    "Crecimiento": [
        "El crecimiento personal te lleva a ser cada día una mejor versión de ti.",
        "La evolución te enseña que el cambio es parte del proceso.",
        "La maduración te da la sabiduría para tomar mejores decisiones.",
        "La expansión de tus horizontes te abre nuevas oportunidades.",
        "La mejora continua es el camino hacia la excelencia personal.",
        "El progreso, por pequeño que sea, siempre suma en tu vida.",
        "La superación te impulsa a ir más allá de tus propios límites.",
        "La transformación te renueva y te llena de energía positiva.",
        "La elevación personal te permite alcanzar metas que parecían inalcanzables.",
        "El fortalecimiento interior te da la resistencia para seguir adelante."
    ],
    "Cambio": [
        "El cambio te saca de la rutina y te abre a nuevas posibilidades.",
        "La transformación te permite evolucionar y adaptarte a las circunstancias.",
        "La adaptación te ayuda a fluir con los cambios de la vida.",
        "La renovación te da la oportunidad de empezar de nuevo cuando lo necesites.",
        "La reforma personal te permite mejorar áreas de tu vida que antes descuidabas.",
        "La innovación te lleva a encontrar soluciones creativas a los problemas.",
        "La variación te da frescura y dinamismo a tu día a día.",
        "La modificación de hábitos te conduce a resultados diferentes y mejores.",
        "La conversión te cambia por dentro y por fuera.",
        "La transición te enseña que cada final es también un nuevo comienzo."
    ],
    "Libertad": [
        "La libertad te da el poder de elegir tu propio camino.",
        "La independencia te permite tomar decisiones sin ataduras.",
        "La autonomía te hace dueño de tu vida y de tus actos.",
        "La liberación te quita el peso de las cargas innecesarias.",
        "La emancipación te permite ser tú mismo sin pedir permiso.",
        "La soltura te da la capacidad de fluir con la vida sin resistencias.",
        "La espontaneidad te conecta con tu esencia más auténtica.",
        "La flexibilidad te ayuda a adaptarte a cualquier situación sin perder tu esencia.",
        "La movilidad te permite moverte libremente en todas las direcciones.",
        "La desenvoltura te da la confianza para enfrentar cualquier reto."
    ],
    "Aprendizaje": [
        "El aprendizaje te abre la mente a nuevas ideas y perspectivas.",
        "La enseñanza te da la oportunidad de compartir lo que sabes con otros.",
        "La instrucción te guía en el camino del conocimiento y la sabiduría.",
        "La educación te prepara para enfrentar los desafíos de la vida.",
        "El conocimiento te da las herramientas para construir un futuro mejor.",
        "La sabiduría te enseña a aplicar lo que aprendes en tu día a día.",
        "La experiencia te demuestra que la práctica hace al maestro.",
        "La lección de cada error te convierte en una persona más sabia.",
        "La comprensión te permite ver más allá de las apariencias.",
        "La asimilación te integra el conocimiento en tu forma de ser."
    ],
    "Sabiduria": [
        "La sabiduría te ayuda a tomar decisiones acertadas en la vida.",
        "La prudencia te aconseja pensar antes de actuar.",
        "La sensatez te guía por el camino del equilibrio y la razón.",
        "La cordura te mantiene en paz contigo mismo y con los demás.",
        "La mesura te enseña a dosificar tus emociones y acciones.",
        "La discreción te permite guardar silencio cuando es necesario.",
        "La templanza te da el control necesario para no dejarte llevar.",
        "La moderación te ayuda a disfrutar sin excesos.",
        "La sagacidad te permite ver lo que otros no ven.",
        "La intuición te conecta con tu sabiduría interior."
    ],
    "Conexion": [
        "La conexión con los demás te hace sentir parte de algo más grande.",
        "El vínculo verdadero se construye con honestidad y respeto.",
        "El lazo emocional te une a las personas que realmente importan.",
        "La relación sana se basa en la comunicación y la confianza.",
        "La comunicación clara evita malentendidos y fortalece los lazos.",
        "El afecto sincero te da la calidez que necesitas para seguir.",
        "La empatía te permite ponerte en el lugar del otro y entenderlo.",
        "La solidaridad te une a los demás en los momentos difíciles.",
        "La unión hace que los problemas se vuelvan más llevaderos.",
        "La armonía en las relaciones te da paz y bienestar emocional."
    ]
}

# ============================================
# FRASES GENÉRICAS PARA TEMAS NO PRE DEFINIDOS
# ============================================
VERBOS_GENERICOS = [
    "cuidar", "escuchar", "valorar", "disfrutar", "confiar",
    "agradecer", "sonreír", "abrazar", "perdonar", "aprender",
    "compartir", "ayudar", "crecer", "soñar", "avanzar"
]
COMPLEMENTOS_GENERICOS = [
    "tu bienestar", "tu paz interior", "a los que quieres",
    "el momento presente", "tus logros", "tu camino",
    "las pequeñas cosas", "tus metas", "tu salud mental",
    "tu felicidad", "tu esfuerzo", "tu familia"
]

def frases_genericas_para_tema(tema):
    frases = []
    for _ in range(10):
        verbo = random.choice(VERBOS_GENERICOS)
        complemento = random.choice(COMPLEMENTOS_GENERICOS)
        femeninas = ("a", "ad", "ión", "umbre", "dad", "tad", "sis", "ez", "eza")
        if tema.lower().endswith(femeninas) and tema.lower() not in ["amor", "cambio", "crecimiento", "propósito", "optimismo", "entusiasmo", "aprendizaje", "conocimiento"]:
            articulo = "la"
        else:
            articulo = "el"
        if tema.lower() in ["amor", "cambio", "crecimiento", "propósito", "optimismo", "entusiasmo", "aprendizaje", "conocimiento"]:
            articulo = "el"
        plantilla = random.choice([
            f"{articulo.title()} {tema} te enseña a {verbo} {complemento}.",
            f"Cuando piensas en {articulo} {tema}, te das cuenta de que {verbo} {complemento}.",
            f"La clave de {articulo} {tema} está en {verbo} {complemento}.",
            f"Si quieres avanzar con {articulo} {tema}, tienes que {verbo} {complemento}.",
            f"No olvides que {verbo} {complemento} es parte de {articulo} {tema}.",
            f"Todos podemos {verbo} {complemento} si nos lo proponemos con {articulo} {tema}.",
            f"A veces, solo hace falta {verbo} {complemento} para entender {articulo} {tema}.",
            f"Recuerda que {verbo} {complemento} te acerca a {articulo} {tema}.",
            f"Piensa en lo que significa {verbo} {complemento} en {articulo} {tema} diario.",
            f"Lo bonito de {articulo} {tema} es que siempre puedes {verbo} {complemento}."
        ])
        frases.append(plantilla)
    return frases

def obtener_frases_para_tema(tema):
    if tema in FRASES_POR_TEMA:
        return FRASES_POR_TEMA[tema]
    else:
        return frases_genericas_para_tema(tema)

# ============================================
# GENERACIÓN DE PREGUNTA
# ============================================
def generar_pregunta(tema):
    preguntas = [
        f"¿Alguna vez has reflexionado sobre la importancia de {tema.lower()} en tu vida?",
        f"¿Qué significa para ti {tema.lower()} en tu día a día?",
        f"¿Cómo aplicas {tema.lower()} en las situaciones más difíciles?",
        f"¿Crees que {tema.lower()} puede cambiar tu forma de ver las cosas?",
        f"¿Cuál es tu mayor aprendizaje sobre {tema.lower()} hasta ahora?",
        f"¿Te has preguntado cómo {tema.lower()} influye en tus decisiones más importantes?",
        f"¿Qué harías si te faltara {tema.lower()} en tu vida?",
        f"¿Cuándo fue la última vez que practicaste {tema.lower()} de forma consciente?",
        f"¿Cómo te sientes cuando hablas o piensas en {tema.lower()}?",
        f"¿Qué consejo le darías a alguien sobre {tema.lower()} para empezar su camino?"
    ]
    return random.choice(preguntas)

# ============================================
# DIVISIÓN EN PÁRRAFOS
# ============================================
def dividir_en_parrafos(pregunta, frases, num_parrafos):
    parrafos = [pregunta]
    num_intermedios = num_parrafos - 2
    if num_intermedios < 1:
        num_intermedios = 1
    
    if len(frases) > num_intermedios:
        seleccionadas = random.sample(frases, num_intermedios)
    else:
        seleccionadas = frases.copy()
        while len(seleccionadas) < num_intermedios:
            seleccionadas.append("Sigue adelante con fe y determinación.")
    
    parrafos.extend(seleccionadas)
    parrafos.append("Déjame tu opinión abajo")
    
    while len(parrafos) < num_parrafos:
        parrafos.insert(-1, "Sigue adelante con fe y determinación.")
    while len(parrafos) > num_parrafos:
        parrafos.pop(-2)
    
    return parrafos

# ============================================
# GESTIÓN DE IMÁGENES LOCALES (descarga automática)
# ============================================
IMAGENES_DIR = "imagenes"
IMAGENES_POR_TEMA = 10  # Número de imágenes a descargar por tema

def asegurar_imagenes_locales():
    """Descarga imágenes para cada tema si no existen localmente."""
    os.makedirs(IMAGENES_DIR, exist_ok=True)
    print("📥 Verificando imágenes locales...")
    
    for tema in TEMAS_PREDEFINIDOS:
        tema_dir = os.path.join(IMAGENES_DIR, tema)
        os.makedirs(tema_dir, exist_ok=True)
        
        # Contar cuántas imágenes ya tenemos
        archivos = [f for f in os.listdir(tema_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if len(archivos) >= IMAGENES_POR_TEMA:
            continue
        
        # Si faltan, descargar
        print(f"   📥 Descargando imágenes para '{tema}'...")
        descargar_imagenes_para_tema(tema, IMAGENES_POR_TEMA - len(archivos))
        print(f"   ✅ Imágenes descargadas para '{tema}'.")

def descargar_imagenes_para_tema(tema, cantidad):
    """Descarga 'cantidad' imágenes de Pexels para el tema dado."""
    if cantidad <= 0:
        return
    
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": CLAVE_PEXELS}
    params = {
        "query": tema,
        "per_page": min(cantidad, 80),
        "orientation": "portrait",
        "page": random.randint(1, 5)
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            fotos = resp.json().get("photos", [])
            if not fotos:
                print(f"      ⚠️ No se encontraron imágenes para '{tema}'.")
                return
            # Descargar cada foto
            tema_dir = os.path.join(IMAGENES_DIR, tema)
            for i, foto in enumerate(fotos[:cantidad]):
                img_url = foto["src"]["large"]
                try:
                    img_data = requests.get(img_url, timeout=10).content
                    with open(os.path.join(tema_dir, f"img_{i+1:03d}.jpg"), "wb") as f:
                        f.write(img_data)
                except Exception as e:
                    print(f"      ⚠️ Error al descargar imagen {i+1}: {e}")
        else:
            print(f"      ⚠️ Error en Pexels: {resp.status_code}")
    except Exception as e:
        print(f"      ⚠️ Error al descargar imágenes para '{tema}': {e}")

def obtener_imagen_local(tema):
    """Devuelve la ruta de una imagen aleatoria local para el tema."""
    tema_dir = os.path.join(IMAGENES_DIR, tema)
    archivos = [f for f in os.listdir(tema_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not archivos:
        # Si no hay imágenes, intentar descargar una
        print(f"   ⚠️ No hay imágenes locales para '{tema}'. Descargando una...")
        descargar_imagenes_para_tema(tema, 1)
        archivos = [f for f in os.listdir(tema_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not archivos:
            # Fallback: imagen por defecto
            return None
    return os.path.join(tema_dir, random.choice(archivos))

# ============================================
# CREAR VÍDEO (con borde grueso, sombra, animación aleatoria y firma dorada)
# ============================================
def crear_video(tema, dia_semana, numero):
    num_parrafos = random.choice([6, 7, 8])
    duracion_total = random.uniform(70, 85)
    duracion_por_parrafo = duracion_total / num_parrafos
    duraciones = [duracion_por_parrafo] * num_parrafos

    print(f"   🎬 Video {numero} ({dia_semana} - {tema}) - {num_parrafos} párrafos, {duracion_total:.1f}s")
    print(f"   ⏱️  Cada párrafo: {duracion_por_parrafo:.1f}s")
    os.makedirs("videos", exist_ok=True)

    pregunta = generar_pregunta(tema)
    frases_tema = obtener_frases_para_tema(tema)
    frases_usar = random.sample(frases_tema, min(8, len(frases_tema)))
    while len(frases_usar) < 6:
        frases_usar.append("Sigue adelante con fe y determinación.")
    
    parrafos = dividir_en_parrafos(pregunta, frases_usar, num_parrafos)

    # Cargar imagen de fondo local para este video
    # Usaremos la misma imagen para todos los párrafos (para simplificar, ya que cada párrafo podría tener una distinta, pero por simplicidad usamos una por video)
    # Si quieres que cada párrafo tenga una imagen diferente, puedes llamar a obtener_imagen_local dentro del bucle.
    img_path = obtener_imagen_local(tema)
    if img_path is None:
        # Si no hay imagen, crear una gris
        img = Image.new("RGB", (1080, 1920), color=(50, 50, 50))
    else:
        try:
            img = Image.open(img_path).convert("RGB")
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
            img = img.resize((1080, 1920))
        except Exception as e:
            print(f"   ⚠️ Error al cargar imagen local: {e}. Usando fondo gris.")
            img = Image.new("RGB", (1080, 1920), color=(50, 50, 50))

    clips = []
    for i, parrafo in enumerate(parrafos):
        # Copiar la imagen base para cada párrafo
        img_copy = img.copy()
        draw = ImageDraw.Draw(img_copy)

        # Dividir el texto en líneas
        lineas = textwrap.wrap(parrafo, width=28, break_long_words=False)
        total_lineas = len(lineas)
        if total_lineas == 0:
            lineas = [" "]
            total_lineas = 1

        MARGEN_Y = 200
        font_size = int((1920 - 2 * MARGEN_Y) / (total_lineas * 1.4))
        font_size = max(30, min(font_size, 70))

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

        altura_bloque = total_lineas * (font_size * 1.3)
        y_inicio = 1920 - altura_bloque - 200

        # Dibujar texto con sombra y borde grueso
        y = y_inicio
        for linea in lineas:
            bbox = draw.textbbox((0, 0), linea, font=font)
            ancho_linea = bbox[2] - bbox[0]
            x = (1080 - ancho_linea) // 2

            # Sombra
            draw.text((x+3, y+3), linea, font=font, fill=(0, 0, 0, 150), stroke_width=0)
            # Texto principal blanco con borde grueso
            draw.text((x, y), linea, font=font, fill='white', stroke_width=7, stroke_fill='black')
            y += font_size * 1.3

        # Firma dorada
        firma = "@jonathan_irigoyen"
        try:
            font_firma = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
        except:
            try:
                font_firma = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 30)
            except:
                font_firma = ImageFont.load_default()
        
        bbox_firma = draw.textbbox((0, 0), firma, font=font_firma)
        ancho_firma = bbox_firma[2] - bbox_firma[0]
        alto_firma = bbox_firma[3] - bbox_firma[1]
        x_firma = 1080 - ancho_firma - 30
        y_firma = 1920 - alto_firma - 30

        draw.text((x_firma+3, y_firma+3), firma, font=font_firma, fill=(0, 0, 0, 150), stroke_width=0)
        draw.text((x_firma, y_firma), firma, font=font_firma, fill='#DAA520', stroke_width=4, stroke_fill='black')

        # Guardar el frame
        temp_path = f"temp_texto_{i}.jpg"
        img_copy.save(temp_path, "JPEG")
        
        # Crear clip con duración
        clip = ImageClip(temp_path, duration=duraciones[i])
        
        # Aplicar animación de entrada (solo fade in para evitar problemas)
        clip = clip.fadein(0.5).fadeout(0.2)
        clips.append(clip)

    # Concatenar clips
    video = concatenate_videoclips(clips, method="compose")

    # Guardar video
    tz_venezuela = timezone(timedelta(hours=-4))
    ahora = datetime.now(tz_venezuela)
    fecha_hora = ahora.strftime("%d-%m-%Y-%H-%M-%S")
    nombre = f"videos/{dia_semana}-{tema}-{fecha_hora}-video-{numero:03d}.mp4"
    video.write_videofile(nombre, fps=15, codec="libx264", audio=False)
    print(f"   ✅ Video guardado: {nombre}")

    # Limpiar archivos temporales
    for f in os.listdir("."):
        if f.startswith("temp_") and f.endswith(".jpg"):
            try:
                os.remove(f)
            except:
                pass

# ============================================
# SELECCIÓN DE TEMAS PARA LA SEMANA (CORREGIDA)
# ============================================
def seleccionar_temas(opcion):
    opcion_limpia = opcion.strip().lower()
    if any(palabra in opcion_limpia for palabra in ["todo", "aleatorio", "random", "azar"]):
        temas = random.sample(TEMAS_PREDEFINIDOS, 7)
        print(f"📌 Temas seleccionados (aleatorios): {', '.join(temas)}")
        return temas
    else:
        print(f"📌 Usando el tema: {opcion} (todos los días)")
        return [opcion] * 7

# ============================================
# EJECUCIÓN PRINCIPAL
# ============================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generador de videos para toda la semana")
    parser.add_argument("--videos", type=int, default=5, help="Número de videos por día (por defecto: 5)")
    parser.add_argument("--tema", type=str, default="Motivacion", help="Tema o 'todo' para aleatorio (por defecto: Motivacion)")
    parser.add_argument("--no-zip", action="store_true", help="No crear ZIP")
    args = parser.parse_args()

    # Asegurar imágenes locales antes de generar cualquier video
    asegurar_imagenes_locales()

    videos_por_dia = args.videos
    tema_input = args.tema

    print("🎬 ¡Generador de videos para toda la semana!")
    print("=" * 50)
    print(f"📝 Videos por día: {videos_por_dia} (por defecto: 5)")
    print(f"🎯 Temática: {tema_input} (escribe 'todo' para aleatorio)")
    print("=" * 50)

    temas_semana = seleccionar_temas(tema_input)

    DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    print(f"\n📝 Generando {videos_por_dia} videos por cada día de la semana")
    print(f"📊 Total: {videos_por_dia * 7} videos")
    print("=" * 50)

    for dia_idx, tema in enumerate(temas_semana):
        dia_nombre = DIAS_SEMANA[dia_idx]
        print(f"\n📅 Procesando: {dia_nombre} - {tema}")
        print(f"   📝 Generando {videos_por_dia} videos...")

        for i in range(videos_por_dia):
            crear_video(tema, dia_nombre, i+1)
            time.sleep(0.5)

    print("\n🎉 ¡Todos los videos generados!")

    if not args.no_zip:
        nombre_zip = "videos-generados.zip"
        print(f"📦 Creando ZIP: {nombre_zip} ...")
        with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk("videos"):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=file)
        print(f"✅ ZIP creado: {nombre_zip}")
        print(f"📁 Revisa la carpeta 'videos' y el archivo '{nombre_zip}'.")
    else:
        print("⏭️  No se creó ZIP (opción --no-zip activada).")
