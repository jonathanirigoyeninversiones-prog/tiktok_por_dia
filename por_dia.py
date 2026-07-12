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
SUJETOS_UNIVERSALES = [
    "la vida", "el camino", "la experiencia", "el corazón", "el alma",
    "la mente", "el ser", "la esencia", "cada día", "el momento",
    "la oportunidad", "el cambio", "la transformación", "la fuerza interior",
    "la luz", "la esperanza", "el propósito", "la conexión"
]

VERBOS_UNIVERSALES = [
    "enseña", "transforma", "fortalece", "conecta", "alivia",
    "guía", "impulsa", "acompaña", "renueva", "despierta",
    "eleva", "sostiene", "ilumina", "abre", "sana",
    "motiva", "inspira", "empodera", "libera", "abraza"
]

COMPLEMENTOS_UNIVERSALES = [
    "tu corazón", "tu alma", "tu camino", "tu vida", "tu ser",
    "tu esencia", "tu mente", "tu espíritu", "tu destino", "tu verdad",
    "cada paso", "tus sueños", "tu propósito", "tu crecimiento", "tu bienestar",
    "tu paz", "tu luz", "tu fuerza", "tu esperanza", "tu libertad"
]

# ============================================
# 📝 LISTAS DE SUJETOS, VERBOS Y COMPLEMENTOS
# ============================================
SUJETOS = {
    "Motivacion": ["La motivación", "La energía", "El entusiasmo", "La pasión", "La fe", "El coraje", "La determinación", "La disciplina", "La resiliencia", "La voluntad", "El impulso", "La chispa", "La llama", "El vigor", "La convicción", "La firmeza", "La constancia", "La perseverancia", "La tenacidad", "La entereza"],
    "Constancia": ["La constancia", "La perseverancia", "La disciplina", "La paciencia", "El esfuerzo", "La rutina", "El hábito", "La tenacidad", "La firmeza", "La resistencia", "La continuidad", "La persistencia", "La determinación", "La voluntad", "La dedicación", "El empeño", "La laboriosidad", "La asiduidad", "La regularidad", "La obstinación"],
    "Superacion": ["La superación", "El crecimiento", "La evolución", "La transformación", "La mejora", "El avance", "El progreso", "El desarrollo", "El aprendizaje", "La resiliencia", "La renovación", "La elevación", "La expansión", "La maduración", "La plenitud", "La fortaleza", "La entereza", "La templanza", "La firmeza", "La solidez"],
    "Gratitud": ["La gratitud", "El agradecimiento", "La apreciación", "El reconocimiento", "La bendición", "La generosidad", "La humildad", "La satisfacción", "La alegría", "La paz", "La complacencia", "La benevolencia", "La clemencia", "La indulgencia", "La mansedumbre", "La dulzura", "La benignidad", "La compasión", "La empatía", "La solidaridad"],
    "Logros": ["El éxito", "El logro", "El triunfo", "La victoria", "El avance", "El progreso", "El cumplimiento", "La meta", "El objetivo", "La conquista", "La hazaña", "La proeza", "El alcance", "La realización", "La materialización", "La culminación", "La finalización", "La ejecución", "La consumación", "El remate"],
    "AmorPropio": ["El amor propio", "La autoaceptación", "El autocuidado", "La autocompasión", "La confianza", "La valía personal", "La autoestima", "El respeto", "La libertad interior", "La paz", "La dignidad", "La integridad", "La autenticidad", "La sinceridad", "La honestidad", "La transparencia", "La coherencia", "La estabilidad", "La serenidad", "La plenitud"],
    "Esperanza": ["La esperanza", "La ilusión", "La fe", "El optimismo", "La confianza", "La certeza", "La luz", "La promesa", "El nuevo comienzo", "La renovación", "La alegría", "La convicción", "La seguridad", "La firmeza", "La estabilidad", "La constancia", "La perseverancia", "La determinación", "La voluntad", "La tenacidad"],
    "Confianza": ["La confianza", "La seguridad", "La certeza", "La convicción", "La fe", "El valor", "La determinación", "La firmeza", "La solidez", "La estabilidad", "La garantía", "La evidencia", "La prueba", "El fundamento", "La base", "El cimiento", "El sostén", "El apoyo", "El respaldo", "La credibilidad"],
    "Resiliencia": ["La resiliencia", "La fortaleza", "La resistencia", "La tenacidad", "La entereza", "La firmeza", "La constancia", "La determinación", "El temple", "La dureza", "La robustez", "La solidez", "La perseverancia", "La persistencia", "La continuidad", "La regularidad", "La asiduidad", "La laboriosidad", "La obstinación", "La firmeza"],
    "Felicidad": ["La felicidad", "La alegría", "La plenitud", "La satisfacción", "El bienestar", "La calma", "La paz", "El gozo", "La dicha", "El contento", "El regocijo", "El júbilo", "La euforia", "El entusiasmo", "La vitalidad", "La energía", "La armonía", "El equilibrio", "La serenidad", "La tranquilidad"],
    "Proposito": ["El propósito", "La misión", "La vocación", "La meta", "El objetivo", "El destino", "La razón", "El norte", "El anhelo", "La aspiración", "El deseo", "La intención", "El fin", "La finalidad", "El blanco", "El rumbo", "La dirección", "El camino", "El sendero", "La visión"],
    "Optimismo": ["El optimismo", "La esperanza", "La fe", "La confianza", "La positividad", "La convicción", "La certeza", "La alegría", "La luz", "El entusiasmo", "La vitalidad", "La energía", "La ilusión", "El contento", "La satisfacción", "La plenitud", "La paz", "La serenidad", "La tranquilidad", "El optimismo"],
    "PazInterior": ["La paz interior", "La serenidad", "La calma", "La tranquilidad", "La armonía", "El sosiego", "La quietud", "La placidez", "La clemencia", "La mansedumbre", "La dulzura", "La benignidad", "La compasión", "La empatía", "La solidaridad", "La benevolencia", "La indulgencia", "La generosidad", "La humildad", "La gratitud"],
    "Actitud": ["La actitud", "La disposición", "La postura", "La posición", "La mentalidad", "El enfoque", "La perspectiva", "La visión", "El ángulo", "El punto de vista", "La orientación", "La dirección", "El rumbo", "El camino", "El sendero", "La vía", "La forma", "El modo", "La manera", "El estilo"],
    "Crecimiento": ["El crecimiento", "El desarrollo", "La evolución", "La maduración", "La expansión", "La mejora", "El progreso", "El avance", "La superación", "La transformación", "La renovación", "La elevación", "La ampliación", "La extensión", "La multiplicación", "La magnificación", "El engrandecimiento", "El fortalecimiento", "La consolidación", "La afirmación"],
    "Cambio": ["El cambio", "La transformación", "La mutación", "La evolución", "La adaptación", "La renovación", "La reforma", "La innovación", "La variación", "La modificación", "La alteración", "La conversión", "La inversión", "La revolución", "La metamorfosis", "La permutación", "La sustitución", "La transición", "El viraje", "El giro"],
    "Libertad": ["La libertad", "La independencia", "La autonomía", "La autodeterminación", "La liberación", "La emancipación", "La soltura", "El desahogo", "La espontaneidad", "La fluidez", "La flexibilidad", "La adaptabilidad", "La movilidad", "La elasticidad", "La plasticidad", "La ductilidad", "La maleabilidad", "La versatilidad", "La agilidad", "La desenvoltura"],
    "Aprendizaje": ["El aprendizaje", "La enseñanza", "La instrucción", "La educación", "El conocimiento", "La sabiduría", "La información", "La experiencia", "La lección", "La comprensión", "La asimilación", "La interiorización", "La asunción", "La aceptación", "La integración", "La incorporación", "La internalización", "La absorción", "La captación", "La asimilación"],
    "Sabiduria": ["La sabiduría", "La prudencia", "La sensatez", "La cordura", "La mesura", "La discreción", "La templanza", "La moderación", "La sagacidad", "La perspicacia", "La clarividencia", "La intuición", "La percepción", "La comprensión", "La penetración", "La agudeza", "La fineza", "La sutileza", "La delicadeza", "La elegancia"],
    "Conexion": ["La conexión", "El vínculo", "El lazo", "El enlace", "La relación", "La comunicación", "El afecto", "La empatía", "La solidaridad", "La unión", "La cohesión", "La integración", "La armonía", "La concordia", "La paz", "La amistad", "El compañerismo", "La hermandad", "La fraternidad", "La camaradería"]
}

