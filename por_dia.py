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
# CONFIGURACIÓN INICIAL Y AMBIENTE
# ============================================
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

CLAVE_PEXELS = os.getenv("PEXELS_API_KEY")

if not CLAVE_PEXELS:
    print("[ERROR] Falta la clave de Pexels.")
    print("Asegúrate de configurar PEXELS_API_KEY como secreto en GitHub.")
    sys.exit(1)

# ============================================
# MATRICES ORIGINALES (20 TEMAS, SUJETOS, VERBOS Y PREDICADOS)
# ============================================
TEMAS_PREDEFINIDOS = [
    "Motivación", "Constancia", "Superación", "Gratitud", "Logros",
    "Amor Propio", "Esperanza", "Confianza", "Resiliencia", "Felicidad",
    "Propósito", "Optimismo", "Paz", "Actitud", "Crecimiento",
    "Cambio", "Libertad", "Aprendizaje", "Sabiduría", "Conexión"
]

SUJETOS = [
    "Tu mente", "El éxito", "Cada pequeño esfuerzo", "La disciplina", "Tu actitud",
    "El camino difícil", "La constancia", "Un hábito diario", "Tu enfoque", "La paciencia",
    "El verdadero poder", "Tu potencial oculto", "La resiliencia", "Cada decisión", "El coraje",
    "La energía positiva", "Tu visión", "La determinación", "El compromiso", "La sabiduría"
]

VERBOS = [
    "transforma", "construye", "impulsa", "revela", "fortalece",
    "desbloquea", "genera", "multiplica", "destruye", "activa",
    "define", "programa", "cataliza", "potencia", "eleva",
    "equilibra", "garantiza", "materializa", "corona", "inspira"
]

PREDICADOS = [
    "el futuro que deseas alcanzar sin mirar atrás.",
    "los obstáculos que otros consideran imposibles de superar.",
    "una realidad completamente nueva basada en tus metas.",
    "la confianza interna que te hace totalmente imparable.",
    "el camino correcto hacia tus mayores aspiraciones.",
    "resultados extraordinarios cuando nadie más cree en ti.",
    "la versión más fuerte y segura de ti mismo hoy.",
    "oportunidades ocultas detrás de cada desafío diario.",
    "un escudo impenetrable contra cualquier tipo de duda.",
    "la claridad mental necesaria para dominar cualquier reto.",
    "un progreso imparable que acelera tu evolución.",
    "la paz interior que sostiene tus grandes victorias.",
    "un ciclo constante de crecimiento y evolución personal.",
    "la llave maestra para abrir puertas que parecían cerradas.",
    "la disciplina exacta que separa el sueño de la realidad.",
    "una energía inagotable para conquistar tus propósitos.",
    "el magnetismo necesario para atraer el éxito absoluto.",
    "una transformación profunda que se nota desde el primer día.",
    "la maestría necesaria para liderar tu propio destino.",
    "un impacto duradero en todo lo que te propones hacer."
]

# ============================================
# GANCHOS DE ALTO IMPACTO (SIN EMOJIS)
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

PREGUNTAS_RETADORAS = [
    "Te has preguntado por que la mayoria falla exactamente en este punto sin saberlo?",
    "Realmente estas dispuesto a hacer lo necesario para transformar tu realidad hoy?",
    "Cuanto tiempo mas vas a postergar lo que sabes que debes hacer?",
    "Por que insistes en cometer el mismo error una y otra vez?",
    "Estas viviendo la vida que deseas o solo la que te toco aceptar?"
]

# ============================================
# FUNCIONES AUXILIARES BLINDADAS
# ============================================
def limpiar_texto(texto):
    return re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s,.;¿?¡!]', '', texto)

def obtener_fondo_pexels(query):
    print(f"[PEXELS] Consultando imagen para: {query}")
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1&orientation=portrait"
    headers = {"Authorization": CLAVE_PEXELS}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("photos"):
                img_url = data["photos"][0]["src"]["large2x"]
                img_data = requests.get(img_url, timeout=5).content
                archivo_temp = f"fondo_{random.randint(1000,9999)}.jpg"
                with open(archivo_temp, "wb") as f:
                    f.write(img_data)
                print("[PEXELS] Fondo descargado correctamente.")
                return archivo_temp
    except Exception as e:
        print(f"[AVISO] Pexels no respondió a tiempo ({e}). Usando respaldo local.")
    
    respaldo = Image.new("RGB", (1080, 1920), color=(25, 25, 25))
    archivo_temp = f"fondo_{random.randint(1000,9999)}.jpg"
    respaldo.save(archivo_temp)
    return archivo_temp

