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
    "Motivación",
    "Constancia",
    "Superación",
    "Gratitud",
    "Logros",
    "Amor Propio",
    "Esperanza",
    "Confianza",
    "Resiliencia",
    "Felicidad",
    "Propósito",
    "Optimismo",
    "Paz",
    "Actitud",
    "Crecimiento",
    "Cambio",
    "Libertad",
    "Aprendizaje",
    "Sabiduría",
    "Conexión"
]

# ============================================
# GANCHOS DE ALTO IMPACTO (SIN EMOJIS PARA EVITAR ERRORES VISUALES)
# ============================================
GANCHOS_INICIALES = [
    "Escucha esto antes de que termine tu día...",
    "Lo que nadie te cuenta sobre este tema...",
    "Si necesitas un cambio real, quédate hasta el final.",
    "Detente un segundo y presta mucha atención a esto.",
    "Esto va a cambiar tu perspectiva por completo hoy.",
    "El secreto que pocos entienden y todos buscan.",
    "Abre los ojos y mira lo que estás ignorando.",
    "Nadie te advierte sobre esto hasta que es muy tarde.",
    "Si te sientes estancado, este mensaje es para ti.",
    "El error que todos cometen y tú puedes evitar.",
    "Presta atención porque esto romperá tus esquemas mentales.",
    "La verdad que necesitas escuchar ahora mismo.",
    "Si quieres avanzar, tienes que entender esto primero.",
    "Pausa lo que estás haciendo y escucha con atención.",
    "Esto es exactamente lo que te faltaba por saber.",
    "Hay algo muy importante que estás pasando por alto.",
    "Escucha con atención si realmente quieres evolucionar.",
    "El detalle clave que cambiará tu forma de ver las cosas.",
    "Nadie habla de esto, pero deberías saberlo ya.",
    "Prepárate porque esta perspectiva lo va a transformar todo."
]

