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
# LISTA DE TEMAS PREDEFINIDOS (20) CON TILDES Y ESPACIOS
# ============================================
TEMAS_PREDEFINIDOS = [
    "Motivación", "Constancia", "Superación", "Gratitud", "Logros",
    "Amor Propio", "Esperanza", "Confianza", "Resiliencia", "Felicidad",
    "Propósito", "Optimismo", "Paz", "Actitud", "Crecimiento",
    "Cambio", "Libertad", "Aprendizaje", "Sabiduría", "Conexión"
]

# ============================================
# GANCHOS DE ALTO IMPACTO (HOOKS) PARA EMPEZAR
# ============================================
GANCHOS_INICIALES = [
    "⚠️ Escucha esto antes de que termine tu día...",
    "🔥 Lo que nadie te dice sobre este tema...",
    "💡 Si necesitas un cambio real, quédate hasta el final.",
    "🛑 Detente un segundo y presta mucha atención a esto.",
    "⚡ Esto va a cambiar tu perspectiva por completo hoy.",
    "🎯 El secreto que pocos entienden y todos buscan.",
    "👁️ Abre los ojos y mira lo que estás ignorando."
]

# ============================================
# FRASES DE VALOR POR TEMA
# ============================================
FRASES_POR_TEMA = {
    "Motivación": [
        "La motivación te da energía para empezar, pero el hábito te mantiene.",
        "Tu entusiasmo tiene el poder de contagiar a quienes te rodean.",
        "La fe en ti mismo abre puertas que antes parecían cerradas.",
        "El coraje no es la ausencia de miedo, es seguir adelante a pesar de él.",
        "La determinación silenciosa te lleva a alcanzar metas lejanas.",
        "La disciplina convierte los sueños más locos en realidades diarias.",
        "La resiliencia te enseña a levantarte con más fuerza tras cada caída.",
        "La voluntad te permite avanzar cuando el camino se pone oscuro.",
        "El impulso inicial es clave, pero la constancia es la que corona el éxito."
    ],
    "Constancia": [
        "La constancia silenciosa construye imperios día tras día.",
        "La perseverancia te acerca a tus metas aunque el camino sea largo y duro.",
        "Los pequeños hábitos diarios moldean tu carácter y tu futuro.",
        "La paciencia te enseña a esperar el momento exacto para cosechar.",
        "El esfuerzo constante e inquebrantable vence cualquier obstáculo.",
        "Una rutina bien estructurada te da estabilidad y progreso real.",
        "La disciplina te mantiene enfocado cuando las distracciones abundan.",
        "La constancia te impide rendirte cuando las cosas se ponen difíciles.",
        "La resistencia te permite seguir avanzando sin desfallecer en el intento."
    ],
    "Superación": [
        "Superarse significa salir de tu zona de confort y abrazar el crecimiento.",
        "Cada error es una lección maestra que ningún libro puede darte.",
        "Cada desafío superado te vuelve mucho más fuerte y sabio.",
        "La transformación personal empieza en el momento exacto en que decides cambiar.",
        "El aprendizaje continuo te convierte en la mejor versión de ti mismo.",
        "La fortaleza interior te permite recuperarte de los golpes más duros.",
        "Cada nueva mañana es una oportunidad perfecta para empezar de cero.",
        "Mejorar un 1% cada día te lleva a lugares que nunca imaginaste.",
        "El progreso constante, por pequeño que parezca, siempre suma."
    ],
    "Gratitud": [
        "Agradecer transforma lo que tienes en suficiente y te llena de paz.",
        "Dar las gracias te conecta instantáneamente con lo mejor de la vida.",
        "Valorar lo que ya posees te hace más feliz y profundamente humano.",
        "Reconocer lo bueno a tu alrededor eleva tu vibración diaria.",
        "Un simple gracias abre tu corazón a una alegría genuina.",
        "La generosidad y la abundancia florecen donde hay gratitud.",
        "La humildad te recuerda que cada bendición es un regalo valioso.",
        "La satisfacción total nace cuando valoras cada pequeño detalle.",
        "La paz interior llega cuando aceptas con gratitud tu presente."
    ],
    "Logros": [
        "Tus logros son el reflejo exacto del esfuerzo que has invertido.",
        "Cada pequeña victoria merece ser celebrada con orgullo.",
        "Las metas alcanzadas te impulsan a soñar todavía más alto.",
        "El verdadero éxito es el resultado directo de la constancia.",
        "Los triunfos te demuestran que tu sacrificio valió la pena.",
        "El progreso diario te muestra que vas por el camino correcto.",
        "La realización personal llega cuando cumples aquello que prometiste.",
        "Las conquistas de hoy construyen tu historia de éxito mañana.",
        "Cumplir tus objetivos alimenta tu confianza y tu motivación."
    ],
    "Amor Propio": [
        "Amarte a ti mismo es el cimiento de cualquier relación sana.",
        "Aceptarte sin condiciones es el primer paso hacia la paz mental.",
        "Cuidar de ti te da la fuerza necesaria para cuidar de los demás.",
        "Perdonarte los errores del pasado te libera de cargas inútiles.",
        "Confiar ciegamente en ti es la clave de todo gran logro.",
        "Respetar tus propios límites es la base del verdadero poder personal.",
        "La libertad interior florece cuando dejas de buscar aprobación ajena.",
        "La paz llega cuando dejas de juzgarte tan severamente.",
        "Ser fiel a tus principios te mantiene conectado con tu esencia."
    ],
    "Esperanza": [
        "La esperanza ilumina los días más grises y te devuelve el aliento.",
        "La ilusión te mantiene con el corazón encendido y ganas de luchar.",
        "La fe en el mañana te ayuda a superar cualquier tormenta actual.",
        "El optimismo abre puertas que el miedo y la duda cierran.",
        "La confianza en que todo mejorará te otorga una calma profunda.",
        "La luz de la esperanza siempre encuentra un resquicio para entrar.",
        "La promesa de un nuevo comienzo renueva por completo tu alma.",
        "La convicción te sostiene firme cuando todo parece desmoronarse.",
        "Saber que hay una salida te da la serenidad que necesitas."
    ],
    "Confianza": [
        "Confiar en tus capacidades es la llave para tomar decisiones sabias.",
        "La seguridad en ti mismo te permite enfrentar cualquier reto con calma.",
        "Saber exactamente lo que vales te da paz en los momentos de dudas.",
        "La convicción firme te ayuda a mantener el rumbo sin vacilar.",
        "La fe en tu talento te impulsa a lograr lo imposible.",
        "La determinación te lleva a cumplir tus metas sin mirar atrás.",
        "La firmeza te otorga el valor para decir no cuando es necesario.",
        "La estabilidad emocional nace de una sólida confianza interna.",
        "Sentir que puedes lograrlo es el primer paso para hacerlo realidad."
    ],
    "Resiliencia": [
        "La resiliencia te levanta con más fuerza cada vez que la vida te bota.",
        "La fortaleza interior te permite soportar las peores tormentas.",
        "La resistencia te enseña a seguir avanzando sin importar el dolor.",
        "La tenacidad es tu mejor aliada para no rendirte jamás.",
        "La entereza te permite mantener la mente fría en medio del caos.",
        "La firmeza de tu carácter destruye cualquier obstáculo en el camino.",
        "La constancia frente al dolor te convierte en alguien indestructible.",
        "La determinación te impulsa a buscar soluciones y no excusas.",
        "El temple adecuado te prepara para dominar lo inesperado."
    ],
    "Felicidad": [
        "La verdadera felicidad se esconde en los pequeños detalles cotidianos.",
        "La alegría brota cuando aprendes a vivir y disfrutar el presente.",
        "La plenitud llega cuando te aceptas tal y como eres hoy.",
        "La satisfacción te envuelve cuando valoras tus bendiciones.",
        "El bienestar se cultiva con buenos hábitos y pensamientos limpios.",
        "La calma mental te permite saborear cada instante sin prisa.",
        "La paz te inunda cuando sueltas las preocupaciones que no controlas.",
        "El gozo se multiplica maravillosamente cuando decides compartirlo.",
        "Vivir en armonía contigo mismo es la cúspide de la dicha."
    ],
    "Propósito": [
        "Un propósito claro le da brújula, sentido y dirección a tu existencia.",
        "Tu misión personal te guía directo hacia lo que realmente importa.",
        "Tu verdadera vocación te conecta con tus talentos más profundos.",
        "Una meta definida focaliza toda tu energía creativa y mental.",
        "El objetivo claro te protege de las distracciones del camino.",
        "Tu destino se construye con cada pequeña elección de hoy.",
        "Una razón de ser poderosa te levanta cuando las fuerzas fallan.",
        "Mantener el norte fijo asegura que llegarás a donde deseas.",
        "Tus más altas aspiraciones te elevan por encima de la mediocridad."
    ],
    "Optimismo": [
        "El optimismo inteligente te enseña a ver oportunidades en cada crisis.",
        "La esperanza alimenta la certeza absoluta de que viene algo mejor.",
        "La fe te sostiene firme cuando la incertidumbre intenta nublarte.",
        "La confianza en el futuro te permite caminar con paso firme.",
        "Una actitud positiva atrae oportunidades y personas extraordinarias.",
        "La alegría se vuelve un hábito cuando decides mirar lo bueno.",
        "La luz del optimismo desvanece las sombras del miedo.",
        "El entusiasmo es el motor que acelera tus proyectos de vida.",
        "La certeza de que saldrás adelante te regala paz inmediata."
    ],
    "Paz": [
        "La paz interior es el lujo más grande que puedes regalarte.",
        "La calma mental te permite decidir con inteligencia y sin estrés.",
        "La tranquilidad llega el día en que entiendes que no controlas todo.",
        "La armonía te reconecta de inmediato con tu fuente de energía.",
        "La quietud absoluta es donde nacen las soluciones más creativas.",
        "La serenidad te envuelve en cuanto aceptas el curso natural de las cosas.",
        "El equilibrio emocional protege tu mente de ataques externos.",
        "Responder con calma ante el caos es una muestra de gran evolución.",
        "La compasión hacia ti mismo inaugura tu camino hacia la paz."
    ],
    "Actitud": [
        "Tu actitud define exactamente cómo golpeas de vuelta a los problemas.",
        "Una disposición positiva abre puertas que el pesimismo sella.",
        "La postura mental con la que miras el mundo cambia tu realidad.",
        "Una mentalidad de crecimiento disuelve cualquier límite autoimpuesto.",
        "Enfocarte en la solución te inyecta una energía imparable.",
        "Una perspectiva optimista reescribe por completo tu historia.",
        "Una visión clara descubre oro donde otros solo ven tierra.",
        "Mantener el rumbo correcto depende de tu actitud al despertar.",
        "La forma en que afrontas las pruebas determina tu destino."
    ],
    "Crecimiento": [
        "El crecimiento personal exige dejar atrás versiones viejas de ti.",
        "La evolución te recuerda que cambiar de piel es parte del proceso.",
        "La madurez te regala la claridad para tomar decisiones impecables.",
        "Expandir tus horizontes destruye los miedos que te paralizaban.",
        "La mejora continua es la única ruta directa hacia la excelencia.",
        "Cada pequeño avance de hoy se convierte en tu victoria de mañana.",
        "Superar tus propios límites te demuestra de lo que estás hecho.",
        "La transformación personal te recarga de una energía magnética.",
        "Fortalecer tu mente te vuelve impermeable a las opiniones ajenas."
    ],
    "Cambio": [
        "El cambio te arranca de la comodidad para llevarte a tu siguiente nivel.",
        "La transformación es la prueba reina de que estás vivo y evolucionando.",
        "Saber adaptarte con elegancia es tu superpoder ante la incertidumbre.",
        "Renovarse por dentro te libera de ciclos que ya no te sirven.",
        "Aceptar las modificaciones del destino te ahorra sufrimiento innecesario.",
        "La innovación nace de atreverse a hacer las cosas de forma distinta.",
        "Darle variedad a tus días oxigena tu mente y tu creatividad.",
        "Modificar tus malos hábitos es el atajo hacia la vida que mereces.",
        "Comprender que cada final es un nuevo comienzo te da libertad."
    ],
    "Libertad": [
        "La verdadera libertad consiste en tener el poder absoluto de elegir.",
        "La independencia madura te permite caminar sin depender de nadie.",
        "Ser autónomo te convierte en el único arquitecto de tu destino.",
        "Liberarte de expectativas ajenas te quita un peso monumental.",
        "La emancipación mental te permite expresarte sin pedir disculpas.",
        "Fluir con ligereza te da la capacidad de adaptarte a cualquier sitio.",
        "La autenticidad te conecta con personas que vibran igual que tú.",
        "La flexibilidad mental es la armadura de los espíritus libres.",
        "Desenvolverte con seguridad es la marca de una mente liberada."
    ],
    "Aprendizaje": [
        "El aprendizaje constante expande tus fronteras mentales sin límites.",
        "Compartir lo que sabes multiplica el valor de tu propio conocimiento.",
        "Una mente instruida navega con facilidad por aguas turbulentas.",
        "La educación formal te da bases, pero la curiosidad te da el mundo.",
        "El conocimiento acumulado es la herramienta más barata para triunfar.",
        "Aplicar la sabiduría práctica en tu día a día marca la diferencia.",
        "La experiencia real te enseña lecciones que ningún título otorga.",
        "Aprender del dolor de los errores te vuelve un estratega experto.",
        "Comprender la raíz de las cosas te da control sobre tu entorno."
    ],
    "Sabiduría": [
        "La verdadera sabiduría se nota en la forma pacífica en que callas.",
        "La prudencia aconseja medir las consecuencias antes de dar un paso.",
        "La sensatez te mantiene siempre en el centro del equilibrio.",
        "La cordura es tu mejor armadura contra los arrebatos del ego.",
        "La mesura te enseña a disfrutar de todo sin caer en excesos.",
        "Saber cuándo guardar silencio es una muestra superior de inteligencia.",
        "La templanza te da el timón exacto para dominar tus emociones.",
        "La moderación protege tu salud mental, física y financiera.",
        "La intuición fina es la voz silenciosa de tu propia sabiduría."
    ],
    "Conexión": [
        "Conectar de verdad con otros le da un sentido profundo a la existencia.",
        "Un vínculo honesto y sincero es el refugio más seguro que existe.",
        "Los lazos emocionales auténticos sanan heridas invisibles del pasado.",
        "Construir relaciones sanas requiere paciencia, escucha y respeto.",
        "Una comunicación transparente evita ruidos y fortalece cualquier unión.",
        "El afecto genuino te entrega la calidez que necesitas para seguir.",
        "La empatía radical te permite comprender mundos distintos al tuyo.",
        "La solidaridad multiplica las fuerzas cuando el peso es demasiado.",
        "Caminar unidos hace que los retos más pesados se vuelvan ligeros."
    ]
}

