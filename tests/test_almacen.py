from pathlib import Path
from notas import almacen
from datetime import datetime

def test_obtener_carpeta_crea_si_no_existe(tmp_path):
    carpeta = almacen.obtener_carpeta(base=tmp_path)
    assert carpeta.exists()
    assert carpeta.name == "apuntes sueltos"

def test_slugify_normaliza_titulo():
    assert almacen.slugify("Ideas Proyecto") == "ideas-proyecto"
    assert almacen.slugify("Café con leche") == "cafe-con-leche"
    assert almacen.slugify("  Varios   espacios  ") == "varios-espacios"

def test_componer_nombre_archivo():
    fecha = datetime(2026, 7, 29, 18, 30)
    nombre = almacen.componer_nombre(fecha, "Ideas Proyecto")
    assert nombre == "2026-07-29_1830_ideas-proyecto.txt"

def test_crear_nota_escribe_archivo(tmp_path):
    ruta = almacen.crear_nota(
        "Ideas Proyecto",
        "primera linea\nsegunda linea",
        base=tmp_path,
    )
    # El archivo debe existir en el disco
    assert ruta.exists()
    # Y su contenido debe ser exactamente el cuerpo que pasamos
    assert ruta.read_text(encoding="utf-8") == "primera linea\nsegunda linea"

def test_listar_notas_orden_reciente_primero(tmp_path):
    # Creamos 3 notas con fechas distintas (se las pasamos a mano
    # para controlar el orden en el test)
    almacen.crear_nota("Antigua", "cuerpo", base=tmp_path,
                        fecha=datetime(2026, 1, 1, 9, 0))
    almacen.crear_nota("Reciente", "cuerpo", base=tmp_path,
                        fecha=datetime(2026, 7, 29, 18, 0))
    almacen.crear_nota("Media", "cuerpo", base=tmp_path,
                        fecha=datetime(2026, 4, 15, 12, 0))

    notas = almacen.listar_notas(base=tmp_path)

    # Deben salir 3, y la primera debe ser la más reciente (julio)
    assert len(notas) == 3
    assert "reciente" in notas[0].name
    assert "antigua" in notas[2].name
def test_buscar_notas(tmp_path):
    almacen.crear_nota("Ideas proyecto", "c", base=tmp_path,
                       fecha=datetime(2026, 7, 29, 18, 0))
    almacen.crear_nota("Ideas varias", "c", base=tmp_path,
                       fecha=datetime(2026, 7, 30, 10, 0))
    almacen.crear_nota("Compra", "c", base=tmp_path,
                       fecha=datetime(2026, 8, 1, 9, 0))

    # Por título: "ideas" aparece en dos notas -> 2 resultados
    assert len(almacen.buscar_notas("ideas", base=tmp_path)) == 2

    # Por título único: "compra" -> 1 resultado
    assert len(almacen.buscar_notas("compra", base=tmp_path)) == 1

    # Por fecha: "2026-08" -> 1 resultado (la de agosto)
    assert len(almacen.buscar_notas("2026-08", base=tmp_path)) == 1

    # Algo que no existe -> 0 resultados
    assert len(almacen.buscar_notas("xyz", base=tmp_path)) == 0