VERBOS = {
    "Motivacion": ["impulsa", "mueve", "enciende", "fortalece", "alienta", "despierta", "eleva", "conduce", "guía", "transforma", "activa", "estimula", "desata", "despliega", "multiplica", "intensifica", "profundiza", "amplía", "extiende", "eleva"],
    "Constancia": ["construye", "consolida", "fortalece", "afianza", "establece", "mantiene", "sostiene", "cultiva", "desarrolla", "perfecciona", "realiza", "concreta", "materializa", "culmina", "finaliza", "ejecuta", "consume", "remata", "corona", "afianza"],
    "Superacion": ["transforma", "eleva", "fortalece", "empodera", "libera", "enseña", "moldea", "construye", "renueva", "revitaliza", "expande", "despliega", "multiplica", "intensifica", "profundiza", "amplía", "extiende", "eleva", "engrandece", "magnifica"],
    "Gratitud": ["transforma", "ilumina", "enaltece", "purifica", "conecta", "abre", "despeja", "fortalece", "restaura", "bendice", "eleva", "expande", "multiplica", "intensifica", "profundiza", "amplía", "extiende", "eleva", "engrandece", "magnifica"],
    "Logros": ["construyen", "celebran", "reconocen", "impulsan", "motivan", "enseñan", "fortalecen", "abren", "conducen", "materializan", "concretan", "culminan", "finalizan", "ejecutan", "consuman", "rematan", "coronan", "consolidan", "afianzan", "rematan"],
    "AmorPropio": ["fortalece", "libera", "acepta", "valora", "respeta", "consuela", "abraza", "nutre", "protege", "empodera", "eleva", "expande", "multiplica", "intensifica", "profundiza", "amplía", "extiende", "eleva", "engrandece", "magnifica"],
    "Esperanza": ["ilumina", "guía", "sostiene", "alienta", "fortalece", "renueva", "abre", "conecta", "asegura", "promete", "anima", "impulsa", "mueve", "despierta", "eleva", "conduce", "transforma", "activa", "estimula", "desata"],
    "Confianza": ["fortalece", "afianza", "consolida", "reafirma", "valida", "confirma", "certifica", "corrobora", "asegura", "garantiza", "establece", "fija", "sostiene", "mantiene", "perpetúa", "consolida", "afianza", "arraiga", "cimienta", "edifica"],
    "Resiliencia": ["fortalece", "endurece", "templa", "forja", "moldea", "construye", "asienta", "consolida", "robustece", "afianza", "vigoriza", "tonifica", "corrobora", "afirma", "consolida", "fija", "sostiene", "mantiene", "perpetúa", "consolida"],
    "Felicidad": ["ilumina", "colma", "plenifica", "satisface", "completa", "regocija", "alegra", "enaltece", "embellece", "perfecciona", "eleva", "expande", "multiplica", "intensifica", "profundiza", "amplía", "extiende", "eleva", "engrandece", "magnifica"],
    "Proposito": ["guía", "orienta", "encamina", "dirige", "conduce", "lleva", "sirve", "motiva", "inspira", "define", "especifica", "determina", "fija", "marca", "señala", "indica", "muestra", "enseña", "descubre", "revela"],
    "Optimismo": ["ilumina", "alienta", "fortalece", "anima", "empodera", "renueva", "inspira", "conduce", "guía", "sostiene", "activa", "estimula", "desata", "despliega", "multiplica", "intensifica", "profundiza", "amplía", "extiende", "eleva"],
    "PazInterior": ["calma", "tranquiliza", "serena", "apacigua", "aquieta", "sosiega", "armoniza", "equilibra", "alinea", "centra", "sosiega", "aquieta", "calma", "tranquiliza", "serena", "apacigua", "aquieta", "sosiega", "armoniza", "equilibra"],
    "Actitud": ["determina", "marca", "define", "orienta", "dirige", "conduce", "abre", "cierra", "cambia", "transforma", "modifica", "altera", "varía", "renueva", "reinventa", "reforma", "revoluciona", "rompe", "renueva", "innova"],
    "Crecimiento": ["impulsa", "promueve", "facilita", "acelera", "prolonga", "extiende", "intensifica", "multiplica", "magnifica", "engrandece", "eleva", "expande", "despliega", "desata", "desencadena", "destraba", "suelta", "desprende", "libera", "desbloquea"],
    "Cambio": ["transforma", "modifica", "altera", "varía", "renueva", "reinventa", "reforma", "revoluciona", "rompe", "renueva", "innova", "cambia", "convierte", "adapta", "ajusta", "reorienta", "reencauza", "reconduce", "redefine", "reestructura"],
    "Libertad": ["expande", "abre", "libera", "desata", "despeja", "desbloquea", "desencadena", "destraba", "suelta", "desprende", "extiende", "multiplica", "intensifica", "profundiza", "amplía", "eleva", "engrandece", "magnifica", "expande", "despliega"],
    "Aprendizaje": ["enseña", "ilumina", "despeja", "aclara", "educa", "forma", "moldea", "instruye", "capacita", "desarrolla", "entrena", "adiestra", "prepara", "habilita", "familiariza", "introduce", "inicia", "orienta", "guía", "conduce"],
    "Sabiduria": ["ilumina", "orienta", "guía", "aconseja", "enseña", "descubre", "revela", "acredita", "certifica", "valida", "confirma", "corrobora", "asegura", "garantiza", "establece", "fija", "sostiene", "mantiene", "perpetúa", "consolida"],
    "Conexion": ["une", "vincula", "enlaza", "conecta", "comunica", "acerca", "integra", "compromete", "solidariza", "comparte", "asocia", "relaciona", "complementa", "armoniza", "equilibra", "sincroniza", "coordina", "ajusta", "adapta", "fusiona"]
}

