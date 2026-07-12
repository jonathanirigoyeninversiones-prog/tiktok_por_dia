# -*- coding: utf-8 -*-
import os
import sys
import json
import requests
import re
import time
import random
from datetime import datetime, timezone, timedelta
from moviepy.editor import ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import textwrap
import zipfile

CLAVE_PEXELS = os.getenv("PEXELS_API_KEY")

if not CLAVE_PEXELS:
    print("ERROR: Falta la clave de Pexels.")
    sys.exit(1)

# ============================================
# 📅 LISTA DE TEMAS PREDEFINIDOS (20)
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
    "PazInterior",
    "Actitud",
    "Crecimiento",
    "Cambio",
    "Libertad",
    "Aprendizaje",
    "Sabiduria",
    "Conexion"
]

# ============================================
# 🌍 GENERADOR UNIVERSAL (para cualquier tema)
# ============================================
FRASES_UNIVERSALES = [
    "A veces, lo más importante es aprender a {verbo} {complemento}.",
    "Cuando piensas en {tema}, te das cuenta de que {verbo} {complemento}.",
    "La clave está en {verbo} {complemento} con calma y sin prisas.",
    "Si quieres avanzar, tienes que {verbo} {complemento}.",
    "No olvides que {verbo} {complemento} es parte del camino.",
    "Todos podemos {verbo} {complemento} si nos lo proponemos.",
    "A veces, solo hace falta {verbo} {complemento} para sentirte mejor.",
    "Recuerda que {verbo} {complemento} te ayuda a crecer.",
    "Piensa en lo que significa {verbo} {complemento} en tu día a día.",
    "Lo bonito de la vida es que siempre puedes {verbo} {complemento}."
]

VERBOS_UNIVERSALES = [
    "cuidar", "escuchar", "valorar", "disfrutar", "confiar",
    "agradecer", "sonreír", "abrazar", "perdonar", "aprender",
    "compartir", "ayudar", "crecer", "soñar", "avanzar"
]

COMPLEMENTOS_UNIVERSALES = [
    "tu bienestar", "tu paz interior", "a los que quieres", "el momento presente",
    "tus logros", "tu camino", "las pequeñas cosas", "tus metas",
    "tu salud mental", "tu felicidad", "tu esfuerzo", "tu familia"
]

