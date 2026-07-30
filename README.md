# notas-cli

Un bloc de notas por línea de comandos escrito en Python. Permite crear, listar y leer notas de texto rápidas desde la terminal, sin salir del flujo de trabajo. Las notas se guardan como archivos `.txt` en una carpeta del escritorio, accesibles en cualquier momento.

Este proyecto es, sobre todo, un ejercicio de **Spec-Driven Development (SDD)** y **Test-Driven Development (TDD)**: la especificación se escribió antes que el código, y cada función de la lógica se construyó a partir de un test que fallaba primero.

## El enfoque

En lugar de abrir el editor y empezar a picar código, el proyecto siguió el flujo completo de SDD:

1. **`specs/spec.md`** — el *qué* y el *por qué*: historias de usuario, requisitos funcionales y criterios de aceptación, sin detalles técnicos.
2. **`specs/plan.md`** — el *cómo*: stack, arquitectura, formato de las notas en disco.
3. **`specs/tasks.md`** — el plan partido en tareas pequeñas, cada una en ciclo TDD.

Y encima, TDD en toda la capa de datos: primero el test (fase *Red*), luego el código mínimo para que pase (fase *Green*). Los seis tests usan carpetas temporales, así que nunca tocan el escritorio real.

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
Nota guardada en: C:\Users\...\Desktop\apuntes sueltos\2026-07-30_1145_ideas-para-el-proyecto.txt
```

### Listar todas las notas

```bash
notas listar
```

Muestra las notas ordenadas de la más reciente a la más antigua.

### Leer una nota

```bash
notas leer ideas
```

Busca por fecha o por título. Si hay varias coincidencias, las lista para que precises cuál; si no hay ninguna, avisa con un mensaje claro.

### Borrar una nota

El borrado se hace eliminando el archivo directamente desde la carpeta `apuntes sueltos` del escritorio. Al ser archivos `.txt` normales, la carpeta es la fuente de verdad y el explorador de archivos sirve como interfaz.

## Cómo funciona por dentro

Cada nota es un archivo `.txt` cuyo **nombre** codifica la identidad, el orden y el título, y cuyo **contenido** es el cuerpo en texto plano:

```
2026-07-30_1145_ideas-para-el-proyecto.txt
└── fecha ──┘ └hora┘ └──── título (slug) ────┘
```

La marca de fecha y hora al principio del nombre cumple dos funciones a la vez: identifica la nota de forma única y da el orden cronológico gratis (ordenar los nombres alfabéticamente equivale a ordenar por fecha). No hace falta base de datos: el sistema de archivos es la fuente de verdad.

## Estructura del proyecto

```
notas-cli/
├── specs/
│   ├── spec.md         # qué y por qué
│   ├── plan.md         # cómo
│   └── tasks.md        # tareas
├── src/notas/
│   ├── almacen.py      # capa de datos (crear, listar, buscar)
│   └── cli.py          # comandos de terminal (typer)
├── tests/
│   └── test_almacen.py # 6 tests de la capa de datos
├── pyproject.toml
├── requirements.txt
└── README.md
```

Se separa `cli.py` (interacción con el usuario) de `almacen.py` (lógica de archivos), de modo que los tests de la lógica no dependen de la terminal.

## Ejecutar los tests

```bash
python -m pytest
```

## Stack

- **Python** — lenguaje
- **Typer** — construcción de la CLI
- **pytest** — tests

## Mejoras futuras

- Hacer que el comando `notas` funcione desde cualquier carpeta (instalación con `pipx` o en el Python global).
- Comando para abrir la carpeta de notas desde la propia app.
