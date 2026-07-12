# -*- coding: utf-8 -*-
import os
import sys
import json
import requests
import re
import time
import random
import argparse
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
    "El tema", "La reflexion", "La vida", "El camino", "La experiencia",
    "El corazon", "El alma", "La mente", "El ser", "La esencia",
    "Cada dia", "El momento", "La oportunidad", "El cambio", "La transformacion",
    "La fuerza interior", "La luz", "La esperanza", "El proposito", "La conexion"
]

VERBOS_UNIVERSALES = [
    "ensena", "transforma", "fortalece", "conecta", "alivia",
    "guia", "impulsa", "acompara", "renueva", "despierta",
    "eleva", "sostiene", "ilumina", "abre", "sanar",
    "motiva", "inspira", "empodera", "libera", "abraza"
]

COMPLEMENTOS_UNIVERSALES = [
    "tu corazon", "tu alma", "tu camino", "tu vida", "tu ser",
    "tu esencia", "tu mente", "tu espiritu", "tu destino", "tu verdad",
    "cada paso", "tus suenos", "tu proposito", "tu crecimiento", "tu bienestar",
    "tu paz", "tu luz", "tu fuerza", "tu esperanza", "tu libertad"
]

# ============================================
# 📝 LISTAS DE SUJETOS, VERBOS Y COMPLEMENTOS PARA LOS 20 TEMAS
# ============================================
SUJETOS = {
    "Motivacion": ["La motivacion", "La energia", "El entusiasmo", "La pasion", "La fe", "El coraje", "La determinacion", "La disciplina", "La resiliencia", "La voluntad", "El impulso", "La chispa", "La llama", "El vigor", "La conviccion", "La firmeza", "La constancia", "La perseverancia", "La tenacidad", "La entereza"],
    "Constancia": ["La constancia", "La perseverancia", "La disciplina", "La paciencia", "El esfuerzo", "La rutina", "El habito", "La tenacidad", "La firmeza", "La resistencia", "La continuidad", "La persistencia", "La determinacion", "La voluntad", "La dedicacion", "El empeno", "La laboriosidad", "La asiduidad", "La regularidad", "La obstinacion"],
    "Superacion": ["La superacion", "El crecimiento", "La evolucion", "La transformacion", "La mejora", "El avance", "El progreso", "El desarrollo", "El aprendizaje", "La resiliencia", "La renovacion", "La elevacion", "La expansion", "La maduracion", "La plenitud", "La fortaleza", "La entereza", "La templanza", "La firmeza", "La solidez"],
    "Gratitud": ["La gratitud", "El agradecimiento", "La apreciacion", "El reconocimiento", "La bendicion", "La generosidad", "La humildad", "La satisfaccion", "La alegria", "La paz", "La complacencia", "La benevolencia", "La clemencia", "La indulgencia", "La mansedumbre", "La dulzura", "La benignidad", "La compasion", "La empatia", "La solidaridad"],
    "Logros": ["El exito", "El logro", "El triunfo", "La victoria", "El avance", "El progreso", "El cumplimiento", "La meta", "El objetivo", "La conquista", "La hazana", "La proeza", "El alcance", "La realizacion", "La materializacion", "La culminacion", "La finalizacion", "La ejecucion", "La consumacion", "El remate"],
    "AmorPropio": ["El amor propio", "La autoaceptacion", "El autocuidado", "La autocompasion", "La confianza", "La valia personal", "La autoestima", "El respeto", "La libertad interior", "La paz", "La dignidad", "La integridad", "La autenticidad", "La sinceridad", "La honestidad", "La transparencia", "La coherencia", "La estabilidad", "La serenidad", "La plenitud"],
    "Esperanza": ["La esperanza", "La ilusion", "La fe", "El optimismo", "La confianza", "La certeza", "La luz", "La promesa", "El nuevo comienzo", "La renovacion", "La alegria", "La conviccion", "La seguridad", "La firmeza", "La estabilidad", "La constancia", "La perseverancia", "La determinacion", "La voluntad", "La tenacidad"],
    "Confianza": ["La confianza", "La seguridad", "La certeza", "La conviccion", "La fe", "El valor", "La determinacion", "La firmeza", "La solidez", "La estabilidad", "La garantia", "La evidencia", "La prueba", "El fundamento", "La base", "El cimiento", "El sostén", "El apoyo", "El respaldo", "La credibilidad"],
    "Resiliencia": ["La resiliencia", "La fortaleza", "La resistencia", "La tenacidad", "La entereza", "La firmeza", "La constancia", "La determinacion", "El temple", "La dureza", "La robustez", "La solidez", "La perseverancia", "La persistencia", "La continuidad", "La regularidad", "La asiduidad", "La laboriosidad", "La obstinacion", "La firmeza"],
    "Felicidad": ["La felicidad", "La alegria", "La plenitud", "La satisfaccion", "El bienestar", "La calma", "La paz", "El gozo", "La dicha", "El contento", "El regocijo", "El jubilo", "La euforia", "El entusiasmo", "La vitalidad", "La energia", "La armonia", "El equilibrio", "La serenidad", "La tranquilidad"],
    "Proposito": ["El proposito", "La mision", "La vocacion", "La meta", "El objetivo", "El destino", "La razon", "El norte", "El anhelo", "La aspiracion", "El deseo", "La intencion", "El fin", "La finalidad", "El blanco", "El rumbo", "La direccion", "El camino", "El sendero", "La vision"],
    "Optimismo": ["El optimismo", "La esperanza", "La fe", "La confianza", "La positividad", "La conviccion", "La certeza", "La alegria", "La luz", "El entusiasmo", "La vitalidad", "La energia", "La ilusion", "El contento", "La satisfaccion", "La plenitud", "La paz", "La serenidad", "La tranquilidad", "El optimismo"],
    "PazInterior": ["La paz interior", "La serenidad", "La calma", "La tranquilidad", "La armonia", "El sosiego", "La quietud", "La placidez", "La clemencia", "La mansedumbre", "La dulzura", "La benignidad", "La compasion", "La empatia", "La solidaridad", "La benevolencia", "La indulgencia", "La generosidad", "La humildad", "La gratitud"],
    "Actitud": ["La actitud", "La disposicion", "La postura", "La posicion", "La mentalidad", "El enfoque", "La perspectiva", "La vision", "El angulo", "El punto de vista", "La orientacion", "La direccion", "El rumbo", "El camino", "El sendero", "La via", "La forma", "El modo", "La manera", "El estilo"],
    "Crecimiento": ["El crecimiento", "El desarrollo", "La evolucion", "La maduracion", "La expansion", "La mejora", "El progreso", "El avance", "La superacion", "La transformacion", "La renovacion", "La elevacion", "La ampliacion", "La extension", "La multiplicacion", "La magnificacion", "El engrandecimiento", "El fortalecimiento", "La consolidacion", "La afirmacion"],
    "Cambio": ["El cambio", "La transformacion", "La mutacion", "La evolucion", "La adaptacion", "La renovacion", "La reforma", "La innovacion", "La variacion", "La modificacion", "La alteracion", "La conversion", "La inversion", "La revolucion", "La metamorfosis", "La permutacion", "La sustitucion", "La transicion", "El viraje", "El giro"],
    "Libertad": ["La libertad", "La independencia", "La autonomia", "La autodeterminacion", "La liberacion", "La emancipacion", "La soltura", "El desahogo", "La espontaneidad", "La fluidez", "La flexibilidad", "La adaptabilidad", "La movilidad", "La elasticidad", "La plasticidad", "La ductilidad", "La maleabilidad", "La versatilidad", "La agilidad", "La desenvoltura"],
    "Aprendizaje": ["El aprendizaje", "La ensenanza", "La instruccion", "La educacion", "El conocimiento", "La sabiduria", "La informacion", "La experiencia", "La leccion", "La comprension", "La asimilacion", "La interiorizacion", "La asuncion", "La aceptacion", "La integracion", "La incorporacion", "La internalizacion", "La absorcion", "La captacion", "La asimilacion"],
    "Sabiduria": ["La sabiduria", "La prudencia", "La sensatez", "La cordura", "La mesura", "La discrecion", "La templanza", "La moderacion", "La sagacidad", "La perspicacia", "La clarividencia", "La intuicion", "La percepcion", "La comprension", "La penetracion", "La agudeza", "La fineza", "La sutileza", "La delicadeza", "La elegancia"],
    "Conexion": ["La conexion", "El vinculo", "El lazo", "El enlace", "La relacion", "La comunicacion", "El afecto", "La empatia", "La solidaridad", "La union", "La cohesion", "La integracion", "La armonia", "La concordia", "La paz", "La amistad", "El companerismo", "La hermandad", "La fraternidad", "La camaraderia"]
}