# ============================================
# 📝 FRASES CON SENTIDO PARA CADA TEMA (predefinidas)
# ============================================
FRASES_POR_TEMA = {
    "Motivacion": [
        "La motivación es como el combustible del alma.",
        "Cuando estás motivado, todo parece más fácil.",
        "No necesitas una razón gigante para empezar, solo un pequeño impulso.",
        "La motivación viene y va, pero tú puedes decidir mantenerla.",
        "Cada día es una nueva oportunidad para encender tu fuego interior.",
        "A veces, solo necesitas recordar por qué comenzaste.",
        "La energía positiva atrae buenas cosas.",
        "Tu entusiasmo puede contagiar a los demás.",
        "La fe en ti mismo es el primer paso hacia el éxito.",
        "El coraje no es no tener miedo, es seguir adelante a pesar de él."
    ],
    "Constancia": [
        "La constancia es la clave para lograr grandes cosas.",
        "No importa lo lento que vayas, si no te detienes, llegas.",
        "Los hábitos diarios construyen tu futuro.",
        "La perseverancia siempre tiene recompensa.",
        "Es mejor avanzar poco a poco que no avanzar nada.",
        "El esfuerzo constante vence cualquier obstáculo.",
        "La disciplina es la hermana de la constancia.",
        "Cada pequeño paso cuenta cuando se mantiene en el tiempo.",
        "La paciencia y la constancia mueven montañas.",
        "Nadie logra nada importante sin ser constante."
    ],
    "Superacion": [
        "Superarse es salir de tu zona de confort.",
        "Los errores son oportunidades para aprender y mejorar.",
        "Cada desafío te hace más fuerte si decides enfrentarlo.",
        "La verdadera superación viene de dentro.",
        "No compares tu progreso con el de otros, solo con el tuyo de ayer.",
        "Caerse está permitido, levantarse es obligatorio.",
        "La transformación personal requiere valentía.",
        "Siempre hay una versión mejor de ti esperando.",
        "Los obstáculos son el gimnasio del alma.",
        "El crecimiento duele, pero el resultado vale la pena."
    ],
    "Gratitud": [
        "Agradecer te cambia la perspectiva de la vida.",
        "Cuando das gracias, el corazón se llena de paz.",
        "La gratitud convierte lo poco en suficiente.",
        "Ser agradecido te ayuda a valorar lo que tienes.",
        "Reconocer lo bueno de tu vida te hace más feliz.",
        "Un simple 'gracias' puede iluminar el día de alguien.",
        "La gratitud es la memoria del corazón.",
        "Agradece incluso por los pequeños momentos.",
        "La vida se vuelve más ligera cuando practicas la gratitud.",
        "Cada noche, piensa en tres cosas buenas que te pasaron."
    ],
    "Logros": [
        "Tus logros son el reflejo de tu esfuerzo.",
        "Celebra cada victoria, por pequeña que sea.",
        "Los logros grandes empiezan con decisiones pequeñas.",
        "No olvides reconocer tu propio trabajo.",
        "Cada meta alcanzada te acerca a tu propósito.",
        "El éxito no es casualidad, es constancia.",
        "Tus triunfos inspiran a quienes te rodean.",
        "El camino al éxito está lleno de aprendizajes.",
        "A veces, el mayor logro es haber intentado.",
        "No subestimes lo que has conseguido hasta ahora."
    ],
    "AmorPropio": [
        "Amarte a ti mismo es el primer amor verdadero.",
        "Cuídate como cuidarías a alguien que quieres.",
        "El respeto hacia ti mismo es innegociable.",
        "No necesitas la aprobación de otros para valer.",
        "Aceptarte con tus virtudes y defectos es libertad.",
        "Mímate, date tiempo, escúchate.",
        "Tu autoestima es el cimiento de todo.",
        "Habla bien de ti, incluso en silencio.",
        "El amor propio no es egoísmo, es autocuidado.",
        "Sé tu mejor versión, pero sin exigirte perfección."
    ],
    "Esperanza": [
        "La esperanza es la luz en los días oscuros.",
        "Siempre hay una razón para seguir adelante.",
        "Después de la tormenta, siempre sale el sol.",
        "La ilusión te da fuerzas para continuar.",
        "Nunca pierdas la fe en que las cosas pueden mejorar.",
        "Un nuevo día trae nuevas oportunidades.",
        "La esperanza es lo último que se pierde.",
        "Cree que todo va a salir bien, aunque ahora no lo veas.",
        "El optimismo abre puertas que el miedo cierra.",
        "La vida siempre encuentra una forma de sorprenderte."
    ],
    "Confianza": [
        "Confiar en ti es el primer paso para todo.",
        "Sin confianza, hasta lo más fácil se vuelve difícil.",
        "La seguridad en uno mismo se construye con pequeños logros.",
        "No dudes de tu capacidad para resolver problemas.",
        "La fe en tus decisiones te da tranquilidad.",
        "La confianza no es arrogancia, es saber lo que vales.",
        "Cuando confías, atraes lo mejor.",
        "La incertidumbre se disipa con la confianza.",
        "Cree en tu instinto, casi nunca falla.",
        "La confianza es como un músculo, se ejercita."
    ],
    "Resiliencia": [
        "Resiliencia es caer y levantarse una y otra vez.",
        "Los golpes de la vida te enseñan a ser más fuerte.",
        "Las heridas sanan y te hacen más sabio.",
        "No importa cuántas veces te caigas, lo importante es volver a intentarlo.",
        "La adversidad forja el carácter.",
        "Siempre tienes la fuerza para sobreponerte.",
        "Acepta el dolor, pero no te estanques en él.",
        "Cada tropiezo es una lección disfrazada.",
        "La resiliencia es el arte de renacer.",
        "Lo que no te mata, te hace más fuerte."
    ],
    "Felicidad": [
        "La felicidad está en las cosas simples.",
        "No la busques fuera, está dentro de ti.",
        "Ser feliz no es tenerlo todo, es disfrutar lo que tienes.",
        "Sonríe, que la vida es corta.",
        "La alegría es contagiosa, compártela.",
        "El bienestar empieza por aceptar quién eres.",
        "La paz interior es el primer paso para la felicidad.",
        "Disfruta del presente, no te pierdas en el futuro.",
        "Las pequeñas cosas son las que más felicidad dan.",
        "La felicidad no es un destino, es una forma de viajar."
    ],
    "Proposito": [
        "Tener un propósito da sentido a tu vida.",
        "Tu misión es única, nadie puede hacerla por ti.",
        "Encuentra lo que te apasiona y síguelo.",
        "El propósito te guía cuando estás perdido.",
        "No hay una sola manera de cumplir tu misión.",
        "Cada persona tiene un talento especial que ofrecer.",
        "La vocación es cuando tu trabajo y tu pasión se unen.",
        "Pregúntate: ¿qué quiero dejar en el mundo?",
        "El propósito no es un destino, es un camino.",
        "Cuando encuentras tu norte, todo tiene más sentido."
    ],
    "Optimismo": [
        "Ver el vaso medio lleno cambia tu día.",
        "El optimismo es una elección, no un don.",
        "Siempre hay un lado bueno en cada situación.",
        "Las dificultades son oportunidades disfrazadas.",
        "La actitud positiva te abre puertas.",
        "Ríete de los problemas, les quitas poder.",
        "El optimismo atrae buenas energías.",
        "Cree que todo irá bien y así será.",
        "Una sonrisa puede cambiar tu perspectiva.",
        "La esperanza es el cimiento del optimismo."
    ],
    "PazInterior": [
        "La paz interior empieza cuando aceptas lo que no puedes cambiar.",
        "No dejes que el ruido exterior te robe la calma.",
        "Respira profundamente y suelta lo que no te sirve.",
        "La serenidad es un refugio en medio del caos.",
        "Aprende a desconectar para reconectar contigo.",
        "El silencio también es una forma de hablar.",
        "La tranquilidad mental no tiene precio.",
        "El equilibrio emocional se construye día a día.",
        "Medita, camina, escucha tu interior.",
        "La paz no es ausencia de problemas, es la forma de enfrentarlos."
    ],
    "Actitud": [
        "Tu actitud determina tu altitud.",
        "Elige ver lo positivo, aunque cueste.",
        "La forma en que enfrentas las cosas marca la diferencia.",
        "Una buena actitud atrae soluciones.",
        "La disposición es más importante que la habilidad.",
        "No dejes que los demás te contaminen con su negatividad.",
        "Cada día es una nueva oportunidad para empezar con buena actitud.",
        "La actitud correcta convierte los problemas en retos.",
        "Sonreír ante la adversidad es un superpoder.",
        "Tu perspectiva lo cambia todo."
    ],
    "Crecimiento": [
        "Crecer es salir de tu zona de confort.",
        "El aprendizaje es un viaje sin fin.",
        "Cada experiencia te hace más sabio.",
        "La madurez llega cuando aceptas tus errores.",
        "El crecimiento personal requiere paciencia.",
        "No tengas miedo al cambio, es necesario para crecer.",
        "Las caídas te enseñan a levantarte mejor.",
        "La evolución es constante, como la vida.",
        "Aprender de los demás también es crecer.",
        "Cada día puedes ser un poco mejor que ayer."
    ],
    "Cambio": [
        "El cambio es la única constante en la vida.",
        "Adaptarse es clave para sobrevivir.",
        "A veces, los cambios más difíciles son los que más te benefician.",
        "No temas a lo nuevo, puede ser el inicio de algo mejor.",
        "La vida te pone desafíos para que evoluciones.",
        "Cambiar de opinión no es debilidad, es crecimiento.",
        "Los cambios pequeños pueden tener grandes efectos.",
        "Acepta el cambio, aunque no lo entiendas.",
        "El cambio es la oportunidad de reinventarse.",
        "No te aferres a lo que ya no te sirve."
    ],
    "Libertad": [
        "La libertad es la capacidad de elegir tu propio camino.",
        "Ser libre es tomar decisiones sin miedo.",
        "La independencia no es hacer lo que quieras, sino hacer lo que debes sin ataduras.",
        "La auténtica libertad está en la mente.",
        "No dejes que nadie te quite tu poder de decidir.",
        "La libertad se gana con responsabilidad.",
        "Despégate de lo que te limita.",
        "Ser libre es ser dueño de tus actos.",
        "La libertad interior no depende de lo exterior.",
        "Vivir sin ataduras es el mayor lujo."
    ],
    "Aprendizaje": [
        "Aprender es abrir puertas que desconocías.",
        "Cada error es una lección, no un fracaso.",
        "La curiosidad es el motor del aprendizaje.",
        "Nunca es tarde para aprender algo nuevo.",
        "El conocimiento te da alas para volar más alto.",
        "Aprende de los demás, pero también de tus errores.",
        "La educación es la herramienta más poderosa.",
        "Cada experiencia te enseña algo valioso.",
        "Enseñar es la mejor forma de aprender.",
        "La sabiduría no es saber mucho, es saber aplicar."
    ],
    "Sabiduria": [
        "La sabiduría no se mide por lo que sabes, sino por cómo vives.",
        "La prudencia te ayuda a tomar mejores decisiones.",
        "Las experiencias te dan sabiduría si sabes escucharlas.",
        "Saber cuándo callar es tan importante como saber hablar.",
        "La cordura es actuar con sensatez, incluso en la tormenta.",
        "La sabiduría te permite ver más allá de lo evidente.",
        "Aprende de los que han vivido más que tú.",
        "La intuición es una forma de sabiduría silenciosa.",
        "No basta con tener información, hay que entenderla.",
        "La sabiduría se comparte, no se guarda."
    ],
    "Conexion": [
        "Conectar con los demás te hace más humano.",
        "La empatía es el puente entre las personas.",
        "Una buena relación se construye con comunicación.",
        "El vínculo verdadero va más allá de las palabras.",
        "La comunidad te da fuerza y apoyo.",
        "Escuchar es la base de cualquier conexión.",
        "Compartir emociones te acerca a los demás.",
        "La armonía nace cuando nos entendemos.",
        "Una sonrisa puede ser el inicio de una gran amistad.",
        "La solidaridad une corazones."
    ]
}