def seleccionar_temas(tema_input):
    if tema_input.lower() in ["todo", "aleatorio"]:
        temas_disponibles = list(TEMAS_PREDEFINIDOS)
        random.shuffle(temas_disponibles)
        return temas_disponibles[:7]
    else:
        tema_encontrado = None
        for t in TEMAS_PREDEFINIDOS:
            if t.lower() == tema_input.lower():
                tema_encontrado = t
                break
        if tema_encontrado:
            return [tema_encontrado] * 7
        else:
            print(f"[AVISO] Tema '{tema_input}' no encontrado. Usando aleatorios.")
            temas_disponibles = list(TEMAS_PREDEFINIDOS)
            random.shuffle(temas_disponibles)
            return temas_disponibles[:7]

def generar_frases_dinamicas(cantidad=5):
    frases = []
    for _ in range(cantidad):
        s = random.choice(SUJETOS)
        v = random.choice(VERBOS)
        p = random.choice(PREDICADOS)
        frase = f"{s} {v} {p}"
        frases.append(frase)
    return frases

# ============================================
# CREACIÓN DE VIDEO INDIVIDUAL
# ============================================
def crear_video(tema, dia_nombre, indice_video):
    print(f"\n[PROCESO] Iniciando video {indice_video} para {dia_nombre} (Tema: {tema})...")
    sys.stdout.flush()
    
    ancho, alto = 1080, 1920
    duracion_total = random.randint(75, 85)
    
    path_fondo = obtener_fondo_pexels(f"{tema} background vertical")
    
    try:
        img_pil = Image.open(path_fondo)
        img_pil = img_pil.resize((ancho, alto), Image.Resampling.LANCZOS)
        img_pil = img_pil.filter(ImageFilter.GaussianBlur(radius=8))
        
        path_fondo_procesado = f"fondo_proc_{random.randint(1000,9999)}.jpg"
        img_pil.save(path_fondo_procesado)
        
        clips_secuencia = []
        
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 60)
            font_firma = ImageFont.truetype("DejaVuSans.ttf", 35)
        except IOError:
            font = ImageFont.load_default()
            font_firma = ImageFont.load_default()
            
        # 1. GANCHO INICIAL (Duración orgánica aleatoria entre 3 y 4 segundos)
        duracion_gancho = round(random.uniform(3.0, 4.0), 2)
        gancho_texto = limpiar_texto(random.choice(GANCHOS_INICIALES))
        img_gancho = img_pil.copy()
        draw_g = ImageDraw.Draw(img_gancho)
        wrapped_gancho = textwrap.fill(gancho_texto, width=25)
        draw_g.multiline_text((ancho/2, alto/2), wrapped_gancho, font=font, fill="white", align="center", anchor="mm")
        
        path_gancho_img = f"temp_gancho_{random.randint(1000,9999)}.png"
        img_gancho.save(path_gancho_img)
        clips_secuencia.append(ImageClip(path_gancho_img).set_duration(duracion_gancho))
        
        # 2. PREGUNTA RETADORA (Duración orgánica aleatoria entre 3 y 4 segundos)
        duracion_pregunta = round(random.uniform(3.0, 4.0), 2)
        pregunta_texto = limpiar_texto(random.choice(PREGUNTAS_RETADORAS))
        img_pregunta = img_pil.copy()
        draw_p = ImageDraw.Draw(img_pregunta)
        wrapped_pregunta = textwrap.fill(pregunta_texto, width=25)
        draw_p.multiline_text((ancho/2, alto/2), wrapped_pregunta, font=font, fill="yellow", align="center", anchor="mm")
        
        path_pregunta_img = f"temp_pregunta_{random.randint(1000,9999)}.png"
        img_pregunta.save(path_pregunta_img)
        clips_secuencia.append(ImageClip(path_pregunta_img).set_duration(duracion_pregunta))
        
        # 3. CUERPO DE VALOR DINÁMICO (Sujetos + Verbos + Predicados)
        tiempo_fijo_cabecera = duracion_gancho + duracion_pregunta
        tiempo_cta = 10.0
        tiempo_restante = duracion_total - tiempo_fijo_cabecera - tiempo_cta
        
        frases_seleccionadas = generar_frases_dinamicas(5)
        duracion_por_frase = max(5, tiempo_restante / len(frases_seleccionadas))
        
        for frase in frases_seleccionadas:
            img_frase = img_pil.copy()
            draw_f = ImageDraw.Draw(img_frase)
            wrapped_frase = textwrap.fill(limpiar_texto(frase), width=28)
            draw_f.multiline_text((ancho/2, alto/2), wrapped_frase, font=font, fill="white", align="center", anchor="mm")
            
            draw_f.text((ancho/2, alto - 120), "@jonathan_irigoyen", font=font_firma, fill="gray", anchor="mm")
            
            path_f_img = f"temp_frase_{random.randint(1000,9999)}.png"
            img_frase.save(path_f_img)
            clips_secuencia.append(ImageClip(path_f_img).set_duration(duracion_por_frase))
            
            if os.path.exists(path_f_img):
                os.remove(path_f_img)
                
        # 4. LLAMADO A LA ACCIÓN (CTA) FINAL
        img_cta = img_pil.copy()
        draw_c = ImageDraw.Draw(img_cta)
        cta_texto = limpiar_texto("Guarda este video y ponlo en practica ahora mismo.")
        wrapped_cta = textwrap.fill(cta_texto, width=25)
        draw_c.multiline_text((ancho/2, alto/2), wrapped_cta, font=font, fill="cyan", align="center", anchor="mm")
        
        path_cta_img = f"temp_cta_{random.randint(1000,9999)}.png"
        img_cta.save(path_cta_img)
        clips_secuencia.append(ImageClip(path_cta_img).set_duration(tiempo_cta))
        
        video_final = concatenate_videoclips(clips_secuencia, method="compose")
        
        os.makedirs("videos_salida", exist_ok=True)
        nombre_salida = f"videos_salida/video_{dia_nombre.lower()}_{indice_video}_{int(time.time())}.mp4"
        
        print(f"[RENDER] Renderizando video con duración de {video_final.duration:.2f} segundos...")
        sys.stdout.flush()
        
        video_final.write_videofile(
            nombre_salida,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            preset='ultrafast',
            threads=2,
            logger=None
        )
        
        print(f"[EXITO] Video generado con éxito: {nombre_salida}")
        sys.stdout.flush()
        
    except Exception as e:
        print(f"[ERROR CRÍTICO] Ocurrió un error al generar el video: {e}")
        sys.stdout.flush()
    finally:
        if os.path.exists(path_fondo):
            os.remove(path_fondo)
        if 'path_fondo_procesado' in locals() and os.path.exists(path_fondo_procesado):
            os.remove(path_fondo_procesado)
        if 'path_gancho_img' in locals() and os.path.exists(path_gancho_img):
            os.remove(path_gancho_img)
        if 'path_pregunta_img' in locals() and os.path.exists(path_pregunta_img):
            os.remove(path_pregunta_img)
        if 'path_cta_img' in locals() and os.path.exists(path_cta_img):
            os.remove(path_cta_img)

