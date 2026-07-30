def obtener_fondo_pexels(query):
    """Descarga un fondo multimedia vertical desde Pexels con control estricto de tiempo para evitar congelamientos."""
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1&orientation=portrait"
    headers = {"Authorization": CLAVE_PEXELS}
    
    try:
        # Añadimos un timeout de 5 segundos para que nunca se quede colgado
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("photos"):
                img_url = data["photos"][0]["src"]["large2x"]
                img_data = requests.get(img_url, timeout=5).content
                archivo_temp = f"fondo_{random.randint(1000,9999)}.jpg"
                with open(archivo_temp, "wb") as f:
                    f.write(img_data)
                return archivo_temp
    except Exception as e:
        print(f"[AVISO] Pexels tardó o falló ({e}). Usando fondo de respaldo de inmediato.")
    
    # Fondo de respaldo seguro por si Pexels no responde
    respaldo = Image.new("RGB", (1080, 1920), color=(25, 25, 25))
    archivo_temp = f"fondo_{random.randint(1000,9999)}.jpg"
    respaldo.save(archivo_temp)
    return archivo_temp