def obtener_frases_para_tema(tema):
    if tema in FRASES_POR_TEMA:
        return FRASES_POR_TEMA[tema]
    else:
        # Generación dinámica básica si el tema es personalizado
        return [
            f"El valor de {tema.lower()} transforma por completo tu perspectiva.",
            f"Cultivar {tema.lower()} cada día es una decisión que vale la pena.",
            f"La clave secreta detrás de {tema.lower()} es la constancia.",
            f"Cuando entiendes {tema.lower()}, tu manera de avanzar cambia.",
            f"No olvides que {tema.lower()} es el motor de grandes cambios.",
            f"Aplica {tema.lower()} en tus momentos más retadores.",
            f"El poder de {tema.lower()} se nota en los pequeños detalles.",
            f"Construye tu futuro apoyándote en {tema.lower()}."
        ]

# ============================================
# GENERACIÓN DE ESTRUCTURA DEL VIDEO (75-85s)
# ============================================
def generar_pregunta(tema):
    tema_lower = tema.lower()
    preguntas = [
        f"¿Alguna vez te has detenido a pensar en el poder real de {tema_lower}?",
        f"¿Qué tan dispuesto estás a transformar tu vida aplicando {tema_lower}?",
        f"¿Por qué ignoras el impacto que {tema_lower} tiene en tu día a día?",
        f"¿Te has preguntado dónde estarías si dominaras {tema_lower}?",
        f"El gran error con {tema_lower} es creer que llega solo. Escucha esto."
    ]
    return random.choice(preguntas)