# ============================================
# FUNCIÓN PRINCIPAL Y EJECUCIÓN
# ============================================
if __name__ == "__main__":
    print("[INICIO] Script configurado correctamente. Analizando argumentos...")
    sys.stdout.flush()
    
    parser = argparse.ArgumentParser(description="Generador automatizado de videos por día.")
    parser.add_argument("--videos", type=int, default=5, help="Número de videos por día")
    parser.add_argument("--tema", type=str, default="todo", help="Tema específico o 'todo'/'aleatorio' para aleatorio")
    parser.add_argument("--no-zip", action="store_true", help="No crear archivo ZIP al final")
    args = parser.parse_args()

    videos_por_dia = args.videos
    tema_input = args.tema

    print("🎬 ¡Generador de videos para toda la semana!")
    print("=" * 50)
    print(f"📝 Videos por día: {videos_por_dia} (por defecto: 5)")
    print(f"🎯 Temática: {tema_input} (soporta 'todo' y 'aleatorio')")
    print("=" * 50)

    temas_semana = seleccionar_temas(tema_input)
    DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    print(f"\n📝 Generando {videos_por_dia} videos por cada día de la semana")
    print(f"📊 Total estimado: {videos_por_dia * 7} videos")
    print("=" * 50)
    sys.stdout.flush()

    for dia_idx, tema in enumerate(temas_semana):
        dia_nombre = DIAS_SEMANA[dia_idx]
        print(f"\n📅 Procesando: {dia_nombre} - {tema}")
        sys.stdout.flush()

        for i in range(videos_por_dia):
            crear_video(tema, dia_nombre, i+1)
            time.sleep(0.5)

    print("\n🎉 ¡Todos los videos generados correctamente!")
    sys.stdout.flush()

    if not args.no_zip:
        nombre_zip = f"videos_generados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        print(f"📦 Comprimiendo videos en {nombre_zip}...")
        sys.stdout.flush()
        
        with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.exists("videos_salida"):
                for root, dirs, files in os.walk("videos_salida"):
                    for file in files:
                        zipf.write(os.path.join(root, file), file)
                        
        print(f"[EXITO] Archivo ZIP creado y listo: {nombre_zip}")
        sys.stdout.flush()
