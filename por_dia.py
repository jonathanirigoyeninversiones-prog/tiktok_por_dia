
import os
import sys
import requests
import re
import random
import argparse
import textwrap
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import TextClip, CompositeVideoClip, ColorClip, AudioFileClip, ImageClip
from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout

# ==========================================
# CONFIGURACIÓN Y REGLAS DEL SISTEMA
# ==========================================
# Resolución estricta vertical
ANCHO = 1080
ALTO = 1920

# Duración estricta entre 75 y 85 segundos
DURACION_MIN = 75
DURACION_MAX = 85

# Firma corporativa fija
FIRMA_CORPORATIVA = "@jonathan_irigoyen"

# Fuente segura estándar (evita errores en Linux/GitHub Actions)
FUENTES_DISPONIBLES = ["DejaVuSans.ttf", "arial.ttf"]

def obtener_fuente(tamanio=50):
    for fuente in FUENTES_DISPONIBLES:
        try:
            return ImageFont.truetype(fuente, tamanio)
        except IOError:
            continue
    return ImageFont.load_default()

# ==========================================
# ESTRUCTURA DE CONTENIDO Y GANCHO DINÁMICO
# ==========================================
# Ajuste enfocado en el gancho de la primera imagen y el primer párrafo
GANCHO_INICIAL = "ATENCION: Lo que estas a punto de ver cambiara tu forma de entender este proceso para siempre."
PREGUNTA_RETADORA = "Te has preguntado por que la mayoria falla exactamente en este punto sin saberlo?"

CUERPO_VALOR = [
    "El secreto principal radica en la constancia y en la ejecucion exacta de cada paso diario.",
    "Muchos ignoran las reglas basicas del sistema y terminan perdiendo tiempo valioso.",
    "La automatizacion inteligente permite escalar resultados sin depender de esfuerzos manuales constantes.",
    "Cada detalle cuenta cuando el objetivo es mantener la retencion alta de principio a fin.",
    "Analizar los errores comunes evita tropiezos innecesarios en el camino hacia la meta."
]

CTA_FINAL = "Guarda este video y ponlo en practica ahora mismo."

def generar_texto_seguro(texto):
    """Elimina emojis y caracteres especiales para evitar cuadros rotos (□)."""
    return re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s,.;¿?¡!]', '', texto)

# ==========================================
# DESCARGA DE RECURSOS (PEXELS API)
# ==========================================
def obtener_fondo_pexels(query="technology background"):
    """Descarga un fondo multimedia vertical desde Pexels."""
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1&orientation=portrait"
    headers = {"Authorization": "TU_API_KEY_DE_PEXELS"} # Reemplazar con clave o variable de entorno
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("photos"):
                img_url = data["photos"][0]["src"]["large2x"]
                img_data = requests.get(img_url).content
                archivo_temp = "fondo_temp.jpg"
                with open(archivo_temp, "wb") as f:
                    f.write(img_data)
                return archivo_temp
    except Exception:
        pass
    
    # Fondo de respaldo plano si falla la API
    respaldo = Image.new("RGB", (ANCHO, ALTO), color=(20, 20, 20))
    respaldo.save("fondo_temp.jpg")
    return "fondo_temp.jpg"

# ==========================================
# PROCESAMIENTO DE VIDEO (MOVIEPY)
# ==========================================
def construir_video():
    print("[INFO] Iniciando generador automatizado de video...")
    
    # 1. Duración total controlada (entre 75 y 85 segundos)
    duracion_total = random.randint(DURACION_MIN, DURACION_MAX)
    
    # 2. Obtener recurso visual optimizado para el gancho inicial
    path_fondo = obtener_fondo_pexels("dark minimalist abstract")
    
    # Crear clip base con la primera imagen del gancho
    clip_fondo = ImageClip(path_fondo).set_duration(duracion_total)
    clip_fondo = clip_fondo.resize(height=ALTO)
    
    # Recorte central para mantener resolución 1080x1920 exacta
    if clip_fondo.w > ANCHO:
        x_center = (clip_fondo.w - ANCHO) / 2
        clip_fondo = clip_fondo.crop(x1=x_center, y1=0, x2=x_center + ANCHO, y2=ALTO)
    
    clips_texto = []
    
    # 3. Estructura de textos por bloques de tiempo
    # Bloque 1: Gancho Inicial (Primer párrafo e imagen de impacto)
    texto_gancho = generar_texto_seguro(GANCHO_INICIAL)
    txt_clip_1 = TextClip(texto_gancho, fontsize=60, color='white', font='Arial', 
                          size=(ANCHO - 150, None), method='caption', align='center')
    txt_clip_1 = txt_clip_1.set_position('center').set_duration(10).set_start(0)
    clips_texto.append(txt_clip_1)
    
    # Bloque 2: Pregunta Retadora
    texto_pregunta = generar_texto_seguro(PREGUNTA_RETADORA)
    txt_clip_2 = TextClip(texto_pregunta, fontsize=55, color='yellow', font='Arial', 
                          size=(ANCHO - 150, None), method='caption', align='center')
    txt_clip_2 = txt_clip_2.set_position('center').set_duration(12).set_start(10)
    clips_texto.append(txt_clip_2)
    
    # Bloque 3: Cuerpo de valor (distribuido en el tiempo restante antes del CTA)
    tiempo_acumulado = 22
    duracion_por_frase = (duracion_total - 22 - 10) / len(CUERPO_VALOR)
    
    for frase in CUERPO_VALOR:
        texto_limpio = generar_texto_seguro(frase)
        c_clip = TextClip(texto_limpio, fontsize=50, color='white', font='Arial', 
                          size=(ANCHO - 150, None), method='caption', align='center')
        c_clip = c_clip.set_position('center').set_duration(duracion_por_duracion := duracion_por_frase).set_start(tiempo_acumulado)
        clips_texto.append(c_clip)
        tiempo_acumulado += duracion_por_frase

    # Bloque 4: Llamado a la Acción (CTA) Final
    texto_cta = generar_texto_seguro(CTA_FINAL)
    txt_clip_cta = TextClip(texto_cta, fontsize=60, color='cyan', font='Arial', 
                            size=(ANCHO - 150, None), method='caption', align='center')
    txt_clip_cta = txt_clip_cta.set_position('center').set_duration(10).set_start(duracion_total - 10)
    clips_texto.append(txt_clip_cta)

    # Firma corporativa fija durante todo el video
    txt_firma = TextClip(FIRMA_CORPORATIVA, fontsize=35, color='gray', font='Arial')
    txt_firma = txt_firma.set_position(('center', ALTO - 100)).set_duration(duracion_total)
    clips_texto.append(txt_firma)

    # 4. Renderizado final del video compuesto
    video_final = CompositeVideoClip([clip_fondo] + clips_texto, size=(ANCHO, ALTO))
    video_final = video_final.set_duration(duracion_total)
    
    nombre_salida = f"video_viral_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    
    print( f"[INFO] Renderizando video con duracion de {duracion_total} segundos...")
    video_final.write_videofile(
        nombre_salida,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        preset='medium',
        threads=4
    )
    
    # Limpieza de archivos temporales
    if os.path.exists("fondo_temp.jpg"):
        os.remove("fondo_temp.jpg")
        
    print(f"[EXITO] Video generado correctamente: {nombre_salida}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generador automatizado de videos verticales.")
    parser.parse_args()
    construir_video()