def dividir_en_parrafos(tema, num_parrafos):
    # Párrafo 1: Gancho potente
    hook = random.choice(GANCHOS_INICIALES)
    
    # Párrafo 2: Pregunta retadora
    pregunta = generar_pregunta(tema)
    
    # Párrafos intermedios: Frases de valor del tema
    frases_disponibles = obtener_frases_para_tema(tema)
    random.shuffle(frases_disponibles)
    
    num_cuerpo = num_parrafos - 3 # Restamos hook, pregunta y CTA final
    if num_cuerpo < 1:
        num_cuerpo = 1
        
    cuerpo = frases_disponibles[:num_cuerpo]
    while len(cuerpo) < num_cuerpo:
        cuerpo.append("Sigue adelante con fe y determinación absoluta.")
        
    # Párrafo final: Llamado a la acción (CTA)
    cta = "Guarda este video y compártelo con alguien que lo necesite hoy."
    
    parrafos = [hook, pregunta] + cuerpo + [cta]
    
    # Ajuste exacto por si acaso
    while len(parrafos) < num_parrafos:
        parrafos.insert(-1, "Cada paso cuenta en este camino.")
    while len(parrafos) > num_parrafos:
        parrafos.pop(-2)
        
    return parrafos

# ============================================
# OBTENER IMÁGENES DE PEXELS
# ============================================
def obtener_imagenes(query, cantidad):
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": CLAVE_PEXELS}
    params = {
        "query": query,
        "per_page": max(cantidad, 5),
        "orientation": "portrait",
        "page": random.randint(1, 5)
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            fotos = resp.json().get("photos", [])
            if fotos:
                return [foto["src"]["large"] for foto in fotos[:cantidad]]
    except:
        pass
    return ["https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg"] * cantidad

# ============================================
# CREAR VÍDEO CON DISEÑO MEJORADO
# ============================================
def crear_video(tema, dia_semana, numero):
    # Duración total estricta entre 75 y 85 segundos
    num_parrafos = random.choice([6, 7, 8])
    duracion_total = random.uniform(75, 85)
    duracion_por_parrafo = duracion_total / num_parrafos
    duraciones = [duracion_por_parrafo] * num_parrafos

    print(f"   🎬 Video {numero} ({dia_semana} - {tema}) - {num_parrafos} párrafos, {duracion_total:.1f}s")
    os.makedirs("videos", exist_ok=True)

    parrafos = dividir_en_parrafos(tema, num_parrafos)

    query = tema.replace(" ", "").lower()
    imagenes_urls = obtener_imagenes(query, num_parrafos)
    while len(imagenes_urls) < num_parrafos:
        imagenes_urls.append("https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg")

    clips = []
    for i, parrafo in enumerate(parrafos):
        try:
            img_data = requests.get(imagenes_urls[i], timeout=10).content
            with open(f"temp_fondo_{i}.jpg", "wb") as f:
                f.write(img_data)
            img = Image.open(f"temp_fondo_{i}.jpg").convert("RGB")
        except:
            img = Image.new("RGB", (1080, 1920), color=(30, 30, 30))
        
        # Filtro de desenfoque y oscurecimiento para mejorar contraste del texto
        img = img.filter(ImageFilter.GaussianBlur(radius=3))
        
        # Crear capa oscura semitransparente para legibilidad perfecta
        capa_oscura = Image.new("RGBA", img.size, (0, 0, 0, 110))
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, capa_oscura).convert("RGB")
        
        img = img.resize((1080, 1920))
        draw = ImageDraw.Draw(img)

        # Ajuste de tipografía y ancho de texto centrado
        lineas = textwrap.wrap(parrafo, width=26, break_long_words=False)
        total_lineas = len(lineas)
        if total_lineas == 0:
            lineas = [" "]
            total_lineas = 1

        MARGEN_Y = 300
        font_size = int((1920 - 2 * MARGEN_Y) / (total_lineas * 1.5))
        font_size = max(35, min(font_size, 65))

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", font_size)
            except:
                font = ImageFont.load_default()

        altura_bloque = total_lineas * (font_size * 1.4)
        y_inicio = (1920 - altura_bloque) // 2  # Centrado vertical estético

        # Dibujar líneas con estilo moderno (Sombra sutil + Texto blanco limpio)
        y = y_inicio
        for linea in lineas:
            bbox = draw.textbbox((0, 0), linea, font=font)
            ancho_linea = bbox[2] - bbox[0]
            x = (1080 - ancho_linea) // 2

            # Sombra de apoyo
            draw.text((x+4, y+4), linea, font=font, fill=(0, 0, 0, 220))
            # Texto principal en blanco
            draw.text((x, y), linea, font=font, fill='white')
            y += font_size * 1.4

        # FIRMA elegante abajo a la derecha
        firma = "@jonathan_irigoyen"
        try:
            font_firma = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
        except:
            try:
                font_firma = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 26)
            except:
                font_firma = ImageFont.load_default()
        
        bbox_firma = draw.textbbox((0, 0), firma, font=font_firma)
        ancho_firma = bbox_firma[2] - bbox_firma[0]
        x_firma = 1080 - ancho_firma - 40
        y_firma = 1920 - 80

        draw.text((x_firma+2, y_firma+2), firma, font=font_firma, fill=(0, 0, 0, 200))
        draw.text((x_firma, y_firma), firma, font=font_firma, fill=(240, 240, 240))

        img.save(f"temp_texto_{i}.jpg", "JPEG")
        
        # Clip con transiciones suaves de entrada y salida
        clip = ImageClip(f"temp_texto_{i}.jpg", duration=duraciones[i])
        clip = clip.fadein(0.25).fadeout(0.25)
        clips.append(clip)

        try:
            os.remove(f"temp_fondo_{i}.jpg")
        except:
            pass

    video = concatenate_videoclips(clips, method="compose")

    tz_venezuela = timezone(timedelta(hours=-4))
    ahora = datetime.now(tz_venezuela)
    fecha_hora = ahora.strftime("%d-%m-%Y-%H-%M-%S")
    tema_archivo = tema.replace(" ", "-")
    nombre = f"videos/{dia_semana}-{tema_archivo}-{fecha_hora}-video-{numero:03d}.mp4"
    
    video.write_videofile(nombre, fps=15, codec="libx264", audio=False)
    print(f"   ✅ Video guardado: {nombre}")

    for f in os.listdir("."):
        if f.startswith("temp_") and f.endswith(".jpg"):
            try:
                os.remove(f)
            except:
                pass

