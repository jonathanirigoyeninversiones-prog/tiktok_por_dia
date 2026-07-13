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
from moviepy.video.fx import slide_in, fadein
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
 