# ============================================
# 📝 GENERACIÓN DE PREGUNTA Y DESARROLLO
# ============================================
def generar_pregunta(tema_nombre):
    """Genera una pregunta clara y directa sobre el tema."""
    preguntas_base = [
        f"¿Alguna vez has reflexionado sobre la importancia de {tema_nombre.lower()} en tu vida?",
        f"¿Qué significa para ti {tema_nombre.lower()}?",
        f"¿Cómo aplicas {tema_nombre.lower()} en tu día a día?",
        f"¿Crees que {tema_nombre.lower()} puede cambiar tu forma de ver las cosas?",
        f"¿Cuál es tu mayor aprendizaje sobre {tema_nombre.lower()}?",
        f"¿Te has preguntado alguna vez cómo {tema_nombre.lower()} influye en tus decisiones?",
        f"¿Qué harías si te faltara {tema_nombre.lower()} en tu vida?",
        f"¿Cuándo fue la última vez que practicaste {tema_nombre.lower()} de forma consciente?",
        f"¿Cómo te sientes cuando hablas de {tema_nombre.lower()}?",
        f"¿Qué consejo darías sobre {tema_nombre.lower()} a alguien que empieza?"
    ]
    return random.choice(preguntas_base)

def generar_frase_desarrollo(tema_nombre):
    """Genera una frase de desarrollo con sentido, específica para el tema."""
    if tema_nombre in FRASES_POR_TEMA:
        frases = FRASES_POR_TEMA[tema_nombre]
        frase = random.choice(frases)
    else:
        femeninas = ("a", "ad", "ión", "umbre", "dad", "tad", "sis", "ez", "eza")
        if tema_nombre.lower().endswith(femeninas) and tema_nombre.lower() not in ["amor", "cambio", "crecimiento", "propósito", "optimismo", "entusiasmo", "aprendizaje", "conocimiento"]:
            articulo = "la"
        else:
            articulo = "el"
        if tema_nombre.lower() in ["amor", "cambio", "crecimiento", "propósito", "optimismo", "entusiasmo", "aprendizaje", "conocimiento"]:
            articulo = "el"
        
        verbo = random.choice(VERBOS_UNIVERSALES)
        complemento = random.choice(COMPLEMENTOS_UNIVERSALES)
        
        plantilla = random.choice(FRASES_UNIVERSALES)
        frase = plantilla.format(
            verbo=verbo,
            complemento=complemento,
            tema=articulo + " " + tema_nombre
        )
        frase = frase[0].upper() + frase[1:]
        if frase[-1] not in [".", "!", "?"]:
            frase += "."
    
    if random.random() < 0.2:
        intro = random.choice(["Mira, ", "O sea, ", "Fíjate, ", "Es que ", "La verdad es que "])
        frase = intro + frase[0].lower() + frase[1:]
    
    if random.random() < 0.2:
        retorica = random.choice([" ¿no te parece?", " ¿verdad?", " ¿a que sí?"])
        frase = frase.rstrip(".!?") + retorica + "."
    
    return frase

