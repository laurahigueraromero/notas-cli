from pathlib import Path
from notas import almacen
from datetime import datetime
import pytest

def test_obtener_carpeta_crea_si_no_existe(tmp_path):
    carpeta = almacen.obtener_carpeta(base=tmp_path)
    assert carpeta.exists()
    assert carpeta.name == "apuntes sueltos"

def test_slugify_normaliza_titulo():
    assert almacen.slugify("Ideas Proyecto") == "ideas-proyecto"
    assert almacen.slugify("Café con leche") == "cafe-con-leche"
    assert almacen.slugify("  Varios   espacios  ") == "varios-espacios"

def test_componer_nombre_archivo():
    # La marca incluye segundos para que dos notas con el mismo título
    # en el mismo minuto no generen el mismo nombre de archivo.
    fecha = datetime(2026, 7, 29, 18, 30, 45)
    nombre = almacen.componer_nombre(fecha, "Ideas Proyecto")
    assert nombre == "2026-07-29_183045_ideas-proyecto.txt"

def test_crear_nota_no_sobrescribe_mismo_titulo_mismo_minuto(tmp_path):
    # Dos notas, mismo título, mismo minuto, distinto segundo:
    # deben quedar como dos archivos distintos, no debe perderse la primera.
    ruta1 = almacen.crear_nota(
        "Idea", "primera", base=tmp_path,
        fecha=datetime(2026, 7, 29, 18, 30, 1),
    )
    ruta2 = almacen.crear_nota(
        "Idea", "segunda", base=tmp_path,
        fecha=datetime(2026, 7, 29, 18, 30, 2),
    )

    assert ruta1 != ruta2
    assert ruta1.exists()
    assert ruta2.exists()
    assert ruta1.read_text(encoding="utf-8") == "primera"
    assert ruta2.read_text(encoding="utf-8") == "segunda"

def test_slugify_elimina_caracteres_invalidos_windows():
    resultado = almacen.slugify('Pregunta: ¿qué "importante"? <ok> | fin*')
    caracteres_invalidos = '<>:"/\\|?*'
    assert not any(caracter in resultado for caracter in caracteres_invalidos)

def test_crear_nota_titulo_vacio_lanza_error(tmp_path):
    with pytest.raises(ValueError):
        almacen.crear_nota("   ", "cuerpo", base=tmp_path)

    # No debe haber creado ningún archivo en la carpeta.
    carpeta = almacen.obtener_carpeta(base=tmp_path)
    assert list(carpeta.glob("*.txt")) == []

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

def test_buscar_notas_criterio_en_mayusculas(tmp_path):
    almacen.crear_nota("Ideas proyecto", "c", base=tmp_path,
                        fecha=datetime(2026, 7, 29, 18, 0))

    # El criterio en mayúsculas debe encontrar igual la nota.
    assert len(almacen.buscar_notas("IDEAS", base=tmp_path)) == 1

def test_listar_notas_carpeta_vacia(tmp_path):
    assert almacen.listar_notas(base=tmp_path) == []

def test_crear_nota_cuerpo_vacio(tmp_path):
    # RF1: el cuerpo es opcional.
    ruta = almacen.crear_nota("Solo titulo", "", base=tmp_path)
    assert ruta.exists()
    assert ruta.read_text(encoding="utf-8") == ""

def test_listar_notas_no_incluye_archivo_borrado_manualmente(tmp_path):
    ruta1 = almacen.crear_nota("Uno", "c", base=tmp_path,
                                fecha=datetime(2026, 1, 1, 9, 0))
    ruta2 = almacen.crear_nota("Dos", "c", base=tmp_path,
                                fecha=datetime(2026, 1, 2, 9, 0))

    ruta1.unlink()  # simula borrar el archivo desde la carpeta (criterio A2)

    notas = almacen.listar_notas(base=tmp_path)
    assert len(notas) == 1
    assert notas[0] == ruta2