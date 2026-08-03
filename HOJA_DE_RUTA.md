# 🟡 Pac-Man — Hoja de Ruta y División de Trabajo

> Proyecto en pareja · Python 3.10+ · Pygame · 42 Curriculum

Este documento define la **arquitectura**, la **división de trabajo** entre los dos programadores y la **hoja de ruta** por fases. La idea rectora del reparto:

> **Programador A** es dueño de la **simulación** (qué pasa en el juego).
> **Programador B** es dueño de la **presentación y los datos** (cómo se ve y cómo se persiste).
>
> El punto de contacto entre ambos NO es el bucle de juego, sino un **contrato de entidades** fijado de antemano. Esto permite trabajar en paralelo sin pisarse.

---

## 📑 Índice

1. [Principio de diseño](#-principio-de-diseño)
2. [Decisiones técnicas tomadas](#-decisiones-técnicas-tomadas)
3. [Estructura de ficheros](#-estructura-de-ficheros)
4. [El contrato de entidades (leer primero)](#-el-contrato-de-entidades-fijar-antes-de-picar-código)
5. [Programador A — Motor y Simulación](#-programador-a--motor-y-simulación)
6. [Programador B — Sistemas, UI y Datos](#-programador-b--sistemas-ui-y-datos)
7. [Ficheros compartidos](#-ficheros-compartidos)
8. [Hoja de ruta por fases](#-hoja-de-ruta-por-fases)
9. [Checklist de requisitos del subject](#-checklist-de-requisitos-del-subject)

---

## 🎯 Principio de diseño

La clave del proyecto en pareja es la **separación modelo / vista**:

- `core/` y `entities/` (**A**) son **lógica pura, sin Pygame**. Se pueden testear sin abrir ventana.
- `ui/` (**B**) **lee** el estado que produce A y lo dibuja, pero **nunca lo modifica**.

Esto rompe el acoplamiento cruzado: A puede cambiar el interior de `Ghost` mientras respete el contrato de lectura, y B no se entera.

**Regla de oro:** el `renderer` solo lee. El `input_handler` solo traduce teclas a intenciones. La mutación del estado ocurre **únicamente** dentro de `core/`.

---

## ⚙️ Decisiones técnicas tomadas

Estas dos decisiones ya están cerradas y condicionan `core/` y `renderer` a la vez. Van escritas aquí para que ambos las implementéis igual.

### 1. Movimiento: modelo híbrido (celdas para lógica, píxeles para render)

Queremos el aspecto **fluido por píxeles**, pero sin heredar la parte cara (colisiones continuas contra muros). La solución: **la simulación piensa en la rejilla, la pantalla miente suave.**

- Cada entidad guarda su **celda lógica** `(col, row)` y una dirección.
- Se mueve píxel a píxel *interpolando hacia el centro de la celda destino*.
- Cuando llega al centro de una celda (queda **alineada**), y **solo entonces**, toma la siguiente decisión: ¿sigo recto?, ¿giro?, ¿hay intersección?
- El jugador **encola** el giro (input buffering): si pulsas arriba antes de llegar a la intersección, el giro se aplica en cuanto es válido. Esto es lo que hace que se sienta responsive como el original.

> **Patrón clave para A:** las decisiones de navegación (colisiones, IA, comer pacgums) se toman **solo al alinear con el centro de una celda**, nunca a mitad de píxel. Así toda la lógica difícil razona en celdas discretas, que es mucho más simple.

### 2. Tiempo real con `dt` (delta time)

El juego avanza por tiempo real, no por turnos de tick:

```python
dt = clock.tick(60) / 1000.0   # segundos desde el último frame
dt = min(dt, 0.05)             # clamp: evita teletransportes si un frame laguea
game.update(dt)
```

- Cada entidad se mueve `velocidad * dt` píxeles → el juego va igual de rápido en cualquier máquina.
- Todos los temporizadores (timer de nivel de 90s, frightened mode, respawn de fantasmas a los 5-10s) acumulan `dt`.
- **El clamp de `dt` es obligatorio**: sin él, un frame lento (lag, arrastrar la ventana) genera un `dt` enorme que puede cruzar una entidad a través de un muro.

---

## 📁 Estructura de ficheros

```
pacman/
│
├── pac-man.py                    # [B] Entry point principal (exigido por el subject)
├── config.json                   # [B] Archivo de configuración de ejemplo
├── Makefile                      # [C] Reglas obligatorias: install, run, debug, clean, lint
├── README.md                     # [C] Archivo con la estructura exigida (description, highscore, maze...)
├── pyproject.toml                # [B] Dependencias (pygame, flake8, mypy)
├── .gitignore                    # [B] Exclusión de __pycache__, .mypy_cache, etc.
│
├── project_management/           # [C] Directorio obligatorio para evidencias de gestión
│   ├── timeline_gantt.pdf        # Cronograma o Gantt
│   ├── risk_analysis.md          # Análisis de riesgos
│   └── team_organization.md      # Organización del equipo
│
├── src/                          # Código fuente modular
│   ├── __init__.py
│   ├── app.py                    # [B] Orquestador de alto nivel + FSM de estados (bucle principal)
│   ├── states.py                 # [C] Enum GameState + contrato de entidades (interfaz común)
│   │
│   ├── core/                     # [A] Simulación pura, SIN Pygame
│   │   ├── __init__.py
│   │   ├── game.py               # [A] Estado del mundo + update(dt): el "modelo"
│   │   ├── level.py              # [A] Un nivel: grid, pacgums, timer, condición de victoria
│   │   └── progression.py        # [A] Secuencia de niveles, seed fija->aleatoria, score/vidas
│   │
│   ├── entities/                 # [A] Clases del juego
│   │   ├── __init__.py
│   │   ├── entity.py             # [A] Clase base: celda, píxeles, dirección, contrato común
│   │   ├── player.py             # [A] Lógica de Pac-Man, movimiento, vidas, respawn
│   │   ├── ghost.py              # [A] FSM IA: chase / frightened / eaten / respawn en esquina
│   │   └── collectibles.py       # [A] Pacgums y Super-pacgums
│   │
│   ├── level_manager/            # [B]
│   │   ├── __init__.py
│   │   └── maze_loader.py        # [B] Wrapper para integrar el paquete externo A-Maze-ing
│   │
│   ├── ui/                       # [B] Renderizado e interfaz gráfica (Pygame)
│   │   ├── __init__.py
│   │   ├── renderer.py           # [B] Dibujado en pantalla (solo LEE del modelo de A)
│   │   ├── menus.py              # [B] Menú principal, Pausa, Game Over, Victoria, nombre
│   │   ├── hud.py                # [B] Display in-game de score, vidas, nivel y tiempo
│   │   └── input_handler.py      # [B] Teclado -> intenciones (no muta entidades)
│   │
│   └── systems/
│       ├── __init__.py
│       ├── config_parser.py      # [B] Lectura de JSON, limpieza de comentarios y defaults
│       ├── highscore.py          # [B] Lógica persistente para leer/guardar el Top 10
│       └── cheat_mode.py         # [A] Flags que la simulación consulta (invencibilidad, skip...)
│
├── tests/                        # Programas de prueba con pytest (no evaluados pero sugeridos)
│   ├── test_config.py            # [B]
│   ├── test_highscore.py         # [B]
│   └── test_progression.py       # [A] Determinista con seed fija
│
└── packaging/                    # Scripts/specs para el despliegue en Steam o Itch.io
    └── build.py                  # [B] Script de empaquetado (PyInstaller)
```

**Leyenda:** `[A]` Programador A · `[B]` Programador B · `[C]` Compartido

---

## 🤝 El contrato de entidades (FIJAR ANTES DE PICAR CÓDIGO)

**Esta es la decisión más importante del proyecto en pareja.** Antes de repartir, acordad qué expone cada entidad para que el `renderer` sepa dibujar sin conocer la lógica interna. Si esto está fijado el día 1, A y B trabajan en paralelo sin bloquearse. Si no, os pisáis constantemente.

Como el movimiento es híbrido (celda lógica + píxeles de render), el contrato refleja ambas cosas:

```python
# Lo que TODA entidad expone:
entity.cell: tuple[int, int]     # celda lógica (col, row) — la decide core/ (A)
entity.px: float                 # posición en píxeles para dibujar — la lee renderer (B)
entity.py: float
entity.direction: Direction      # UP | DOWN | LEFT | RIGHT
entity.sprite_id: str            # qué sprite dibujar

# Player, además:
player.lives: int

# Ghost, además:
ghost.state: GhostState          # CHASE | FRIGHTENED | EATEN -> color/sprite
```

> **Quién escribe qué:** `core/` (A) decide sobre `cell` y actualiza `px/py` interpolando hacia el centro de la celda destino. `renderer` (B) **solo lee** `px/py` y `sprite_id`. Sigue siendo separación limpia modelo/vista.

Vive en `src/states.py`, que es el fichero que editáis **juntos** al inicio y casi no volvéis a tocar. Es vuestra "interfaz" común.

---

## 🔴 Programador A — Motor y Simulación

**Responsabilidad global:** toda la lógica de qué ocurre en el juego. Complejidad algorítmica: IA, colisiones, progresión de niveles. Sin una sola línea de Pygame en `core/` ni `entities/`.

### `src/core/game.py` — El modelo del mundo
El corazón de la simulación.
- `update(dt)`: avanza un tick — interpola posiciones en píxeles, y **al alinear con el centro de celda** resuelve colisiones y decisiones de navegación.
- Mantiene referencias al `Player`, la lista de `Ghost`, los `collectibles` y el `level` actual.
- Detecta condiciones: vida perdida, nivel completado, game over.
- Consulta `cheat_mode` para saber si aplicar invencibilidad, freeze, etc.

### `src/core/level.py` — Un nivel individual
- Contiene el grid del laberinto (recibido del `maze_loader` de B).
- Coloca pacgums en los corredores y super-pacgums en las 4 esquinas.
- Gestiona el **timer del nivel** (límite de tiempo, ej. 90s, acumulando `dt`).
- Sabe cuándo el nivel está completado (todos los pacgums comidos).

### `src/core/progression.py` — Secuencia de niveles
- Genera al menos 10 niveles.
- **Nivel 1 con seed fija** (ej. 42), niveles siguientes con **seed aleatoria**.
- Mantiene **score y vidas persistentes** entre niveles.
- Decide qué pasa al agotarse el tiempo (reiniciar nivel / terminar / etc.).

### `src/entities/entity.py` — Clase base
- `cell (col, row)`, `px/py` en píxeles, `direction`, contrato común que hereda el resto.
- Lógica de interpolación píxel→centro de celda compartida por todas las entidades.

### `src/entities/player.py` — Pac-Man
- Movimiento en 4 direcciones (solo por corredores, no atraviesa muros).
- **Input buffering**: encola el giro y lo aplica al alinear con la intersección.
- Gestión de vidas (empieza con 3).
- Respawn en el centro del laberinto al perder una vida.

### `src/entities/ghost.py` — IA de fantasmas
- **FSM de estados:** `CHASE` (persigue) / `FRIGHTENED` (huye, comestible) / `EATEN` (vuelve a su esquina) / respawn.
- Movimiento autónomo por corredores; decide dirección **solo en intersecciones** (al alinear con celda).
- Lógica de persecución (definidla vosotros: distancia, aleatoria, etc.).
- Respawn en su esquina tras ser comido (ej. tras 5-10s, con `dt` acumulado).

### `src/entities/collectibles.py` — Coleccionables
- `Pacgum` (+X puntos) y `SuperPacgum` (+Y puntos, activa modo frightened).

### `src/systems/cheat_mode.py` — Modo trucos
- Flags que la simulación consulta: invencibilidad, saltar nivel, congelar fantasmas, vidas extra, velocidad aumentada.
- **Debe ayudar de verdad al revisor** a probar todas las features rápido.

### `tests/test_progression.py`
- Test determinista de la progresión usando la seed fija.

---

## 🔵 Programador B — Sistemas, UI y Datos

**Responsabilidad global:** entrada del programa, configuración, integración externa (maze), persistencia, y toda la presentación gráfica. Más ficheros, pero más mecánicos y con menos interdependencia interna.

### `pac-man.py` — Entry point
- Procesa el argumento de consola (exactamente 1: el config).
- Valida que sea un `.json` existente.
- Arranca `src/app.py`. Cualquier error se maneja limpio, **nunca traceback**.

### `src/app.py` — Orquestador + FSM de aplicación
- Contiene el bucle `while running` de Pygame y el cálculo de `dt` (con clamp).
- **FSM de estados de aplicación:** menú ↔ juego ↔ pausa ↔ game over ↔ victoria.
- Cuando el estado es "jugando", delega en `core/game.update(dt)` de A.
- Gestiona las transiciones entre pantallas.

### `src/systems/config_parser.py` — Parser de config
- **Strip de líneas que empiezan por `#`** (comentarios), *después* `json.loads`.
  > ⚠️ `config.json` con comentarios NO es JSON válido: hay que preprocesar antes de parsear. No uses `json.load` directo.
- Asigna defaults robustos y hace **clamp** de valores inválidos.
- Ignora claves desconocidas. Nunca crashea.

### `src/level_manager/maze_loader.py` — Adapter A-Maze-ing
- Integra el paquete externo asignado **sin modificarlo**.
- Fuerza `PERFECT = False` (corredores compatibles con Pac-Man).
- Tu loader se adapta a **su** interfaz, no al revés.
- Si el generador falla, error limpio.

### `src/ui/renderer.py` — Renderizado
- Dibuja el mapa, tiles, jugador, fantasmas y coleccionables.
- **Solo LEE `px/py` y `sprite_id` del modelo de A.** Nunca lo modifica.

### `src/ui/menus.py` — Menús
- Menú principal (start, ver highscores, instrucciones, exit), pausa, game over, victoria.
- Input del nombre del jugador para el highscore.

### `src/ui/hud.py` — HUD en juego
- Muestra score, vidas, nivel actual, tiempo restante. Siempre visible durante el juego.

### `src/ui/input_handler.py` — Manejo de input
- Traduce teclas (WASD/flechas, pausa, teclas de cheat) a **intenciones** (`MOVE_UP`, `PAUSE`, `CHEAT_SKIP`).
- **No toca entidades directamente.** A consume esas intenciones en su update (y las encola con input buffering).

### `src/systems/highscore.py` — Highscores
- Top 10 persistente (json en disco).
- Robusto a errores de fichero (ausente, formato inválido).
- Nombres: máx 10 chars, alfanuméricos y espacios. Scores: enteros no negativos.
- Carga al inicio, guarda al final. Se muestra en el menú principal.

### `packaging/build.py` — Empaquetado
- Script PyInstaller para subir a Itch.io/Steam (build gratis, privado/unlisted).

### `tests/test_config.py` y `tests/test_highscore.py`
- Tests deterministas del parser y del sistema de scores. Baratos y quedan bien en defensa.

---

## 🤍 Ficheros compartidos

| Fichero | Descripción |
|---|---|
| `src/states.py` | Enum `GameState` + el **contrato de entidades**. Se edita junto al inicio. |
| `Makefile` | Reglas obligatorias: `install`, `run`, `debug`, `clean`, `lint`. |
| `README.md` | Todas las secciones que exige el subject (ver checklist). |
| `project_management/` | Kanban, timeline/Gantt, análisis de riesgos, organización del equipo. |

---

## 🗺️ Hoja de ruta por fases

### Fase 0 — Cimientos (juntos)
- [ ] Definir `states.py`: enum de estados + **contrato de entidades** (celda + píxeles).
- [ ] Confirmar las dos decisiones técnicas (ya cerradas: híbrido celdas/píxeles + tiempo real con dt).
- [ ] Montar esqueleto de carpetas con `__init__.py` y stubs.
- [ ] Makefile + pyproject + .gitignore funcionando (`make lint` pasa en vacío).
- [ ] Acordar el paquete A-Maze-ing asignado y su interfaz.

### Fase 1 — Verticales mínimos en paralelo
- **A:** `entity.py` + `player.py` con movimiento híbrido (interpolación píxel + decisión al alinear) sobre un grid dummy.
- **B:** `config_parser.py` + `maze_loader.py` devolviendo un grid real.
- [ ] **Integración:** el player de A se mueve suave sobre el maze de B.

### Fase 2 — Núcleo jugable
- **A:** `game.py` con colisiones + pacgums + `ghost.py` (chase básico, decisión en intersecciones).
- **B:** `renderer.py` dibujando el modelo por píxeles + `app.py` con bucle, `dt` y estado "jugando".
- [ ] **Integración:** partida jugable de un nivel, se ve fluida en pantalla.

### Fase 3 — Sistemas
- **A:** frightened mode + eaten/respawn de fantasmas + `progression.py` (10 niveles) + `cheat_mode.py`.
- **B:** `hud.py` + `menus.py` (menú, pausa, game over, victoria) + `highscore.py`.
- [ ] **Integración:** flujo completo menú → juego → fin → nombre → menú.

### Fase 4 — Pulido y entrega
- [ ] `packaging/build.py` y build subido a Itch.io/Steam.
- [ ] Tests (`test_config`, `test_highscore`, `test_progression`).
- [ ] README completo + `project_management/`.
- [ ] `make lint` limpio (flake8 + mypy), docstrings PEP 257.
- [ ] Config faulty testeada (defaults, clamp, claves desconocidas, sin traceback).

---

## ✅ Checklist de requisitos del subject

**Técnicos (transversales, desde el minuto uno):**
- [ ] Python 3.10+
- [ ] flake8 limpio
- [ ] Type hints + `mypy` sin errores (correr **antes de cada commit**, no al final)
- [ ] Docstrings PEP 257 (Google o NumPy style)
- [ ] Manejo de excepciones con try-except, context managers para recursos
- [ ] **Nunca un traceback** durante la review

**Makefile:** `install`, `run`, `debug` (pdb), `clean`, `lint` (`flake8 .` + `mypy .` con flags)

**Gameplay:**
- [ ] Config JSON con comentarios `#`, defaults robustos, clamp
- [ ] Integración A-Maze-ing sin modificarlo, `PERFECT=False`
- [ ] Highscore persistente Top 10, validación nombres/scores
- [ ] ≥10 niveles, seed fija en nivel 1, timer por nivel, score/vidas persistentes
- [ ] Player: 3 vidas, movimiento por corredores, respawn al centro
- [ ] Ghosts: chase / frightened / eaten / respawn en esquina
- [ ] Pacgums + super-pacgums en las 4 esquinas
- [ ] Cheat mode que ayude de verdad al revisor
- [ ] UI: menú, HUD, pausa, game over, victoria
- [ ] Empaquetado en plataforma pública (Itch.io/Steam)

**README** debe incluir: primera línea en cursiva con los logins, Description, Instructions, Resources (con **uso de IA** especificado), Configuration, Highscore, Maze Generation, Implementation, General Software Architecture, Project Management.

---

## 📝 Notas finales

- **El guion en `pac-man.py`:** funciona como entry point ejecutado directamente, pero **no lo importes** desde tests (`import pac-man` no es válido en Python por el guion).
- **No borréis todos los tests** al final: `test_config` y `test_highscore` son deterministas, baratos y quedan bien en defensa.
- **Corred `make lint` continuamente.** El type-checking al final es una pesadilla; con mypy desde el día uno es trivial.
- **La simulación piensa en la rejilla, la pantalla miente suave.** Si en algún momento os cuesta una colisión o una decisión de IA, es señal de que estáis razonando en píxeles donde deberíais razonar en celdas.