COMPLEMENTOS = {
    "Motivacion": ["tus sueños", "tu camino", "tus metas", "tu fuerza interior", "tu propósito", "tu crecimiento", "tu mejor versión", "tu destino", "tu verdad", "cada paso", "tu ser", "tu alma", "tu mente", "tu corazón", "tu espíritu", "tu vida", "tu futuro", "tu presente", "tu pasado", "tu esencia"],
    "Constancia": ["el éxito", "tus metas", "tus logros", "tu progreso", "tu camino", "tu futuro", "tu disciplina", "tu resistencia", "tu grandeza", "tu victoria", "tu constancia", "tu perseverancia", "tu esfuerzo", "tu trabajo", "tu dedicación", "tu empeño", "tu labor", "tu obra", "tu legado", "tu huella"],
    "Superacion": ["tu vida", "tu mente", "tu carácter", "tu espíritu", "tu futuro", "tu realidad", "tu ser", "tu propósito", "tu camino", "tu libertad", "tu alma", "tu corazón", "tu esencia", "tu verdad", "tu destino", "tu historia", "tu legado", "tu huella", "tu obra", "tu labor"],
    "Gratitud": ["tu vida", "tu corazón", "tu alma", "tu ser", "tu camino", "tu realidad", "tu entorno", "tu familia", "tu presente", "tu futuro", "tu pasado", "tu esencia", "tu verdad", "tu destino", "tu historia", "tu legado", "tu huella", "tu obra", "tu labor", "tu esfuerzo"],
    "Logros": ["tu esfuerzo", "tu dedicación", "tu trabajo", "tu constancia", "tu visión", "tu camino", "tu legado", "tu historia", "tu progreso", "tu destino", "tu meta", "tu objetivo", "tu éxito", "tu triunfo", "tu victoria", "tu avance", "tu progreso", "tu cumplimiento", "tu conquista", "tu realización"],
    "AmorPropio": ["tu ser", "tu alma", "tu mente", "tu cuerpo", "tu espíritu", "tu esencia", "tu corazón", "tu vida", "tu paz", "tu libertad", "tu verdad", "tu destino", "tu camino", "tu historia", "tu legado", "tu huella", "tu obra", "tu labor", "tu esfuerzo", "tu trabajo"],
    "Esperanza": ["tu futuro", "tu camino", "tu vida", "tu alma", "tu fe", "tu destino", "tu propósito", "tu mañana", "tus sueños", "tu luz", "tu esperanza", "tu ilusión", "tu optimismo", "tu confianza", "tu certeza", "tu convicción", "tu seguridad", "tu firmeza", "tu estabilidad", "tu constancia"],
    "Confianza": ["tu decisión", "tu camino", "tu proceso", "tu vida", "tu instinto", "tu ser", "tu propósito", "tu destino", "tu esfuerzo", "tu trabajo", "tu dedicación", "tu empeño", "tu labor", "tu obra", "tu legado", "tu huella", "tu verdad", "tu esencia", "tu alma", "tu corazón"],
    "Resiliencia": ["tu espíritu", "tu corazón", "tu mente", "tu alma", "tu carácter", "tu fuerza", "tu fe", "tu propósito", "tu vida", "tu camino", "tu destino", "tu historia", "tu legado", "tu huella", "tu obra", "tu labor", "tu esfuerzo", "tu trabajo", "tu dedicación", "tu empeño"],
    "Felicidad": ["tu vida", "tu alma", "tu corazón", "tu mente", "tu ser", "tu espíritu", "tu familia", "tus amigos", "tu camino", "tu destino", "tu propósito", "tu meta", "tu objetivo", "tu éxito", "tu triunfo", "tu victoria", "tu avance", "tu progreso", "tu cumplimiento", "tu conquista"],
    "Proposito": ["tu vida", "tu camino", "tu destino", "tu misión", "tu vocación", "tu llamado", "tu esfuerzo", "tu trabajo", "tu legado", "tu meta", "tu objetivo", "tu éxito", "tu triunfo", "tu victoria", "tu avance", "tu progreso", "tu cumplimiento", "tu conquista", "tu realización", "tu plenitud"],
    "Optimismo": ["tu futuro", "tu vida", "tu camino", "tu destino", "tu propósito", "tu fe", "tu alma", "tu corazón", "tu esperanza", "tu luz", "tu ilusión", "tu optimismo", "tu confianza", "tu certeza", "tu convicción", "tu seguridad", "tu firmeza", "tu estabilidad", "tu constancia", "tu perseverancia"],
    "PazInterior": ["tu mente", "tu corazón", "tu alma", "tu espíritu", "tu ser", "tu vida", "tu destino", "tu camino", "tu propósito", "tu felicidad", "tu paz", "tu tranquilidad", "tu serenidad", "tu calma", "tu armonía", "tu equilibrio", "tu sosiego", "tu quietud", "tu placidez", "tu clemencia"],
    "Actitud": ["tu día", "tu semana", "tu mes", "tu año", "tu vida", "tu proyecto", "tu meta", "tu objetivo", "tu misión", "tu propósito", "tu camino", "tu destino", "tu éxito", "tu triunfo", "tu victoria", "tu avance", "tu progreso", "tu cumplimiento", "tu conquista", "tu realización"],
    "Crecimiento": ["tu persona", "tu carácter", "tu mente", "tu espíritu", "tu alma", "tu vida", "tu futuro", "tu camino", "tu destino", "tu misión", "tu meta", "tu objetivo", "tu éxito", "tu triunfo", "tu victoria", "tu avance", "tu progreso", "tu cumplimiento", "tu conquista", "tu realización"],
    "Cambio": ["tu vida", "tu realidad", "tu futuro", "tu camino", "tu destino", "tu propósito", "tu ser", "tu alma", "tu mente", "tu corazón", "tu espíritu", "tu esencia", "tu verdad", "tu historia", "tu legado", "tu huella", "tu obra", "tu labor", "tu esfuerzo", "tu trabajo"],
    "Libertad": ["tu ser", "tu alma", "tu mente", "tu corazón", "tu espíritu", "tu vida", "tu camino", "tu destino", "tu propósito", "tu verdad", "tu esencia", "tu historia", "tu legado", "tu huella", "tu obra", "tu labor", "tu esfuerzo", "tu trabajo", "tu dedicación", "tu empeño"],
    "Aprendizaje": ["tu vida", "tu camino", "tu mente", "tu ser", "tu alma", "tu espíritu", "tu destino", "tu propósito", "tu legado", "tu futuro", "tu meta", "tu objetivo", "tu éxito", "tu triunfo", "tu victoria", "tu avance", "tu progreso", "tu cumplimiento", "tu conquista", "tu realización"],
    "Sabiduria": ["tu vida", "tu camino", "tu destino", "tu propósito", "tu ser", "tu alma", "tu mente", "tu corazón", "tu espíritu", "tu legado", "tu meta", "tu objetivo", "tu éxito", "tu triunfo", "tu victoria", "tu avance", "tu progreso", "tu cumplimiento", "tu conquista", "tu realización"],
    "Conexion": ["tu vida", "tu camino", "tu destino", "tu propósito", "tu ser", "tu alma", "tu mente", "tu corazón", "tu espíritu", "tu legado", "tu meta", "tu objetivo", "tu éxito", "tu triunfo", "tu victoria", "tu avance", "tu progreso", "tu cumplimiento", "tu conquista", "tu realización"]
}