def generar_texto_completo(tema_nombre):
    pregunta = generar_pregunta(tema_nombre)
    num_frases = random.choice([6, 7, 8])
    frases = []
    for _ in range(num_frases):
        frases.append(generar_frase_desarrollo(tema_nombre))
    random.shuffle(frases)
    texto_completo = pregunta + "\n\n" + "\n\n".join(frases)
    return texto_completo

def dividir_en_parrafos(texto, num_partes):
    texto = re.sub(r'Te leo en los comentarios\s*[.!?]*\s*', '', texto)
    oraciones = re.findall(r'[^.!?]+[.!?]', texto)
    oraciones = [o.strip() for o in oraciones if len(o.strip()) > 5]
    
    if not oraciones:
        oraciones = [texto.strip()]
    
    if oraciones and "¿" in oraciones[0]:
        pregunta = oraciones[0]
        resto = oraciones[1:]
        random.shuffle(resto)
        oraciones = [pregunta] + resto
    else:
        random.shuffle(oraciones)
    
    parrafos = []
    grupo_actual = []
    lineas_objetivo = random.randint(3, 5)
    lineas_actuales = 0
    
    for oracion in oraciones:
        lineas_oracion = max(1, len(oracion) // 28)
        if lineas_actuales + lineas_oracion > lineas_objetivo and grupo_actual:
            parrafos.append(" ".join(grupo_actual))
            grupo_actual = []
            lineas_actuales = 0
            lineas_objetivo = random.randint(3, 5)
        grupo_actual.append(oracion)
        lineas_actuales += lineas_oracion
    
    if grupo_actual:
        parrafos.append(" ".join(grupo_actual))
    
    while len(parrafos) > num_partes - 1:
        ultimo = parrafos.pop() + " " + parrafos.pop()
        parrafos.append(ultimo)
    while len(parrafos) < num_partes - 1:
        parrafos.append("Sigue adelante con fe y determinación.")
    
    parrafos.append("Te leo en los comentarios")
    return parrafos[:num_partes]

def crear_video(texto, dia_semana, tema_nombre, numero):
    num_parrafos = random.choice([6, 7, 8])
    duracion_total = random.uniform(70, 85)
    duracion_por_parrafo = duracion_total / num_parrafos
    duraciones = [duracion_por_parrafo] * num_parrafos

    print(f"   🎬 Video {numero} ({dia_semana} - {tema_nombre}) - {num_parrafos} párrafos, {duracion_total:.1f}s")
    print(f"   ⏱️  Cada párrafo: {duracion_por_parrafo:.1f}s")
    os.makedirs("videos", exist_ok=True)

    parrafos = dividir_en_parrafos(texto, num_parrafos)

    palabras_clave = texto.split()[:4]
    tema_imagen = " ".join(palabras_clave) if palabras_clave else "motivacion"
    tema_imagen = re.sub(r'[^\w\s]', '', tema_imagen)

    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": CLAVE_PEXELS}
    params = {"query": tema_imagen, "per_page": 3, "orientation": "portrait", "page": random.randint(1, 5)}

    imagen_url = None
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            fotos = resp.json().get("photos", [])
            if fotos:
                imagen_url = random.choice(fotos)["src"]["large"]
    except:
        pass

    if not imagen_url:
        imagen_url = "https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg"

    try:
        img_data = requests.get(imagen_url, timeout=10).content
        with open("temp_fondo.jpg", "wb") as f:
            f.write(img_data)
    except:
        return

    clips = []
    for i, parrafo in enumerate(parrafos):
        img = Image.open("temp_fondo.jpg").convert("RGB")
        img = img.resize((1080, 1920))
        draw = ImageDraw.Draw(img)

        lineas = textwrap.wrap(parrafo, width=28, break_long_words=False)
        total_lineas = len(lineas)

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

        y = y_inicio
        for linea in lineas:
            bbox = draw.textbbox((0, 0), linea, font=font)
            ancho_linea = bbox[2] - bbox[0]
            x = (1080 - ancho_linea) // 2
            draw.text((x, y), linea, font=font, fill='white', stroke_width=5, stroke_fill='black')
            y += font_size * 1.3

        img.save(f"temp_texto_{i}.jpg", "JPEG")
        clip = ImageClip(f"temp_texto_{i}.jpg", duration=duraciones[i])
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")

    tz_venezuela = timezone(timedelta(hours=-4))
    ahora = datetime.now(tz_venezuela)
    fecha_hora = ahora.strftime("%d-%m-%Y-%H-%M-%S")
    nombre = f"videos/{dia_semana}-{tema_nombre}-{fecha_hora}-video-{numero:03d}.mp4"

    video.write_videofile(nombre, fps=15, codec="libx264", audio=False)
    print(f"   ✅ Video guardado: {nombre}")

    for f in os.listdir("."):
        if f.startswith("temp_") and f.endswith(".jpg"):
            try:
                os.remove(f)
            except:
                pass

# ============================================
# 🎯 SELECCIÓN DE TEMAS
# ============================================
def seleccionar_temas(opcion, videos_por_dia):
    if opcion.lower() in ["todo", "aleatorio", "azar", "random"]:
        temas_seleccionados = random.sample(TEMAS_PREDEFINIDOS, 7)
        print(f"📌 Temas seleccionados: {', '.join(temas_seleccionados)}")
        return {i: tema for i, tema in enumerate(temas_seleccionados)}
    else:
        print(f"📌 Usando el tema: {opcion}")
        return {i: opcion for i in range(7)}

# ============================================
# 🚀 EJECUCIÓN PRINCIPAL
# ============================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generador de videos semanales")
    parser.add_argument("--videos", type=int, default=5, help="Número de videos por día")
    parser.add_argument("--tema", type=str, default="todo", help="Tema o 'todo' para aleatorio")
    parser.add_argument("--zip", type=str, help="Nombre del archivo ZIP (sin extensión o con .zip)")
    parser.add_argument("--no-zip", action="store_true", help="No crear ZIP")
    args = parser.parse_args()

    videos_por_dia = args.videos
    tema_input = args.tema

    # 🔥 El ZIP se llama videos-generados.zip por defecto
    if args.zip:
        nombre_zip = args.zip if args.zip.endswith(".zip") else args.zip + ".zip"
    else:
        nombre_zip = "videos-generados.zip"

    print("🎬 ¡Generador de videos para toda la semana!")
    print("=" * 50)
    print(f"📝 Videos por día: {videos_por_dia}")
    print(f"🎯 Temática: {tema_input}")
    print(f"📦 ZIP: {nombre_zip}")
    print("=" * 50)

    TEMAS = seleccionar_temas(tema_input, videos_por_dia)

    DIAS_SEMANA = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"}

    print(f"\n📝 Generando {videos_por_dia} videos por cada día de la semana")
    print(f"📊 Total: {videos_por_dia * 7} videos")
    print("=" * 50)

    for dia, tema_nombre in TEMAS.items():
        dia_nombre = DIAS_SEMANA.get(dia, "Día")
        print(f"\n📅 Procesando: {dia_nombre} - {tema_nombre}")
        print(f"   📝 Generando {videos_por_dia} videos...")

        for i in range(videos_por_dia):
            texto = generar_texto_completo(tema_nombre)
            crear_video(texto, dia_nombre, tema_nombre, i+1)
            time.sleep(0.5)

    print("\n🎉 ¡Todos los videos generados!")

    if not args.no_zip:
        print(f"📦 Creando ZIP: {nombre_zip} ...")
        with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk("videos"):
                for file in files:
                    # 🔥 Añadir la carpeta "videos/" dentro del ZIP
                    zipf.write(os.path.join(root, file), arcname=os.path.join("videos", file))
        print(f"✅ ZIP creado: {nombre_zip}")
        print(f"📁 Revisa la carpeta 'videos' y el archivo '{nombre_zip}'.")
    else:
        print("⏭️  No se creó ZIP (opción --no-zip activada).")