# ============================================
# SELECCIÓN DE TEMAS PARA LA SEMANA
# ============================================
def seleccionar_temas(opcion):
    opcion_limpia = opcion.strip().lower()
    if any(palabra in opcion_limpia for palabra in ["todo", "aleatorio", "random", "azar"]):
        temas = random.sample(TEMAS_PREDEFINIDOS, 7)
        print(f"📌 Temas seleccionados (aleatorios): {', '.join(temas)}")
        return temas
    else:
        tema_encontrado = None
        for t in TEMAS_PREDEFINIDOS:
            if t.lower() == opcion_limpia or t.lower().replace(" ", "") == opcion_limpia.replace(" ", ""):
                tema_encontrado = t
                break
        if tema_encontrado:
            print(f"📌 Usando el tema: {tema_encontrado}")
            return [tema_encontrado] * 7
        else:
            print(f"📌 Usando el tema: {opcion}")
            return [opcion] * 7

# ============================================
# EJECUCIÓN PRINCIPAL
# ============================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generador optimizado de videos")
    parser.add_argument("--videos", type=int, default=5, help="Número de videos por día")
    parser.add_argument("--tema", type=str, default="Motivación", help="Tema o 'todo'")
    parser.add_argument("--no-zip", action="store_true", help="No crear ZIP")
    args = parser.parse_args()

    videos_por_dia = args.videos
    tema_input = args.tema

    print("🎬 ¡Generador de videos optimizado!")
    print("=" * 50)
    print(f"📝 Videos por día: {videos_por_dia}")
    print(f"🎯 Temática: {tema_input}")
    print("=" * 50)

    temas_semana = seleccionar_temas(tema_input)
    DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    for dia_idx, tema in enumerate(temas_semana):
        dia_nombre = DIAS_SEMANA[dia_idx]
        print(f"\n📅 Procesando: {dia_nombre} - {tema}")
        for i in range(videos_por_dia):
            crear_video(tema, dia_nombre, i+1)
            time.sleep(0.5)

    print("\n🎉 ¡Todos los videos optimizados fueron generados con éxito!")

    if not args.no_zip:
        nombre_zip = "videos-generados.zip"
        print(f"📦 Creando ZIP: {nombre_zip} ...")
        with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk("videos"):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=file)
        print(f"✅ ZIP creado: {nombre_zip}")