# ============================================
# 🗣️ FRASES COLOQUIALES Y SENCILLAS
# ============================================
INICIOS_COLOQUIALES = [
    "Mira,",
    "Es que",
    "La cosa es que",
    "A veces pasa que",
    "Te digo algo,",
    "Lo bueno es que",
    "El tema es que",
    "Fíjate que",
    "Resulta que",
    "La verdad es que",
    "O sea,",
    "Bueno,",
    "Piensa esto:",
    "Imagínate que",
    "Lo cierto es que",
    "Sin duda,",
    "Vale,"
]

PREGUNTAS_RETORICAS_SENCILLAS = [
    "¿sabes?",
    "¿no te parece?",
    "¿verdad?",
    "¿te das cuenta?",
    "¿no crees?",
    "¿a que sí?",
    "¿lo ves?",
    "¿me entiendes?",
    "¿no es así?",
    "¿qué te parece?"
]

def hacer_sencilla(frase):
    """Convierte una frase en algo más sencillo y coloquial."""
    if not frase:
        return frase
    # Asegurar mayúscula
    if frase[0].islower():
        frase = frase[0].upper() + frase[1:]
    # Añadir inicio coloquial (a veces)
    if random.random() < 0.5:
        intro = random.choice(INICIOS_COLOQUIALES)
        if intro[-1] in [",", ":", ";"]:
            frase = f"{intro} {frase[0].lower() + frase[1:]}"
        else:
            frase = f"{intro} {frase[0].lower() + frase[1:]}"
    # Añadir pregunta retórica (a veces)
    if random.random() < 0.3:
        pregunta = random.choice(PREGUNTAS_RETORICAS_SENCILLAS)
        if frase[-1] in [".", "?", "!"]:
            frase = frase[:-1] + " " + pregunta
        else:
            frase = frase + " " + pregunta
    return frase

