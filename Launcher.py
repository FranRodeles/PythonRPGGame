from pathlib import Path
import os
import time

from pynput import keyboard
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.live import Live

from Menu.menu import Menu
from Menu.menu_character import main_character, text as CHAR_TEXT, character as CHAR_DATA
from Character.player import create_player_from_menu_dict
from JsonReaders.reader import JsonReader
from Character.enemy import Enemy


console = Console()

# ----- estados del launcher -----
STATE_MAIN = "main"
STATE_CHAR = "characters"

FIRST_ZONE_FILE = "zona1_tutorial.json"  # archivo inicial en ./Jsons/


def clear():
    os.system("cls" if os.name == "nt" else "clear")


# =========================
# GAME LOOP (como test.py)
# =========================

def run_game():
    """
    Game loop que imita a test.py:
    - Tiene su propio estado de input (selected/confirm/quit_flag)
    - Tiene su propio keyboard.Listener
    - Tiene su propio Live con render_screen()
    Vuelve cuando el jugador pulsa Esc o cuando se llega a FIN.
    """
    reader = JsonReader(Path("./Jsons"))
    reader.load_zone(FIRST_ZONE_FILE)  # arranca en el primer nodo

    selected = 0
    confirm = False
    quit_flag = False

    def on_press(key):
        nonlocal selected, confirm, quit_flag
        try:
            ch = key.char.lower() if hasattr(key, "char") and key.char else None
        except:
            ch = None

        if key == keyboard.Key.up or ch == "w":
            selected -= 1
        elif key == keyboard.Key.down or ch == "s":
            selected += 1
        elif key == keyboard.Key.enter:
            confirm = True
        elif key == keyboard.Key.esc or ch == "q":
            quit_flag = True

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    def render_screen():
        nodo = reader.get_current_node()

        # --- combate (1 enemigo) ---
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
                f"{desc}\n\n{stats_line}\n\n[dim]Enter para continuar...  (Esc para volver al menú)[/dim]",
                title=f"[bold red]Combate contra {enemigo.name}[/bold red]",
                border_style="red"
            )
            return desc_panel

        # --- historia ---
        opciones = nodo.get("opciones", [])
        # clamp visual del seleccionado
        nonlocal selected
        if opciones:
            if selected < 0:
                selected = len(opciones) - 1
            if selected >= len(opciones):
                selected = 0

        header = Panel.fit(
            f"[bold red]{reader.zone_name}[/bold red] • [cyan]{reader.current_file}[/cyan] • "
            f"[magenta]Nodo:[/magenta] [white]{nodo['id']}[/white]",
            border_style="bright_black",
        )

        desc_panel = Panel(
            nodo.get("descripcion", ""),
            title="[bold]Descripción[/bold]",
            border_style="cyan"
        )

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column(" ", width=3, justify="center")
        table.add_column("Opción", style="yellow")
        for i, opt in enumerate(opciones):
            cursor = "→" if i == selected else " "
            table.add_row(cursor, opt["texto"])

        layout = Table.grid(padding=(0, 1))
        layout.add_row(header)
        layout.add_row(desc_panel)
        layout.add_row(Align.center(table))

        return Panel(layout, border_style="white")

    try:
        with Live(render_screen(), refresh_per_second=30, screen=True) as live:
            while True:
                if quit_flag:
                    # salir al menú principal
                    clear()
                    break

                nodo = reader.get_current_node()

                # --- combate ---
                if nodo.get("tipo") == "combate":
                    live.update(render_screen())

                    if confirm:
                        confirm = False
                        # Simulación: siempre victoria (cambiar cuando integren el sistema real)
                        outcome = "victoria"
                        next_str = nodo["victoria"] if outcome == "victoria" else nodo["derrota"]
                        status = reader.jump_to_result(next_str)

                        selected = 0
                        if status == "FIN" or reader.current_node_id is None:
                            live.update(Panel("[bold green]Fin.[/bold green] (Esc para volver)", border_style="green"))
                            # Esperar a que el jugador presione Esc para volver
                            while not quit_flag:
                                time.sleep(0.05)
                            break

                    time.sleep(0.05)
                    continue

                # --- historia ---
                live.update(render_screen())

                if confirm:
                    status = reader.jump_to_by_index(selected)
                    confirm = False
                    selected = 0
                    if status == "FIN" or reader.current_node_id is None:
                        live.update(Panel("[bold green]Fin.[/bold green] (Esc para volver)", border_style="green"))
                        while not quit_flag:
                            time.sleep(0.05)
                        break

                time.sleep(0.05)
    finally:
        listener.stop()


# =========================
# LAUNCHER (menús)
# =========================

def main():
    state = STATE_MAIN
    running = True

    # Menú principal
    text_menu = "[bold red] Divine Light [/bold red]\n[yellow] This Game is Awesome [/yellow]"
    options = {
        0: "Nuevo Juego",
        1: "Cargar Partida",
        2: "Salir del Juego",
    }
    main_menu = Menu(text_menu, options, console)
    main_menu.show()

    # Menú de personajes (on-demand)
    char_menu = None
    current_player = None

    def on_press(key):
        nonlocal state, running, char_menu, current_player

        # Esc en MAIN: salir
        if key == keyboard.Key.esc and state == STATE_MAIN:
            console.print("[bold red]Saliendo...[/bold red]")
            running = False
            return False

        # --- MAIN ---
        if state == STATE_MAIN:
            if key == keyboard.Key.up:
                main_menu.move_up()
            elif key == keyboard.Key.down:
                main_menu.move_down()
            elif key == keyboard.Key.enter:
                choice = main_menu.current_choice()

                if choice == 0:  # Nuevo juego
                    if char_menu is None:
                        char_menu = main_character(CHAR_TEXT, CHAR_DATA, console)
                    state = STATE_CHAR
                    char_menu.show()

                elif choice == 1:  # Cargar (WIP)
                    clear()
                    console.print(Panel("[yellow]Cargar partida: funcionalidad en desarrollo.[/yellow]", border_style="yellow"))
                    time.sleep(1.0)
                    main_menu.show()

                elif choice == 2:  # Salir
                    console.print("[bold red]Saliendo...[/bold red]")
                    running = False
                    return False

        # --- CHAR SELECT ---
        elif state == STATE_CHAR:
            if key == keyboard.Key.esc:
                state = STATE_MAIN
                main_menu.show()
            elif key == keyboard.Key.up:
                char_menu.move_up()
            elif key == keyboard.Key.down:
                char_menu.move_down()
            elif key == keyboard.Key.enter:
                sel = char_menu.get_selected_character()
                current_player = create_player_from_menu_dict(sel)

                clear()
                console.print(Panel(
                    f"[bold green]Seleccionaste:[/bold green] {current_player.name} "
                    f"([cyan]{current_player.type}[/cyan])\n\n"
                    f"LVL={current_player.level} VIDA={current_player.vida} "
                    f"ATK={current_player.atk} MAG={current_player.mage} "
                    f"ACC={current_player.accuracy} DEF={current_player.defense}",
                    title="Jugador creado",
                    border_style="green"
                ))
                time.sleep(0.8)

                # Entrar al game loop estilo test.py
                clear()
                run_game()  # <- vuelve aquí al terminar/escapar

                # Al volver del juego, mostramos de nuevo el menú principal
                state = STATE_MAIN
                main_menu.show()

        return True

    # Listener del launcher (sólo para menús)
    with keyboard.Listener(on_press=on_press) as listener:
        while running:
            time.sleep(0.05)


if __name__ == "__main__":
    main()