# ============================================
# FRASES PARA CADA TEMA (con las claves actualizadas)
# ============================================
FRASES_POR_TEMA = {
    "Motivación": [
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
    "Superación": [
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
    "Amor Propio": [
        "Amarte a ti mismo es el primer amor verdadero.",
        "Aceptarte es el primer paso hacia la felicidad plena.",
        "Cuidarte te da la fuerza para cuidar de los demás.",
        "Perdonarte te permite seguir adelante sin culpas.",
        "Confiar en ti mismo es el cimiento de todo logro.",
        "Respetarte a ti mismo es la base de todas las relaciones.",
        "Valorar tu esencia te hace invulnerable a las críticas.",
        "Escuchar tu intuición es un acto de profundo amor propio.",
        "Darte tiempo para sanar es prioridad absoluta.",
        "Tu bienestar emocional no es negociable bajo ninguna circunstancia."
    ],
    "Esperanza": [
        "La esperanza enciende una luz en medio de la oscuridad.",
        "Confiar en el mañana te da fuerzas para hoy.",
        "La ilusión es el motor que impulsa nuevos comienzos.",
        "Creer que lo mejor está por venir transforma tu realidad.",
        "La expectativa positiva atrae resultados favorables.",
        "Mantener viva la esperanza es un acto de valentía.",
        "Cada amanecer trae una nueva oportunidad para empezar.",
        "El optimismo nutre el alma y aclara la mente.",
        "La fe en el futuro disipa la incertidumbre del presente.",
        "Soñar despierto es el primer paso para materializar tus deseos."
    ],
    "Confianza": [
        "La confianza en ti mismo es tu mejor carta de presentación.",
        "Creer en tus capacidades abre cualquier puerta.",
        "La seguridad interna ahuyenta los miedos más intensos.",
        "Tener fe en tus decisiones te hace imparable.",
        "La convicción firme es la base del éxito seguro.",
        "Saber quién eres te da un poder incalculable.",
        "La autoconfianza se entrena con cada pequeño reto superado.",
        "Caminar con seguridad cambia la forma en que el mundo te mira.",
        "Tu potencial no tiene límites cuando confías en tu talento.",
        "La certeza en tus pasos ilumina todo el trayecto."
    ],
    "Resiliencia": [
        "La resiliencia te vuelve más fuerte ante la adversidad.",
        "Doblarte sin romperte es el arte de sobrevivir con gracia.",
        "Las tormentas pasan y tu capacidad de resistencia permanece.",
        "Cada golpe recibido te enseña a construir un escudo mejor.",
        "La dureza del camino solo demuestra tu enorme capacidad.",
        "Reinventarte tras un fracaso es tu mayor superpoder.",
        "El dolor se transforma en sabiduría con el paso del tiempo.",
        "Soportar la presión es el proceso para convertirte en diamante.",
        "Ninguna herida es permanente cuando decides sanar.",
        "Tu capacidad de recuperación asombrará a todos los que dudaron."
    ],
    "Felicidad": [
        "La felicidad se encuentra en los detalles más pequeños del día.",
        "Sonreír sin motivo es el reflejo de un alma en paz.",
        "Disfrutar el presente es la clave para una vida plena.",
        "La alegría genuina no depende de lo externo, sino de ti.",
        "Compartir tu bienestar multiplica los momentos felices.",
        "Apreciar lo cotidiano convierte la rutina en magia.",
        "La ligereza del corazón atrae experiencias maravillosas.",
        "Estar en paz contigo mismo es la cima de la felicidad.",
        "Cada risa sincera alimenta tu espíritu de manera única.",
        "Elegir ser feliz es la decisión más sabiza que puedes tomar."
    ],
    "Propósito": [
        "Tener un propósito claro le da sentido a cada esfuerzo.",
        "Conocer tu misión en la vida alinea todas tus acciones.",
        "El sentido de dirección te ahorra años de caminar a ciegas.",
        "Seguir tu vocación es la forma más honesta de vivir.",
        "Tus metas deben estar conectadas con tu razón de ser.",
        "El enfoque en tu propósito disipa cualquier distracción.",
        "Saber por qué luchas hace que cualquier sacrificio valga la pena.",
        "El destino se construye cuando caminas con una intención firme.",
        "Tu legado se escribe con cada paso guiado por tu propósito.",
        "La claridad en tus objetivos te convierte en una fuerza imparable."
    ],
    "Optimismo": [
        "Ver el lado positivo de las cosas multiplica tus oportunidades.",
        "Una sonrisa sincera atrae energías extraordinarias.",
        "El vaso medio lleno es suficiente para saciar tu sed.",
        "Pensar en positivo es elegir vivir con ligereza y paz.",
        "La actitud optimista disipa las nubes más grises del día.",
        "Esperar lo mejor te prepara para recibir lo extraordinario.",
        "La alegría de vivir se contagia con una mirada luminosa.",
        "Encontrar belleza en el caos es un don que se cultiva.",
        "La esperanza activa transforma los problemas en soluciones.",
        "Cada día es una nueva oportunidad para sonreírle al mundo."
    ],
    "Paz": [
        "La paz interior es el refugio que nadie te puede quitar.",
        "Soltar el control te regala la calma que tanto buscas.",
        "El silencio de la mente es el inicio de la verdadera sabiduría.",
        "Elegir la tranquilidad por encima de la discusión es madurez.",
        "Un suspiro profundo puede ordenar todos tus pensamientos.",
        "La armonía en tu entorno empieza por la calma en tu alma.",
        "Alejarte del ruido innecesario te devuelve el centro.",
        "La serenidad es la armadura más fuerte frente al caos externo.",
        "Respirar con consciencia te reconecta con tu esencia pura.",
        "La paz no es ausencia de problemas, sino control interno."
    ],
    "Actitud": [
        "Tu actitud determina la altitud de tus mayores logros.",
        "Una mente abierta convierte cualquier tropiezo en aprendizaje.",
        "La disposición positiva abre caminos donde antes habías muros.",
        "Responder con elegancia a los problemas define tu gran valor.",
        "La energía que proyectas es la misma que regresa a ti.",
        "Tomar la iniciativa cambia por completo el rumbo de tu día.",
        "Una sonrisa ante la adversidad desarma cualquier conflicto.",
        "Tu perspectiva es el filtro que colorea toda tu realidad.",
        "Elegir buena actitud es un hábito que transforma tu destino.",
        "El entusiasmo es la chispa que enciende cualquier proyecto."
    ],
    "Crecimiento": [
        "El crecimiento personal requiere paciencia, amor y constancia.",
        "Aprender de tus propios errores acelera tu evolución.",
        "Expandir tus horizontes te permite ver el mundo distinto.",
        "Invertir tiempo en ti mismo es la decisión más rentable.",
        "La evolución constante deja atrás versiones que ya no te sirven.",
        "Cultivar tu mente es asegurar un futuro lleno de éxito.",
        "Cada paso fuera de tu zona de confort es crecimiento puro.",
        "La madurez llega cuando aceptas que todo cambia y fluye.",
        "Sembrar buenos hábitos hoy garantiza cosechar bienestar mañana.",
        "El deseo de superación es la brújula de tu desarrollo."
    ],
    "Cambio": [
        "Aceptar el cambio es la única forma de fluir con la vida.",
        "Lo que hoy parece un final es solo el inicio de otra etapa.",
        "Transformar tus costumbres rediseña tu camino por completo.",
        "Renovarse es vital para no quedarse estancado en el pasado.",
        "El miedo al cambio desaparece cuando descubres tu potencial.",
        "Dejar ir lo viejo abre espacio para recibir lo maravilloso.",
        "Cada transformación interna se refleja en tu entorno exterior.",
        "Adaptarte con rapidez a las nuevas circunstancias es un arte.",
        "El ciclo de la vida exige que evolucionemos sin temor.",
        "Dar el salto hacia lo desconocido es el acto más valiente."
    ],
    "Libertad": [
        "La verdadera libertad nace cuando te liberas del que dirán.",
        "Tomar tus propias decisiones es el mayor signo de madurez.",
        "Vivir sin ataduras te permite volar hacia tus metas.",
        "La independencia emocional es el regalo más valioso.",
        "Romper con las expectativas ajenas te devuelve tu autenticidad.",
        "Elegir tu propio camino es un derecho que debes ejercer.",
        "La mente libre de prejuicios encuentra soluciones donde otros ven muros.",
        "Ser fiel a tus principios te otorga una paz inquebrantable.",
        "Soltar las cargas del pasado te devuelve la ligereza para volar.",
        "Tu autonomía es el pilar fundamental de tu felicidad."
    ],
    "Aprendizaje": [
        "Cada experiencia vivida te deja una lección invaluable.",
        "Aprender algo nuevo cada día mantiene tu mente joven y activa.",
        "La curiosidad insaciable es el motor de los grandes genios.",
        "Equivocarse es solo la evidencia de que lo estás intentando.",
        "El conocimiento adquirido es un tesoro que nadie te puede quitar.",
        "Escuchar con atención te enseña más que hablar sin parar.",
        "La humildad de aprender siempre te llevará a la cima.",
        "Estudiar tu propio camino te da claridad para el futuro.",
        "La sabiduría se cultiva con paciencia, lectura y reflexión.",
        "Abrir tu mente a nuevas ideas es expandir tus propios límites."
    ],
    "Sabiduría": [
        "La sabiduría se manifiesta cuando hablas menos y observas más.",
        "Entender el tiempo de las cosas te da una ventaja única.",
        "El silencio prudente vale más que mil palabras vacías.",
        "La experiencia acumulada es la mejor guía para el presente.",
        "Saber cuándo retirarse es también una forma de ganar.",
        "La calma ante la crisis es la marca de la verdadera sabiduría.",
        "Comprender las diferencias te hace más tolerante y sabio.",
        "La reflexión constante ilumina las decisiones más difíciles.",
        "Aceptar lo que no puedes cambiar es un acto de gran lucidez.",
        "La madurez mental te permite ver el panorama completo."
    ],
    "Conexión": [
        "Conectar con otros seres humanos enriquece profundamente tu alma.",
        "La empatía es el puente que une dos corazones distintos.",
        "Escuchar con el corazón crea vínculos que duran para siempre.",
        "Sentir la energía de quienes te rodean te hace más empático.",
        "La verdadera unión se basa en el respeto y el cariño sincero.",
        "Compartir tus vivencias genera una cercanía inigualable.",
        "El amor y la amistad son los hilos que sostienen el mundo.",
        "Mirar a los ojos es conectar con la esencia del otro.",
        "Rodearte de gente positiva eleva tu frecuencia espiritual.",
        "La sintonía con el universo empieza por conectar contigo mismo."
    ]
}

# ============================================
# FUNCIONES AUXILIARES
# ============================================
def limpiar_texto(texto):
    """Elimina emojis y caracteres especiales para evitar cuadros rotos (□)."""
    return re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s,.;¿?¡!]', '', texto)

def obtener_fondo_pexels(query):
    """Descarga un fondo multimedia vertical desde Pexels usando la API."""
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1&orientation=portrait"
    headers = {"Authorization": CLAVE_PEXELS}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("photos"):
                img_url = data["photos"][0]["src"]["large2x"]
                img_data = requests.get(img_url).content
                archivo_temp = f"fondo_{random.randint(1000,9999)}.jpg"
                with open(archivo_temp, "wb") as f:
                    f.write(img_data)
                return archivo_temp
    except Exception as e:
        print(f"[AVISO] Error al conectar con Pexels ({e}). Usando fondo de respaldo.")
    
    # Fondo de respaldo plano si falla la API
    respaldo = Image.new("RGB", (1080, 1920), color=(25, 25, 25))
    archivo_temp = f"fondo_{random.randint(1000,9999)}.jpg"
    respaldo.save(archivo_temp)
    return archivo_temp

def seleccionar_temas(tema_input):
    """Selecciona los temas para los 7 días de la semana."""
    if tema_input.lower() == "todo":
        temas_disponibles = list(TEMAS_PREDEFINIDOS)
        random.shuffle(temas_disponibles)
        return temas_disponibles[:7]
    else:
        # Si el usuario especifica un tema, se repite para toda la semana o se busca coincidencia
        tema_encontrado = None
        for t in TEMAS_PREDEFINIDOS:
            if t.lower() == tema_input.lower():
                tema_encontrado = t
                break
        if tema_encontrado:
            return [tema_encontrado] * 7
        else:
            print(f"[AVISO] Tema '{tema_input}' no encontrado en predefinidos. Usando aleatorios.")
            temas_disponibles = list(TEMAS_PREDEFINIDOS)
            random.shuffle(temas_disponibles)
            return temas_disponibles[:7]

# ============================================
# CREACIÓN DE VIDEO INDIVIDUAL
# ============================================
def crear_video(tema, dia_nombre, indice_video):
    print(f"\n[PROCESO] Creando video {indice_video} para {dia_nombre} (Tema: {tema})...")
    
    ancho, alto = 1080, 1920
    duracion_total = random.randint(75, 85) # Duración estricta entre 75 y 85 segundos
    
    # Obtener fondo multimedia desde Pexels relacionado con el tema
    path_fondo = obtener_fondo_pexels(f"{tema} background vertical")
    
    try:
        # Cargar imagen y aplicar desenfoque suave con PIL
        img_pil = Image.open(path_fondo)
        img_pil = img_pil.resize((ancho, alto), Image.Resampling.LANCZOS)
        img_pil = img_pil.filter(ImageFilter.GaussianBlur(radius=8))
        
        path_fondo_procesado = f"fondo_proc_{random.randint(1000,9999)}.jpg"
        img_pil.save(path_fondo_procesado)
        
        clip_fondo = ImageClip(path_fondo_procesado).set_duration(duracion_total)
        
        # Seleccionar gancho inicial único de alto impacto
        gancho_texto = limpiar_texto(random.choice(GANCHOS_INICIALES))
        
        # Obtener frases del cuerpo según el tema
        frases_disponibles = FRASES_POR_TEMA.get(tema, FRASES_POR_TEMA["Motivación"])
        frases_seleccionadas = random.sample(frases_disponibles, min(5, len(frases_disponibles)))
        
        # Estructura de textos en fotogramas estáticos con PIL para evitar desbordamientos en MoviePy
        clips_secuencia = []
        
        # 1. Gancho Inicial (Primeros 10 segundos)
        img_gancho = img_pil.copy()
        draw = ImageDraw.Draw(img_gancho)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 60)
        except IOError:
            font = ImageFont.load_default()
            
        margin = 100
        wrapped_gancho = textwrap.fill(gancho_texto, width=25)
        draw.multiline_text((ancho/2, alto/2), wrapped_gancho, font=font, fill="white", align="center", anchor="mm")
        
        path_gancho_img = f"temp_gancho_{random.randint(1000,9999)}.png"
        img_gancho.save(path_gancho_img)
        clip_gancho = ImageClip(path_gancho_img).set_duration(10)
        clips_secuencia.append(clip_gancho)
        
        # 2. Cuerpo de valor (distribuido uniformemente)
        tiempo_restante = duracion_total - 10 - 10 # Descontando gancho (10s) y CTA (10s)
        duracion_por_frase = max(5, tiempo_restante / len(frases_seleccionadas))
        
        for frase in frases_seleccionadas:
            img_frase = img_pil.copy()
            draw_f = ImageDraw.Draw(img_frase)
            wrapped_frase = textwrap.fill(limpiar_texto(frase), width=28)
            draw_f.multiline_text((ancho/2, alto/2), wrapped_frase, font=font, fill="white", align="center", anchor="mm")
            
            # Firma corporativa fija inferior
            draw_f.text((ancho/2, alto - 120), "@jonathan_irigoyen", font=ImageFont.load_default(), fill="gray", anchor="mm")
            
            path_f_img = f"temp_frase_{random.randint(1000,9999)}.png"
            img_frase.save(path_f_img)
            clip_f = ImageClip(path_f_img).set_duration(duracion_por_frase)
            clips_secuencia.append(clip_f)
            
            # Limpiar archivo temporal de frase
            if os.path.exists(path_f_img):
                os.remove(path_f_img)
                
        # 3. Llamado a la Acción (CTA) Final (Últimos 10 segundos)
        img_cta = img_pil.copy()
        draw_c = ImageDraw.Draw(img_cta)
        cta_texto = limpiar_texto("Guarda este video y ponlo en practica ahora mismo.")
        wrapped_cta = textwrap.fill(cta_texto, width=25)
        draw_c.multiline_text((ancho/2, alto/2), wrapped_cta, font=font, fill="cyan", align="center", anchor="mm")
        
        path_cta_img = f"temp_cta_{random.randint(1000,9999)}.png"
        img_cta.save(path_cta_img)
        clip_cta = ImageClip(path_cta_img).set_duration(10)
        clips_secuencia.append(clip_cta)
        
        # Concatenar todos los clips de la secuencia
        video_final = concatenate_videoclips(clips_secuencia, method="compose")
        
        # Nombre de salida optimizado
        os.makedirs("videos_salida", exist_ok=True)
        nombre_salida = f"videos_salida/video_{dia_nombre.lower()}_{indice_video}_{int(time.time())}.mp4"
        
        print(f"[INFO] Renderizando video con duración de {video_final.duration} segundos...")
        video_final.write_videofile(
            nombre_salida,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            threads=4,
            logger=None
        )
        
        print(f"[EXITO] Video generado: {nombre_salida}")
        
    except Exception as e:
        print(f"[ERROR] Ocurrió un error al generar el video: {e}")
    finally:
        # Limpieza de archivos temporales de imagen y fondo
        if os.path.exists(path_fondo):
            os.remove(path_fondo)
        if 'path_fondo_procesado' in locals() and os.path.exists(path_fondo_procesado):
            os.remove(path_fondo_procesado)
        if 'path_gancho_img' in locals() and os.path.exists(path_gancho_img):
            os.remove(path_gancho_img)
        if 'path_cta_img' in locals() and os.path.exists(path_cta_img):
            os.remove(path_cta_img)

# ============================================
# FUNCIÓN PRINCIPAL Y EJECUCIÓN
# ============================================
def main():
    parser = argparse.ArgumentParser(description="Generador automatizado de videos por día.")
    parser.add_argument("--videos", type=int, default=5, help="Número de videos por día")
    parser.add_argument("--tema", type=str, default="todo", help="Tema específico o 'todo' para aleatorio")
    parser.add_argument("--no-zip", action="store_true", help="No crear archivo ZIP al final")
    args = parser.parse_args()

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
        
        for i in range(videos_por_dia):
            crear_video(tema, dia_nombre, i+1)
            time.sleep(0.5)

    print("\n🎉 ¡Todos los videos generados con éxito!")

    if not args.no_zip:
        nombre_zip = f"videos_generados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        print(f"📦 Comprimiendo videos en {nombre_zip}...")
        with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.exists("videos_salida"):
                for root, dirs, files in os.walk("videos_salida"):
                    for file in files:
                        zipf.write(os.path.join(root, file), file)
        print(f"[EXITO] Archivo ZIP creado: {nombre_zip}")

if __name__ == "__main__":
    main()