# ============================================
# 📝 GENERACIÓN DE PREGUNTA Y DESARROLLO
# ============================================
INICIOS_PREGUNTA = [
    "Alguna vez has sentido que",
    "Qué pasaría si",
    "Cuánto tiempo más vas a",
    "Por qué",
    "Cómo",
    "Qué te impide",
    "Qué harías si",
    "Estás listo para",
    "Cuándo fue la última vez que",
    "En qué momento decidiste",
    "De qué manera",
    "Hasta cuándo",
    "Qué crees que pasaría si",
    "Por qué crees que",
    "Qué significa para ti",
    "Cómo te sientes cuando",
    "Qué cambiarías de",
    "Cuál es la razón por la que",
    "Qué esperas de",
    "Qué te gustaría decirle a"
]

def generar_pregunta(tema_nombre):
    sujeto = random.choice(SUJETOS.get(tema_nombre, SUJETOS["Motivacion"])).lower()
    verbo = random.choice(VERBOS.get(tema_nombre, VERBOS["Motivacion"])).lower()
    complemento = random.choice(COMPLEMENTOS.get(tema_nombre, COMPLEMENTOS["Motivacion"])).lower()
    inicio = random.choice(INICIOS_PREGUNTA)
    opciones = [
        f"{inicio} {sujeto} {verbo} {complemento}?",
        f"{inicio} {sujeto} {verbo} {complemento} sin miedo?",
        f"{inicio} {sujeto} {verbo} {complemento} y alcanzar tus metas?",
        f"{inicio} {sujeto} {verbo} {complemento} cuando todo parece difícil?",
        f"{inicio} {sujeto} {verbo} {complemento} a pesar de los obstáculos?"
    ]
    pregunta = random.choice(opciones)
    # Asegurar signos de interrogación
    if not pregunta.startswith("¿"):
        pregunta = "¿" + pregunta
    if not pregunta.endswith("?"):
        pregunta += "?"
    return pregunta

