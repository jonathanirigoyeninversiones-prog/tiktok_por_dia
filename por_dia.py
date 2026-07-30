import os
import sys
import requests
import random
import argparse
import time
import zipfile
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, CompositeVideoClip

TEMAS_SEMANA = {
    "Lunes": "Cambio",
    "Martes": "Paz",
    "Miércoles": "Esperanza",
    "Jueves": "Gratitud",
    "Viernes": "Resiliencia",
    "Sábado": "Constancia",
    "Domingo": "Logros"
}

MATRIZ_CONTENIDO = [
    "La disciplina transforma tu realidad diaria y construye un destino solido.",
    "Cada obstaculo superado fortalece tu mente para los grandes retos.",
    "El enfoque constante elimina las dudas y acelera tu progreso personal.",
    "Acepta el proceso de evolucion y confia en el poder de la constancia.",
    "Tus habitos diarios definen la magnitud de tus futuros logros."
]

def obtener_fondo_pexels(tema, output_path):
    api_key = os.environ.get("PEXELS_API_KEY") or os.environ.get("PEXELS_KEY")
    if not api_key:
        print("[ERROR] Falta la clave de Pexels.")
        print("Asegúrate de configurar PEXELS_API_KEY como secreto en GitHub.")
        sys.exit(1)
    
    headers = {"Authorization": api_key}
    url = f"https://api.pexels.com/v1/search?query={tema}+vertical&per_page=15"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            photos = data.get("photos", [])
            if photos:
                foto = random.choice(photos)
                img_url = foto["src"]["portrait"]
                img_data = requests.get(img_url).content
                with open(output_path, "wb") as handler:
                    handler.write(img_data)
                print(f"[PEXELS] Fondo descargado correctamente para: {tema}")
                return True
    except Exception as e:
        print(f"[PEXELS] Error de conexion: {e}")
    
    img = Image.new('RGB', (1080, 1920), color=(15, 15, 25))
    img.save(output_path)
    print(f"[PEXELS] Usando fondo de respaldo para: {tema}")
    return True

def generar_video(dia, tema, indice, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = int(time.time())
    video_filename = f"video_{dia.lower()}_{indice}_{timestamp}.mp4"
    video_path = os.path.join(output_dir, video_filename)
    bg_path = f"bg_{dia.lower()}_{indice}.jpg"
    
    print(f"[PROCESO] Iniciando video {indice} para {dia} (Tema: {tema})...")
    obtener_fondo_pexels(tema, bg_path)
    
    # Duración estricta y aleatoria entre 75 y 85 segundos
    duracion = random.uniform(75.0, 85.0)
    
    frase = random.choice(MATRIZ_CONTENIDO)
    hook = f"El secreto oculto sobre {tema}"
    
    img_bg = Image.open(bg_path)
    img_bg = img_bg.resize((1080, 1920), Image.Resampling.LANCZOS)
    img_bg.save(bg_path)
    
    clip_fondo = ImageClip(bg_path).set_duration(duracion)
    
    # Capa transparente con dimensiones exactas verticales 1080x1920
    capa_txt = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(capa_txt)
    
    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font_hook = ImageFont.truetype(font_path, 52)
        font_texto = ImageFont.truetype(font_path, 42)
        font_firma = ImageFont.truetype(font_path, 28)
    except:
        font_hook = ImageFont.load_default()
        font_texto = ImageFont.load_default()
        font_firma = ImageFont.load_default()

    # 1. Gancho superior (Hook) centrado con reborde negro y resplandor
    hook_x = 540 - (len(hook) * 13)
    hook_y = 280
    for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2), (0,-2), (0,2), (-2,0), (2,0)]:
        draw.text((hook_x + dx, hook_y + dy), hook, font=font_hook, fill=(0, 0, 0, 255))
    draw.text((hook_x, hook_y), hook, font=font_hook, fill=(255, 255, 255, 255))

    # 2. Firma permanente: Abajo a la derecha (Estrictamente separada y sin tocar el centro)
    firma_texto = "@jonathan_irigoyen"
    firma_x = 1050 - (len(firma_texto) * 17)
    firma_y = 1820
    for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
        draw.text((firma_x + dx, firma_y + dy), firma_texto, font=font_firma, fill=(0, 0, 0, 255))
    draw.text((firma_x, firma_y), firma_texto, font=font_firma, fill=(255, 205, 120, 255)) # Iluminación cálida

    # 3. Párrafo / Texto principal: Posicionado abajo, JUSTO ARRIBA de la firma sin superponerse
    texto_x = 540 - (len(frase) * 10)
    texto_y = 1680
    for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2), (0,-2), (0,2), (-2,0), (2,0)]:
        draw.text((texto_x + dx, texto_y + dy), frase, font=font_texto, fill=(0, 0, 0, 255))
    draw.text((texto_x, texto_y), frase, font=font_texto, fill=(255, 255, 255, 255))

    temp_img_path = f"temp_overlay_{dia}.png"
    capa_txt.save(temp_img_path)
    
    clip_overlay = ImageClip(temp_img_path).set_duration(duracion)
    
    video_final = CompositeVideoClip([clip_fondo, clip_overlay])
    video_final.write_videofile(video_path, fps=24, codec="libx264", audio=False, logger=None)
    
    if os.path.exists(bg_path):
        os.remove(bg_path)
    if os.path.exists(temp_img_path):
        os.remove(temp_img_path)
        
    print(f"[EXITO] Video generado con éxito: {video_path}")
    return video_path

def main():
    parser = argparse.ArgumentParser(description="Generador de Videos Virales por Día")
    parser.add_argument("--videos", type=int, default=5, help="Cantidad de videos por día")
    parser.add_argument("--tema", type=str, default="aleatorio", help="Temática (aleatorio o todo)")
    args = parser.parse_args()

    print("[INICIO] Script configurado correctamente. Analizando argumentos...")
    print("==================================================")
    print(f"📝 Videos por día: {args.videos}")
    print(f"🎯 Temática: {args.tema}")
    print("==================================================")

    output_dir = "videos_salida"
    os.makedirs(output_dir, exist_ok=True)
    
    for dia, tema in TEMAS_SEMANA.items():
        for i in range(1, args.videos + 1):
            generar_video(dia, tema, i, output_dir)

    print("🎉 ¡Todos los videos generados correctamente!")
    
    zip_nombre = f"videos_generados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    print(f"📦 Comprimiendo videos en {zip_nombre}...")
    
    with zipfile.ZipFile(zip_nombre, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith(".mp4"):
                    zipf.write(os.path.join(root, file), os.path.basename(file))
                    
    print(f"[EXITO] Archivo ZIP creado y listo: {zip_nombre}")

if __name__ == "__main__":
    main()
