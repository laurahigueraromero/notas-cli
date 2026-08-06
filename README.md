# notas-cli

Un bloc de notas por línea de comandos escrito en Python. Permite crear, listar y leer notas de texto rápidas desde la terminal, sin salir del flujo de trabajo. Las notas se guardan como archivos `.txt` en una carpeta del escritorio, accesibles en cualquier momento.

Este proyecto es, sobre todo, un ejercicio de **Spec-Driven Development (SDD)** y **Test-Driven Development (TDD)**: la especificación se escribió antes que el código, y cada función de la lógica se construyó a partir de un test que fallaba primero. Tras un primer repaso de trazabilidad requisito → test, se hizo una segunda pasada de robustez (ver "Casos límite manejados" más abajo) siguiendo el mismo ciclo.

## El enfoque

En lugar de abrir el editor y empezar a picar código, el proyecto siguió el flujo completo de SDD:

1. **`specs/specs.md.txt`** — el *qué* y el *por qué*: historias de usuario, requisitos funcionales y criterios de aceptación, sin detalles técnicos.
2. **`specs/plan.md.txt`** — el *cómo*: stack, arquitectura, formato de las notas en disco.
3. **`specs/task.md.txt`** — el plan partido en tareas pequeñas, cada una en ciclo TDD, con un mapa explícito requisito → tarea.

Y encima, TDD en toda la capa de datos y en la CLI: primero el test (fase *Red*), luego el código mínimo para que pase (fase *Green*). Todos los tests usan carpetas temporales (`tmp_path` de pytest, o `Path.home()` parcheado con `monkeypatch` para los tests de CLI), así que nunca tocan el escritorio real.

## Requisitos

- Python 3.11 o superior

## Instalación

Clona el repositorio y entra en la carpeta:

```bash
git clone https://github.com/laurahigueraromero/notas-cli.git
cd notas-cli
```

Crea y activa un entorno virtual:

```bash
python -m venv venv
venv\Scripts\activate.bat        # Windows (CMD)
# source venv/bin/activate        # Linux / macOS
```

Instala el proyecto en modo editable:

```bash
python -m pip install -e .
```

Esto registra el comando `notas` dentro del entorno virtual.

## Uso

### Crear una nota

```bash
notas crear
```

Pide el título y luego el cuerpo. El cuerpo puede tener varias líneas; para terminar, se pulsa `Ctrl+Z` y `Enter` (en Windows).

```
Título: ideas para el proyecto
Cuerpo (escribe y pulsa Ctrl+Z + Enter para terminar):
primera idea
segunda idea
^Z
Nota guardada en: C:\Users\...\Desktop\apuntes sueltos\2026-07-30_114523_ideas-para-el-proyecto.txt
```

Un título vacío o compuesto solo de espacios se rechaza con un mensaje claro y no crea ningún archivo.

### Listar todas las notas

```bash
notas listar
```

Muestra las notas ordenadas de la más reciente a la más antigua. Si no hay ninguna, lo indica en vez de mostrar una lista vacía.

### Leer una nota

```bash
notas leer ideas
```

Busca por fecha o por título (sin distinguir mayúsculas/minúsculas). Según el número de coincidencias:

- **Ninguna**: mensaje de error claro, sin crash.
- **Una**: se muestra el nombre y el contenido completo de la nota.
- **Varias**: se listan los nombres para que precises cuál, sin mostrar contenido.

### Borrar una nota

El borrado se hace eliminando el archivo directamente desde la carpeta `apuntes sueltos` del escritorio. Al ser archivos `.txt` normales, la carpeta es la fuente de verdad y el explorador de archivos sirve como interfaz; `notas listar` deja de mostrar cualquier archivo borrado así.

## Cómo funciona por dentro

Cada nota es un archivo `.txt` cuyo **nombre** codifica la identidad, el orden y el título, y cuyo **contenido** es el cuerpo en texto plano:

```
2026-07-30_114523_ideas-para-el-proyecto.txt
└── fecha ──┘ └─hora+seg─┘ └──── título (slug) ────┘
```

La marca de fecha, hora y segundos al principio del nombre cumple dos funciones a la vez: identifica la nota de forma única (los segundos evitan que dos notas con el mismo título creadas en el mismo minuto se sobrescriban) y da el orden cronológico gratis (ordenar los nombres alfabéticamente equivale a ordenar por fecha). No hace falta base de datos: el sistema de archivos es la fuente de verdad.

### Casos límite manejados

Detectados en un repaso de trazabilidad requisito → test y cerrados con TDD (ver `specs/task.md.txt`, Fase 2.5):

- **Colisión de nombres**: la marca de tiempo incluye segundos, así que dos notas con el mismo título en el mismo minuto no se pisan.
- **Caracteres inválidos de Windows** en el título (`< > : " / \ | ? *`): se limpian al generar el slug, para que el título nunca rompa la escritura del archivo.
- **Título vacío**: se valida tanto en la CLI como en la capa de datos (`almacen.crear_nota`), por si se llama directamente sin pasar por la terminal.

## Estructura del proyecto

```
notas-cli/
├── specs/
│   ├── specs.md.txt    # qué y por qué
│   ├── plan.md.txt     # cómo
│   └── task.md.txt     # tareas y mapa requisito -> tarea
├── src/notas/
│   ├── almacen.py      # capa de datos (crear, listar, buscar)
│   └── cli.py          # comandos de terminal (typer)
├── tests/
│   ├── test_almacen.py # tests de la capa de datos
│   └── test_cli.py     # tests de los comandos (typer.testing.CliRunner)
├── pyproject.toml
├── requirements.txt
└── README.md
```

Se separa `cli.py` (interacción con el usuario) de `almacen.py` (lógica de archivos), de modo que los tests de la lógica no dependen de la terminal.

## Ejecutar los tests

```bash
python -m pytest
```

Con cobertura:

```bash
python -m pytest --cov=notas --cov-report=term-missing
```

## Stack

- **Python** — lenguaje
- **Typer** — construcción de la CLI
- **pytest** — tests
- **pytest-cov** — cobertura de tests

## Mejoras futuras

- Hacer que el comando `notas` funcione desde cualquier carpeta (instalación con `pipx` o en el Python global).
- Comando para abrir la carpeta de notas desde la propia app.