def generar_frase_desarrollo(tema_nombre):
    sujetos = SUJETOS.get(tema_nombre, SUJETOS_UNIVERSALES)
    verbos = VERBOS.get(tema_nombre, VERBOS_UNIVERSALES)
    complementos = COMPLEMENTOS.get(tema_nombre, COMPLEMENTOS_UNIVERSALES)
    
    if tema_nombre not in SUJETOS:
        # Detectar género para el artículo
        femeninas = ("a", "ad", "ión", "umbre", "dad", "tad", "sis", "ez", "eza")
        if tema_nombre.lower().endswith(femeninas) and tema_nombre.lower() not in ["amor", "cambio", "crecimiento", "propósito", "optimismo", "entusiasmo", "aprendizaje", "conocimiento"]:
            articulo = "La"
        else:
            articulo = "El"
        if tema_nombre.lower() in ["amor", "cambio", "crecimiento", "propósito", "optimismo", "entusiasmo", "aprendizaje", "conocimiento"]:
            articulo = "El"
        
        # Patrones sencillos para temas no predefinidos
        patrones = [
            f"{articulo} {tema_nombre} te enseña a {random.choice(verbos)} {random.choice(complementos)}.",
            f"Reflexionar sobre {articulo.lower()} {tema_nombre} te ayuda a {random.choice(verbos)} {random.choice(complementos)}.",
            f"Cada día puedes usar {articulo.lower()} {tema_nombre} para {random.choice(verbos)} {random.choice(complementos)}.",
            f"{articulo} {tema_nombre} está ahí para que {random.choice(verbos)} {random.choice(complementos)}.",
            f"Aceptar {articulo.lower()} {tema_nombre} es el primer paso para {random.choice(verbos)} {random.choice(complementos)}.",
            f"Cuando hablamos de {articulo.lower()} {tema_nombre}, hablamos de {random.choice(verbos)} {random.choice(complementos)}.",
        ]
        frase = random.choice(patrones)
    else:
        sujeto = random.choice(sujetos)
        verbo = random.choice(verbos)
        complemento = random.choice(complementos)
        # Patrones más sencillos y directos
        plantillas = [
            f"{sujeto} {verbo} {complemento}.",
            f"Es que {sujeto.lower()} {verbo} {complemento}.",
            f"La verdad es que {sujeto.lower()} {verbo} {complemento}.",
            f"Fíjate que {sujeto.lower()} {verbo} {complemento}.",
            f"O sea, {sujeto.lower()} {verbo} {complemento}.",
            f"Bueno, {sujeto.lower()} {verbo} {complemento}.",
            f"Mira, {sujeto.lower()} {verbo} {complemento}.",
        ]
        frase = random.choice(plantillas)
    
    # Aplicar simplificación (con probabilidad)
    if random.random() < 0.6:
        frase = hacer_sencilla(frase)
    else:
        if frase and frase[0].islower():
            frase = frase[0].upper() + frase[1:]
    return frase

