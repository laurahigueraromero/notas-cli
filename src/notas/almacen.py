from pathlib import Path
import unicodedata
from datetime import datetime

def obtener_carpeta(base=None):
    # base: dónde vive la carpeta de notas.
    #   - En los tests le pasamos una carpeta temporal (para no ensuciar
    #     el escritorio real).
    #   - En el uso real no se pasa nada, así que usa el escritorio.
    if base is None:
        base = Path.home() / "Desktop"

    carpeta = Path(base) / "apuntes sueltos"

    # Crea la carpeta si no existe. Con parents y exist_ok no falla
    # aunque ya exista o falten carpetas intermedias.
    carpeta.mkdir(parents=True, exist_ok=True)

    return carpeta

# Caracteres que Windows no permite en nombres de archivo.
CARACTERES_INVALIDOS_WINDOWS = '<>:"/\\|?*'

def slugify(titulo):
    # 1. Quitar acentos: "café" -> "cafe"
    #    Descompone cada letra acentuada en (letra + acento) y luego
    #    elimina los acentos, quedándose solo con la letra base.
    sin_acentos = unicodedata.normalize("NFKD", titulo)
    sin_acentos = sin_acentos.encode("ascii", "ignore").decode("ascii")

    # 2. Minúsculas y quitar espacios sobrantes de los extremos
    texto = sin_acentos.lower().strip()

    # 3. Quitar caracteres inválidos para nombres de archivo en Windows,
    #    para que el título nunca rompa la escritura del archivo.
    for caracter in CARACTERES_INVALIDOS_WINDOWS:
        texto = texto.replace(caracter, "")

    # 4. Reemplazar grupos de espacios por un solo guion
    #    (split() sin argumentos parte por cualquier cantidad de espacios
    #    y descarta los vacíos, así "varios   espacios" -> ["varios","espacios"])
    palabras = texto.split()
    return "-".join(palabras)

def componer_nombre(fecha, titulo):
    # fecha.strftime da formato a la fecha/hora según un patrón:
    #   %Y = año (2026)   %m = mes (07)   %d = día (29)
    #   %H = hora (18)    %M = minutos (30)  %S = segundos (45)
    # Los segundos evitan que dos notas con el mismo título creadas dentro
    # del mismo minuto generen el mismo nombre de archivo y se pisen.
    # Resultado: "2026-07-29_183045"
    marca = fecha.strftime("%Y-%m-%d_%H%M%S")

    # Reutilizamos slugify (T1.2) para limpiar el título
    titulo_slug = slugify(titulo)

    # Juntamos todo y añadimos la extensión .txt
    return f"{marca}_{titulo_slug}.txt"

def crear_nota(titulo, cuerpo, base=None, fecha=None):
    # Título obligatorio también a nivel de datos, no solo en la CLI:
    # cualquier código que use almacen.py directamente debe quedar protegido.
    if not titulo or not titulo.strip():
        raise ValueError("El título no puede estar vacío.")

    # Si no nos dan fecha, usamos la de ahora (uso real).
    # En los tests le pasamos una fecha fija para controlar el orden.
    if fecha is None:
        fecha = datetime.now()

    carpeta = obtener_carpeta(base=base)
    nombre = componer_nombre(fecha, titulo)
    ruta = carpeta / nombre
    ruta.write_text(cuerpo, encoding="utf-8")
    return ruta

def listar_notas(base=None):
    carpeta = obtener_carpeta(base=base)
    notas = sorted(carpeta.glob("*.txt"), reverse=True)
    return notas

def buscar_notas(criterio, base=None):
    # Partimos de todas las notas ya ordenadas (reutilizamos T1.5)
    todas = listar_notas(base=base)

    # Nos quedamos solo con aquellas cuyo nombre de archivo contenga
    # el criterio. Pasamos ambos a minúsculas para que la búsqueda no
    # distinga mayúsculas ("Ideas" encuentra "ideas").
    criterio = criterio.lower()
    coincidencias = [nota for nota in todas if criterio in nota.name.lower()]

    return coincidencias
