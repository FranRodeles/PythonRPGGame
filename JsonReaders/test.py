# test.py
# test.py (encabezado correcto)
from pathlib import Path
import sys

# Añadí la carpeta raíz del repo al sys.path
ROOT = Path(__file__).resolve().parents[1]   # .../PythonRPGGame/
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# recién ahora importás paquetes hermanos
from pynput import keyboard
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.align import Align
import time

from JsonReaders.reader import JsonReader
from Character.enemy import Enemy

     

# -------- init ----------
console = Console()
reader = JsonReader(Path("./Jsons"))
reader.load_zone("zona1_tutorial.json")  # arranca en el primer nodo

# -------- input state ----------
selected = 0
confirm = False
quit_flag = False

def on_press(key):
    global selected, confirm, quit_flag
    try:
        ch = key.char.lower() if hasattr(key, "char") and key.char else None
    except:
        ch = None

    # mover selección
    if key == keyboard.Key.up or ch == "w":
        selected -= 1
    elif key == keyboard.Key.down or ch == "s":
        selected += 1
    # confirmar
    elif key == keyboard.Key.enter:
        confirm = True
    # salir
    elif key == keyboard.Key.esc or ch == "q":
        quit_flag = True

listener = keyboard.Listener(on_press=on_press)
listener.start()

# -------- render ----------
def render_screen():
    nodo = reader.get_current_node()

    # si es combate, mostramos enemigos en vez de opciones
        # si es combate, mostramos 1 enemigo fijo
    if nodo.get("tipo") == "combate":
        enemigo_raw = nodo["enemigos"][0]
        enemigo = Enemy.from_json(enemigo_raw)

        desc = nodo.get("descripcion", "")
        stats_line = (
            f"- {enemigo.name}: LVL={enemigo.level} "
            f"VIDA={enemigo.vida} ATK={enemigo.atk} DEF={enemigo.defense} SPD={enemigo.spd} "
            f"XP={enemigo.xp_reward}"
        )

        desc_panel = Panel(
            f"{desc}\n\n{stats_line}\n\n[dim]Enter para continuar...[/dim]",
            title=f"[bold red]Combate contra {enemigo.name}[/bold red]",
            border_style="red"
        )
        return desc_panel

    # si es historia
    opciones = nodo.get("opciones", [])

    # corregir selección fuera de rango
    global selected
    if opciones:
        if selected < 0:
            selected = len(opciones) - 1
        if selected >= len(opciones):
            selected = 0

    # header
    header = Panel.fit(
        f"[bold red]{reader.zone_name}[/bold red] • [cyan]{reader.current_file}[/cyan] • "
        f"[magenta]Nodo:[/magenta] [white]{nodo['id']}[/white]",
        border_style="bright_black",
    )

    # descripción
    desc_panel = Panel(
        nodo.get("descripcion", ""),
        title="[bold]Descripción[/bold]",
        border_style="cyan"
    )

    # opciones
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column(" ", width=3, justify="center")
    table.add_column("Opción", style="yellow")
    for i, opt in enumerate(opciones):
        cursor = "→" if i == selected else " "
        table.add_row(cursor, opt["texto"])

    layout = Table.grid(padding=(0,1))
    layout.add_row(header)
    layout.add_row(desc_panel)
    layout.add_row(Align.center(table))

    return Panel(layout, border_style="white")

# -------- loop ----------
try:
    with Live(render_screen(), refresh_per_second=30, screen=True) as live:
        while True:
            if quit_flag:
                break

            nodo = reader.get_current_node()

                        # --- caso combate (1 enemigo) ---
            if nodo.get("tipo") == "combate":
                enemigo = Enemy.from_json(nodo["enemigos"][0])  # 1 solo

                # 1) Mostrar pantalla de combate (render_screen ya la arma)
                live.update(render_screen())

                # 2) Esperar Enter para continuar (debug: mostrar objeto)
                if confirm:
                    confirm = False
                    console.print(f"[yellow]DEBUG[/yellow] {enemigo}")
                    time.sleep(0.3)

                    # 3) Simular resultado y transicionar
                    outcome = "victoria"  # o "derrota" para probar
                    next_str = nodo["victoria"] if outcome == "victoria" else nodo["derrota"]
                    status = reader.jump_to_result(next_str)

                    selected = 0
                    if status == "FIN" or reader.current_node_id is None:
                        live.update(Panel("[bold green]Fin.[/bold green]", border_style="green"))
                        time.sleep(1.0)
                        break

                # Mientras no se apriete Enter, seguir mostrando el panel de combate
                continue


            # --- caso historia ---
            live.update(render_screen())

            # confirmar selección
            if confirm:
                status = reader.jump_to_by_index(selected)
                confirm = False
                selected = 0
                if status == "FIN" or reader.current_node_id is None:
                    live.update(Panel("[bold green]Fin.[/bold green]", border_style="green"))
                    time.sleep(1.0)
                    break

            time.sleep(0.05)
finally:
    listener.stop()