def generar_texto_completo(tema_nombre):
    pregunta = generar_pregunta(tema_nombre)
    num_desarrollo = random.choice([6, 7, 8])
    desarrollo = []
    for _ in range(num_desarrollo):
        desarrollo.append(generar_frase_desarrollo(tema_nombre))
    random.shuffle(desarrollo)
    # Unir pregunta y desarrollo con saltos de línea
    texto_completo = pregunta + "\n\n" + "\n\n".join(desarrollo)
    return texto_completo

def dividir_en_parrafos(texto, num_partes):
    """
    Divide el texto en párrafos de entre 3 y 5 líneas, sin cortar oraciones.
    """
    texto = re.sub(r'Te leo en los comentarios\s*[.!?]*\s*', '', texto)
    oraciones = re.findall(r'[^.!?]+[.!?]', texto)
    oraciones = [o.strip() for o in oraciones if len(o.strip()) > 5]
    
    if not oraciones:
        oraciones = [texto.strip()]
    
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
            # Borde negro grueso
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

    # Limpieza de temporales
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
# 🚀 EJECUCIÓN PRINCIPAL (con argumentos y ZIP directo)
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

    # 🔥 El ZIP se llamará DD-MM-AAAA.zip por defecto
    fecha_actual = datetime.now().strftime("%d-%m-%Y")
    if args.zip:
        nombre_zip = args.zip if args.zip.endswith(".zip") else args.zip + ".zip"
    else:
        nombre_zip = f"{fecha_actual}.zip"

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
                    # 🔥 Añadir solo el nombre del archivo (sin ruta)
                    zipf.write(os.path.join(root, file), arcname=file)
        print(f"✅ ZIP creado: {nombre_zip}")
        print(f"📁 Revisa la carpeta 'videos' y el archivo '{nombre_zip}'.")
    else:
        print("⏭️  No se creó ZIP (opción --no-zip activada).")