VERBOS = {
    "Motivacion": ["impulsa", "mueve", "enciende", "fortalece", "alienta", "despierta", "eleva", "conduce", "guia", "transforma", "activa", "estimula", "desata", "despliega", "multiplica", "intensifica", "profundiza", "amplia", "extiende", "eleva"],
    "Constancia": ["construye", "consolida", "fortalece", "afianza", "establece", "mantiene", "sostiene", "cultiva", "desarrolla", "perfecciona", "realiza", "concreta", "materializa", "culmina", "finaliza", "ejecuta", "consume", "remata", "corona", "afianza"],
    "Superacion": ["transforma", "eleva", "fortalece", "empodera", "libera", "ensena", "moldea", "construye", "renueva", "revitaliza", "expande", "despliega", "multiplica", "intensifica", "profundiza", "amplia", "extiende", "eleva", "engrandece", "magnifica"],
    "Gratitud": ["transforma", "ilumina", "enaltece", "purifica", "conecta", "abre", "despeja", "fortalece", "restaura", "bendice", "eleva", "expande", "multiplica", "intensifica", "profundiza", "amplia", "extiende", "eleva", "engrandece", "magnifica"],
    "Logros": ["construyen", "celebran", "reconocen", "impulsan", "motivan", "ensenan", "fortalecen", "abren", "conducen", "materializan", "concretan", "culminan", "finalizan", "ejecutan", "consuman", "rematan", "coronan", "consolidan", "afianzan", "rematan"],
    "AmorPropio": ["fortalece", "libera", "acepta", "valora", "respeta", "consuela", "abraza", "nutre", "protege", "empodera", "eleva", "expande", "multiplica", "intensifica", "profundiza", "amplia", "extiende", "eleva", "engrandece", "magnifica"],
    "Esperanza": ["ilumina", "guia", "sostiene", "alienta", "fortalece", "renueva", "abre", "conecta", "asegura", "promete", "anima", "impulsa", "mueve", "despierta", "eleva", "conduce", "transforma", "activa", "estimula", "desata"],
    "Confianza": ["fortalece", "afianza", "consolida", "reafirma", "valida", "confirma", "certifica", "corrobora", "asegura", "garantiza", "establece", "fija", "sostiene", "mantiene", "perpetua", "consolida", "afianza", "arraiga", "cimienta", "edifica"],
    "Resiliencia": ["fortalece", "endurece", "templa", "forja", "moldea", "construye", "asienta", "consolida", "robustece", "afianza", "vigoriza", "tonifica", "corrobora", "afirma", "consolida", "fija", "sostiene", "mantiene", "perpetua", "consolida"],
    "Felicidad": ["ilumina", "colma", "plenifica", "satisface", "completa", "regocija", "alegra", "enaltece", "embellece", "perfecciona", "eleva", "expande", "multiplica", "intensifica", "profundiza", "amplia", "extiende", "eleva", "engrandece", "magnifica"],
    "Proposito": ["guia", "orienta", "encamina", "dirige", "conduce", "lleva", "sirve", "motiva", "inspira", "define", "especifica", "determina", "fija", "marca", "senala", "indica", "muestra", "ensena", "descubre", "revela"],
    "Optimismo": ["ilumina", "alienta", "fortalece", "anima", "empodera", "renueva", "inspira", "conduce", "guia", "sostiene", "activa", "estimula", "desata", "despliega", "multiplica", "intensifica", "profundiza", "amplia", "extiende", "eleva"],
    "PazInterior": ["calma", "tranquiliza", "serena", "apacigua", "aquieta", "sosiega", "armoniza", "equilibra", "alinea", "centra", "sosiega", "aquieta", "calma", "tranquiliza", "serena", "apacigua", "aquieta", "sosiega", "armoniza", "equilibra"],
    "Actitud": ["determina", "marca", "define", "orienta", "dirige", "conduce", "abre", "cierra", "cambia", "transforma", "modifica", "altera", "varia", "renueva", "reinventa", "reforma", "revoluciona", "rompe", "renueva", "innova"],
    "Crecimiento": ["impulsa", "promueve", "facilita", "acelera", "prolonga", "extiende", "intensifica", "multiplica", "magnifica", "engrandece", "eleva", "expande", "despliega", "desata", "desencadena", "destraba", "suelta", "desprende", "libera", "desbloquea"],
    "Cambio": ["transforma", "modifica", "altera", "varia", "renueva", "reinventa", "reforma", "revoluciona", "rompe", "renueva", "innova", "cambia", "convierte", "adapta", "ajusta", "reorienta", "reencauza", "reconduce", "redefine", "reestructura"],
    "Libertad": ["expande", "abre", "libera", "desata", "despeja", "desbloquea", "desencadena", "destraba", "suelta", "desprende", "extiende", "multiplica", "intensifica", "profundiza", "amplia", "eleva", "engrandece", "magnifica", "expande", "despliega"],
    "Aprendizaje": ["ensena", "ilumina", "despeja", "aclara", "educa", "forma", "moldea", "instruye", "capacita", "desarrolla", "entrena", "adiestra", "prepara", "habilita", "familiariza", "introduce", "inicia", "orienta", "guia", "conduce"],
    "Sabiduria": ["ilumina", "orienta", "guia", "aconseja", "ensena", "descubre", "revela", "acredita", "certifica", "valida", "confirma", "corrobora", "asegura", "garantiza", "establece", "fija", "sostiene", "mantiene", "perpetua", "consolida"],
    "Conexion": ["une", "vincula", "enlaza", "conecta", "comunica", "acerca", "integra", "compromete", "solidariza", "comparte", "asocia", "relaciona", "complementa", "armoniza", "equilibra", "sincroniza", "coordina", "ajusta", "adapta", "fusiona"]
}

