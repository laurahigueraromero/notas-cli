import typer
from notas import almacen

app = typer.Typer(help="Bloc de notas por línea de comandos.", no_args_is_help=True)


@app.command()
def crear():
    """Crea una nota nueva escribiendo título y cuerpo en la terminal."""
    titulo = typer.prompt("Título")

    if not titulo.strip():
        typer.echo("El título no puede estar vacío.")
        raise typer.Exit(code=1)

    typer.echo("Cuerpo (escribe y pulsa Ctrl+Z + Enter para terminar):")
    lineas = []
    while True:
        try:
            linea = input()
            lineas.append(linea)
        except EOFError:
            break

    cuerpo = "\n".join(lineas)
    ruta = almacen.crear_nota(titulo, cuerpo)
    typer.echo(f"Nota guardada en: {ruta}")


@app.command()
def listar():
    """Lista todas las notas, de la más reciente a la más antigua."""
    notas = almacen.listar_notas()
    if not notas:
        typer.echo("No hay ninguna nota todavía.")
        return
    for nota in notas:
        typer.echo(nota.name)


@app.command()
def leer(criterio: str):
    """Muestra el contenido de una nota buscándola por fecha o título."""
    coincidencias = almacen.buscar_notas(criterio)

    if not coincidencias:
        typer.echo("No se encontró ninguna nota con ese criterio.")
        return

    if len(coincidencias) > 1:
        typer.echo("Hay varias notas que coinciden. Precisa cuál con su nombre:")
        for nota in coincidencias:
            typer.echo(f"  {nota.name}")
        return

    nota = coincidencias[0]
    typer.echo(f"--- {nota.name} ---")
    typer.echo(nota.read_text(encoding="utf-8"))