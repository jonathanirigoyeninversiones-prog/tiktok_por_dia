# -*- coding: utf-8 -*-
import os
import sys
import requests
import re
import random
import argparse
import textwrap
import zipfile
import time  # <--- ESTO FALTABA
from datetime import datetime, timezone, timedelta
from moviepy.editor import ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

# ============================================
# CONFIGURACIÓN
# ============================================
CLAVE_PEXELS = os.getenv("PEXELS_API_KEY")

if not CLAVE_PEXELS:
    print("ERROR: Falta la clave de Pexels.")
    print("Asegúrate de configurar PEXELS_API_KEY como secreto en GitHub.")
    sys.exit(1)

# ============================================
# TEMAS Y FRASES (solo 1 tema para prueba)
# ============================================
TEMAS = ["Motivacion"]
FRASES = {
    "Motivacion": [
        "La motivación te da energía para empezar cada día.",
        "Tu entusiasmo contagia a los que te rodean.",
        "La fe en ti mismo abre puertas cerradas.",
        "El coraje te ayuda a enfrentar los miedos.",
        "La determinación te lleva a alcanzar metas lejanas.",
        "La disciplina convierte los sueños en hábitos.",
        "La resiliencia te enseña a levantarte después de caer.",
        "La voluntad te permite seguir cuando todo se complica.",
        "El impulso inicial es el paso más importante.",
        "La constancia transforma pequeños esfuerzos en grandes logros."
    ]
}

def generar_pregunta(tema):
    preguntas = [
        f"¿Alguna vez has reflexionado sobre la importancia de {tema.lower()} en tu vida?",
        f"¿Qué significa para ti {tema.lower()} en tu día a día?",
        f"¿Cómo aplicas {tema.lower()} en las situaciones difíciles?",
        f"¿Crees que {tema.lower()} puede cambiar tu forma de ver las cosas?",
        f"¿Qué consejo le darías a alguien sobre {tema.lower()}?"
    ]
    return random.choice(preguntas)

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
    parrafos.append("¿Qué piensas? Te leo en los comentarios")
    
    while len(parrafos) < num_parrafos:
        parrafos.insert(-1, "Sigue adelante con fe y determinación.")
    while len(parrafos) > num_parrafos:
        parrafos.pop(-2)
    
    return parrafos

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

def crear_video(tema, dia_semana, numero):
    num_parrafos = random.choice([6, 7, 8])
    duracion_total = random.uniform(70, 85)
    duracion_por_parrafo = duracion_total / num_parrafos
    duraciones = [duracion_por_parrafo] * num_parrafos

    print(f"   🎬 Video {numero} ({dia_semana} - {tema}) - {num_parrafos} párrafos, {duracion_total:.1f}s")
    print(f"   ⏱️  Cada párrafo: {duracion_por_parrafo:.1f}s")
    os.makedirs("videos", exist_ok=True)

    pregunta = generar_pregunta(tema)
    frases = random.sample(FRASES[tema], min(8, len(FRASES[tema])))
    parrafos = dividir_en_parrafos(pregunta, frases, num_parrafos)

    query = tema.lower()
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
            img = Image.new("RGB", (1080, 1920), color=(50, 50, 50))
        
        img = img.resize((1080, 1920))
        draw = ImageDraw.Draw(img)

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

        y = y_inicio
        for linea in lineas:
            bbox = draw.textbbox((0, 0), linea, font=font)
            ancho_linea = bbox[2] - bbox[0]
            x = (1080 - ancho_linea) // 2
            draw.text((x, y), linea, font=font, fill='white', stroke_width=5, stroke_fill='black')
            y += font_size * 1.3

        # FIRMA
        firma = "@jonathan_irigoyen"
        try:
            font_firma = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
        except:
            try:
                font_firma = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 30)
            except:
                font_firma = ImageFont.load_default()
        margen = 20
        draw.text((margen, margen), firma, font=font_firma, fill='white', stroke_width=2, stroke_fill='black')

        img.save(f"temp_texto_{i}.jpg", "JPEG")
        clip = ImageClip(f"temp_texto_{i}.jpg", duration=duraciones[i])
        clips.append(clip)

        try:
            os.remove(f"temp_fondo_{i}.jpg")
        except:
            pass

    video = concatenate_videoclips(clips, method="compose")

    tz_venezuela = timezone(timedelta(hours=-4))
    ahora = datetime.now(tz_venezuela)
    fecha_hora = ahora.strftime("%d-%m-%Y-%H-%M-%S")
    nombre = f"videos/{dia_semana}-{tema}-{fecha_hora}-video-{numero:03d}.mp4"
    video.write_videofile(nombre, fps=15, codec="libx264", audio=False)
    print(f"   ✅ Video guardado: {nombre}")

    for f in os.listdir("."):
        if f.startswith("temp_") and f.endswith(".jpg"):
            try:
                os.remove(f)
            except:
                pass

# ============================================
# EJECUCIÓN PRINCIPAL
# ============================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--videos", type=int, default=1, help="Videos por día")
    parser.add_argument("--tema", type=str, default="Motivacion", help="Tema")
    parser.add_argument("--no-zip", action="store_true", help="No crear ZIP")
    args = parser.parse_args()

    print("🎬 ¡Generador de videos (versión estable)!")
    print("=" * 50)
    print(f"📝 Videos a generar: {args.videos}")
    print(f"🎯 Tema: {args.tema}")
    print("=" * 50)

    for i in range(args.videos):
        crear_video(args.tema, "Lunes", i+1)
        time.sleep(0.5)  # <--- AHORA time ESTÁ DEFINIDO

    print("\n🎉 ¡Todos los videos generados!")

    if not args.no_zip:
        nombre_zip = "videos-generados.zip"
        print(f"📦 Creando ZIP: {nombre_zip} ...")
        with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk("videos"):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=os.path.join("videos", file))
        print(f"✅ ZIP creado: {nombre_zip}")
        print(f"📁 Revisa la carpeta 'videos' y el archivo '{nombre_zip}'.")
    else:
        print("⏭️  No se creó ZIP (opción --no-zip activada).")