COMPLEMENTOS = {
    "Motivacion": ["tus suenos", "tu camino", "tus metas", "tu fuerza interior", "tu proposito", "tu crecimiento", "tu mejor version", "tu destino", "tu verdad", "cada paso", "tu ser", "tu alma", "tu mente", "tu corazon", "tu espiritu", "tu vida", "tu futuro", "tu presente", "tu pasado", "tu esencia"],
    "Constancia": ["el exito", "tus metas", "tus logros", "tu progreso", "tu camino", "tu futuro", "tu disciplina", "tu resistencia", "tu grandeza", "tu victoria", "tu constancia", "tu perseverancia", "tu esfuerzo", "tu trabajo", "tu dedicacion", "tu empeno", "tu labor", "tu obra", "tu legado", "tu huella"],
    "Superacion": ["tu vida", "tu mente", "tu caracter", "tu espiritu", "tu futuro", "tu realidad", "tu ser", "tu proposito", "tu camino", "tu libertad", "tu alma", "tu corazon", "tu esencia", "tu verdad", "tu destino", "tu historia", "tu legado", "tu huella", "tu obra", "tu labor"],
    "Gratitud": ["tu vida", "tu corazon", "tu alma", "tu ser", "tu camino", "tu realidad", "tu entorno", "tu familia", "tu presente", "tu futuro", "tu pasado", "tu esencia", "tu verdad", "tu destino", "tu historia", "tu legado", "tu huella", "tu obra", "tu labor", "tu esfuerzo"],
    "Logros": ["tu esfuerzo", "tu dedicacion", "tu trabajo", "tu constancia", "tu vision", "tu camino", "tu legado", "tu historia", "tu progreso", "tu destino", "tu meta", "tu objetivo", "tu exito", "tu triunfo", "tu victoria", "tu avance", "tu progreso", "tu cumplimiento", "tu conquista", "tu realizacion"],
    "AmorPropio": ["tu ser", "tu alma", "tu mente", "tu cuerpo", "tu espiritu", "tu esencia", "tu corazon", "tu vida", "tu paz", "tu libertad", "tu verdad", "tu destino", "tu camino", "tu historia", "tu legado", "tu huella", "tu obra", "tu labor", "tu esfuerzo", "tu trabajo"],
    "Esperanza": ["tu futuro", "tu camino", "tu vida", "tu alma", "tu fe", "tu destino", "tu proposito", "tu manana", "tus suenos", "tu luz", "tu esperanza", "tu ilusion", "tu optimismo", "tu confianza", "tu certeza", "tu conviccion", "tu seguridad", "tu firmeza", "tu estabilidad", "tu constancia"],
    "Confianza": ["tu decision", "tu camino", "tu proceso", "tu vida", "tu instinto", "tu ser", "tu proposito", "tu destino", "tu esfuerzo", "tu trabajo", "tu dedicacion", "tu empeno", "tu labor", "tu obra", "tu legado", "tu huella", "tu verdad", "tu esencia", "tu alma", "tu corazon"],
    "Resiliencia": ["tu espiritu", "tu corazon", "tu mente", "tu alma", "tu caracter", "tu fuerza", "tu fe", "tu proposito", "tu vida", "tu camino", "tu destino", "tu historia", "tu legado", "tu huella", "tu obra", "tu labor", "tu esfuerzo", "tu trabajo", "tu dedicacion", "tu empeno"],
    "Felicidad": ["tu vida", "tu alma", "tu corazon", "tu mente", "tu ser", "tu espiritu", "tu familia", "tus amigos", "tu camino", "tu destino", "tu proposito", "tu meta", "tu objetivo", "tu exito", "tu triunfo", "tu victoria", "tu avance", "tu progreso", "tu cumplimiento", "tu conquista"],
    "Proposito": ["tu vida", "tu camino", "tu destino", "tu mision", "tu vocacion", "tu llamado", "tu esfuerzo", "tu trabajo", "tu legado", "tu meta", "tu objetivo", "tu exito", "tu triunfo", "tu victoria", "tu avance", "tu progreso", "tu cumplimiento", "tu conquista", "tu realizacion", "tu plenitud"],
    "Optimismo": ["tu futuro", "tu vida", "tu camino", "tu destino", "tu proposito", "tu fe", "tu alma", "tu corazon", "tu esperanza", "tu luz", "tu ilusion", "tu optimismo", "tu confianza", "tu certeza", "tu conviccion", "tu seguridad", "tu firmeza", "tu estabilidad", "tu constancia", "tu perseverancia"],
    "PazInterior": ["tu mente", "tu corazon", "tu alma", "tu espiritu", "tu ser", "tu vida", "tu destino", "tu camino", "tu proposito", "tu felicidad", "tu paz", "tu tranquilidad", "tu serenidad", "tu calma", "tu armonia", "tu equilibrio", "tu sosiego", "tu quietud", "tu placidez", "tu clemencia"],
    "Actitud": ["tu dia", "tu semana", "tu mes", "tu ano", "tu vida", "tu proyecto", "tu meta", "tu objetivo", "tu mision", "tu proposito", "tu camino", "tu destino", "tu exito", "tu triunfo", "tu victoria", "tu avance", "tu progreso", "tu cumplimiento", "tu conquista", "tu realizacion"],
    "Crecimiento": ["tu persona", "tu caracter", "tu mente", "tu espiritu", "tu alma", "tu vida", "tu futuro", "tu camino", "tu destino", "tu mision", "tu meta", "tu objetivo", "tu exito", "tu triunfo", "tu victoria", "tu avance", "tu progreso", "tu cumplimiento", "tu conquista", "tu realizacion"],
    "Cambio": ["tu vida", "tu realidad", "tu futuro", "tu camino", "tu destino", "tu proposito", "tu ser", "tu alma", "tu mente", "tu corazon", "tu espiritu", "tu esencia", "tu verdad", "tu historia", "tu legado", "tu huella", "tu obra", "tu labor", "tu esfuerzo", "tu trabajo"],
    "Libertad": ["tu ser", "tu alma", "tu mente", "tu corazon", "tu espiritu", "tu vida", "tu camino", "tu destino", "tu proposito", "tu verdad", "tu esencia", "tu historia", "tu legado", "tu huella", "tu obra", "tu labor", "tu esfuerzo", "tu trabajo", "tu dedicacion", "tu empeno"],
    "Aprendizaje": ["tu vida", "tu camino", "tu mente", "tu ser", "tu alma", "tu espiritu", "tu destino", "tu proposito", "tu legado", "tu futuro", "tu meta", "tu objetivo", "tu exito", "tu triunfo", "tu victoria", "tu avance", "tu progreso", "tu cumplimiento", "tu conquista", "tu realizacion"],
    "Sabiduria": ["tu vida", "tu camino", "tu destino", "tu proposito", "tu ser", "tu alma", "tu mente", "tu corazon", "tu espiritu", "tu legado", "tu meta", "tu objetivo", "tu exito", "tu triunfo", "tu victoria", "tu avance", "tu progreso", "tu cumplimiento", "tu conquista", "tu realizacion"],
    "Conexion": ["tu vida", "tu camino", "tu destino", "tu proposito", "tu ser", "tu alma", "tu mente", "tu corazon", "tu espiritu", "tu legado", "tu meta", "tu objetivo", "tu exito", "tu triunfo", "tu victoria", "tu avance", "tu progreso", "tu cumplimiento", "tu conquista", "tu realizacion"]
}

