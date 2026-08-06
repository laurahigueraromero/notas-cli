from datetime import datetime
import pytest
from typer.testing import CliRunner
from notas import almacen, cli

runner = CliRunner()


@pytest.fixture
def home(tmp_path, monkeypatch):
    # La CLI no recibe "base" en sus llamadas a almacen (usa Path.home()
    # internamente), así que redirigimos Path.home() a una carpeta temporal
    # para que estos tests nunca toquen el escritorio real.
    monkeypatch.setattr(almacen.Path, "home", lambda: tmp_path)
    return tmp_path


def test_crear_guarda_titulo_y_cuerpo(home):
    resultado = runner.invoke(
        cli.app, ["crear"], input="Ideas Proyecto\nprimera linea\nsegunda linea\n"
    )

    assert resultado.exit_code == 0
    assert "Nota guardada en:" in resultado.output

    notas = almacen.listar_notas()
    assert len(notas) == 1
    assert "ideas-proyecto" in notas[0].name
    assert notas[0].read_text(encoding="utf-8") == "primera linea\nsegunda linea"


def test_crear_titulo_vacio_no_crea_archivo(home):
    resultado = runner.invoke(cli.app, ["crear"], input="   \n")

    assert resultado.exit_code == 1
    assert "El título no puede estar vacío." in resultado.output
    assert almacen.listar_notas() == []


def test_listar_sin_notas(home):
    resultado = runner.invoke(cli.app, ["listar"])

    assert resultado.exit_code == 0
    assert "No hay ninguna nota todavía." in resultado.output


def test_listar_con_notas_mas_reciente_primero(home):
    almacen.crear_nota("Antigua", "c", fecha=datetime(2026, 1, 1, 9, 0))
    almacen.crear_nota("Reciente", "c", fecha=datetime(2026, 7, 29, 18, 0))

    resultado = runner.invoke(cli.app, ["listar"])

    lineas = [linea for linea in resultado.output.splitlines() if linea.strip()]
    assert "reciente" in lineas[0]
    assert "antigua" in lineas[1]


def test_leer_sin_coincidencias(home):
    resultado = runner.invoke(cli.app, ["leer", "xyz"])

    assert "No se encontró ninguna nota con ese criterio." in resultado.output


def test_leer_una_coincidencia_muestra_contenido_completo(home):
    almacen.crear_nota("Compra", "leche\npan", fecha=datetime(2026, 8, 1, 9, 0))

    resultado = runner.invoke(cli.app, ["leer", "compra"])

    assert "compra" in resultado.output
    assert "leche" in resultado.output
    assert "pan" in resultado.output


def test_leer_varias_coincidencias_lista_sin_mostrar_contenido(home):
    almacen.crear_nota("Ideas proyecto", "cuerpo A", fecha=datetime(2026, 7, 29, 18, 0))
    almacen.crear_nota("Ideas varias", "cuerpo B", fecha=datetime(2026, 7, 30, 10, 0))

    resultado = runner.invoke(cli.app, ["leer", "ideas"])

    assert "Hay varias notas que coinciden" in resultado.output
    assert "ideas-proyecto" in resultado.output
    assert "ideas-varias" in resultado.output
    assert "cuerpo A" not in resultado.output
    assert "cuerpo B" not in resultado.output