# ============================================
# 🗣️ FRASES PARA HUMANIZAR EL TEXTO
# ============================================
INTROS_HUMANAS = [
    "Mira,",
    "La verdad es que",
    "Piensa en esto:",
    "No hay duda de que",
    "A veces",
    "Siempre he creído que",
    "Es curioso, pero",
    "Fíjate:",
    "Resulta que",
    "Lo cierto es que",
    "Sin duda,",
    "Para ser sincero,",
    "Hay que reconocer que",
    "Te invito a reflexionar:",
    "Imagina por un momento",
    "No es casualidad que",
    "Vamos a ver:",
    "Vale la pena recordar que",
    "Lo interesante es que",
    "Por supuesto,"
]

PREGUNTAS_RETORICAS = [
    "¿No te parece?",
    "¿Verdad?",
    "¿No crees?",
    "¿Te suena familiar?",
    "¿Sabes a lo que me refiero?",
    "¿No es así?",
    "¿Te das cuenta?",
    "¿No te hace pensar?",
    "¿Lo ves?",
    "¿No es increíble?"
]

def humanizar_frase(frase):
    """Añade una muletilla o pregunta retórica para sonar más natural."""
    if random.random() < 0.4:
        intro = random.choice(INTROS_HUMANAS)
        frase = f"{intro} {frase[0].lower() + frase[1:] if frase else frase}"
    if random.random() < 0.3:
        frase += " " + random.choice(PREGUNTAS_RETORICAS)
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
        inicio + " " + sujeto + " " + verbo + " " + complemento + "?",
        inicio + " " + sujeto + " " + verbo + " " + complemento + " sin miedo?",
        inicio + " " + sujeto + " " + verbo + " " + complemento + " y alcanzar tus metas?",
        inicio + " " + sujeto + " " + verbo + " " + complemento + " cuando todo parece difícil?",
        inicio + " " + sujeto + " " + verbo + " " + complemento + " a pesar de los obstáculos?"
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
        articulo = "El" if not tema_nombre.endswith(("a", "ad", "ión", "umbre", "dad", "tad", "sis")) else "La"
        if tema_nombre.lower() in ["amor", "cambio", "crecimiento", "proposito", "optimismo", "entusiasmo"]:
            articulo = "El"
        patrones = [
            f"{articulo} {tema_nombre} {random.choice(VERBOS_UNIVERSALES)} {random.choice(COMPLEMENTOS_UNIVERSALES)}.",
            f"Reflexionar sobre {articulo.lower()} {tema_nombre} {random.choice(VERBOS_UNIVERSALES)} {random.choice(COMPLEMENTOS_UNIVERSALES)}.",
            f"Cada día es una oportunidad para transformar {articulo.lower()} {tema_nombre} en {random.choice(COMPLEMENTOS_UNIVERSALES)}.",
            f"{articulo} {tema_nombre} te enseña a {random.choice(VERBOS_UNIVERSALES)} {random.choice(COMPLEMENTOS_UNIVERSALES)}.",
            f"Aceptar {articulo.lower()} {tema_nombre} es el primer paso para {random.choice(VERBOS_UNIVERSALES)} {random.choice(COMPLEMENTOS_UNIVERSALES)}."
        ]
        frase = random.choice(patrones)
    else:
        sujeto = random.choice(sujetos)
        verbo = random.choice(verbos)
        complemento = random.choice(complementos)
        frase = f"{sujeto} {verbo} {complemento}."
    
    if random.random() < 0.7:
        frase = humanizar_frase(frase)
    return frase

def generar_texto_completo(tema_nombre):
    pregunta = generar_pregunta(tema_nombre)
    num_desarrollo = random.choice([6, 7, 8])
    desarrollo = []
    for _ in range(num_desarrollo):
        desarrollo.append(generar_frase_desarrollo(tema_nombre))
    random.shuffle(desarrollo)
    return pregunta, desarrollo

def dividir_en_parrafos(pregunta, desarrollo, num_parrafos):
    """
    Divide el contenido en exactamente num_parrafos párrafos.
    - El primer párrafo es siempre la pregunta.
    - El último párrafo es siempre "Te leo en los comentarios".
    - Los párrafos intermedios se rellenan con las oraciones de desarrollo,
      distribuidas de manera equitativa.
    """
    # 1. Preparar la pregunta como un solo párrafo
    oraciones_pregunta = re.findall(r'[^.!?]+[.!?]', pregunta)
    if not oraciones_pregunta:
        oraciones_pregunta = [pregunta.strip()]
    parrafo_pregunta = " ".join(oraciones_pregunta)
    
    # 2. Extraer oraciones del desarrollo
    texto_desarrollo = " ".join(desarrollo)
    oraciones = re.findall(r'[^.!?]+[.!?]', texto_desarrollo)
    oraciones = [o.strip() for o in oraciones if len(o.strip()) > 5]
    if not oraciones:
        oraciones = ["Sigue adelante con fe y determinación."]
    
    # 3. Mezclar oraciones de desarrollo
    random.shuffle(oraciones)
    
    # 4. Número de párrafos intermedios (total - 2: pregunta y cierre)
    num_intermedios = num_parrafos - 2
    if num_intermedios < 1:
        num_parrafos = 3
        num_intermedios = 1
    
    # 5. Repartir oraciones entre los párrafos intermedios
    total_oraciones = len(oraciones)
    while total_oraciones < num_intermedios:
        oraciones.append("Sigue adelante con fe y determinación.")
        total_oraciones += 1
    
    oraciones_por_parrafo = total_oraciones // num_intermedios
    resto = total_oraciones % num_intermedios
    grupos = []
    indice = 0
    for i in range(num_intermedios):
        extra = 1 if i < resto else 0
        fin = indice + oraciones_por_parrafo + extra
        grupos.append(oraciones[indice:fin])
        indice = fin
    
    parrafos_intermedios = [" ".join(g) for g in grupos]
    
    # 6. Armar lista final: [pregunta] + intermedios + [cierre]
    parrafos = [parrafo_pregunta] + parrafos_intermedios + ["Te leo en los comentarios"]
    
    # Ajustar por si sobra o falta algún párrafo
    if len(parrafos) > num_parrafos:
        parrafos = parrafos[:num_parrafos]
        parrafos[-1] = "Te leo en los comentarios"
    elif len(parrafos) < num_parrafos:
        while len(parrafos) < num_parrafos - 1:
            parrafos.insert(-1, "Sigue adelante con fe y determinación.")
        if len(parrafos) < num_parrafos:
            parrafos.append("Te leo en los comentarios")
    
    return parrafos

def crear_video(pregunta, desarrollo, dia_semana, tema_nombre, numero):
    num_parrafos = random.choice([5, 6, 7])
    duracion_total = random.uniform(70, 85)
    duracion_por_parrafo = duracion_total / num_parrafos
    duraciones = [duracion_por_parrafo] * num_parrafos

    print(f"   🎬 Video {numero} ({dia_semana} - {tema_nombre}) - {num_parrafos} párrafos, {duracion_total:.1f}s")
    print(f"   ⏱️  Cada párrafo: {duracion_por_parrafo:.1f}s")
    os.makedirs("videos", exist_ok=True)

    parrafos = dividir_en_parrafos(pregunta, desarrollo, num_parrafos)

    palabras_clave = (pregunta + " " + " ".join(desarrollo)).split()[:4]
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

        # Dividir el párrafo en líneas
        lineas = textwrap.wrap(parrafo, width=28, break_long_words=False)
        total_lineas = len(lineas)
        if total_lineas == 0:
            lineas = [" "]
            total_lineas = 1

        # Calcular tamaño de fuente
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

        # Calcular posición central inferior
        altura_bloque = total_lineas * (font_size * 1.3)
        y_inicio = 1920 - altura_bloque - 200

        # Dibujar cada línea con borde negro grueso (sin fondo)
        y = y_inicio
        for linea in lineas:
            bbox = draw.textbbox((0, 0), linea, font=font)
            ancho_linea = bbox[2] - bbox[0]
            x = (1080 - ancho_linea) // 2
            # Borde negro grueso (stroke_width=5) y sombra ligera (opcional)
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

    # Limpieza
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
    parser = argparse.ArgumentParser(description="Generador de videos semanales")
    parser.add_argument("--videos", type=int, default=5, help="Número de videos por día")
    parser.add_argument("--tema", type=str, default="todo", help="Tema o 'todo' para aleatorio")
    parser.add_argument("--zip", type=str, help="Nombre del archivo ZIP (sin extensión o con .zip)")
    parser.add_argument("--no-zip", action="store_true", help="No crear ZIP")
    args = parser.parse_args()

    videos_por_dia = args.videos
    tema_input = args.tema

    if args.zip:
        nombre_zip = args.zip if args.zip.endswith(".zip") else args.zip + ".zip"
    else:
        fecha_zip = datetime.now().strftime("%d-%m-%Y")
        nombre_zip = f"Videos-{fecha_zip}.zip"

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
            pregunta, desarrollo = generar_texto_completo(tema_nombre)
            crear_video(pregunta, desarrollo, dia_nombre, tema_nombre, i+1)
            time.sleep(0.5)

    print("\n🎉 ¡Todos los videos generados!")

    if not args.no_zip:
        print(f"📦 Creando ZIP: {nombre_zip} ...")
        with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk("videos"):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), "."))
        print(f"✅ ZIP creado: {nombre_zip}")
        print(f"📁 Revisa la carpeta 'videos' y el archivo '{nombre_zip}'.")
    else:
        print("⏭️  No se creó ZIP (opción --no-zip activada).")
