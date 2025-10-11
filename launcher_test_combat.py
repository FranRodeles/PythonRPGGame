# launcher.py (actualizado - primera etapa de combate)
from pathlib import Path
import os
import time
import random
import copy

from pynput import keyboard
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.live import Live ###### ???

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

def run_game(player):
    """
    Game loop que imita a test.py:
    - Ahora espera recibir el objeto `player` para mostrar stats en combate.
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

    # Estado de combate local
    in_combat = False
    combat_enemy = None
    player_battle = None
    combat_log = []
    last_node_id = None

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
        nonlocal selected
        nodo = reader.get_current_node()

        # --- combate (interfaz activa) ---
        nonlocal selected, in_combat, combat_enemy, player_battle, combat_log, last_node_id
        if nodo.get("tipo") == "combate":
            # inicializar combate al entrar al nodo por primera vez
            if last_node_id != nodo.get("id"):
                enemigo_raw = nodo["enemigos"][0]
                combat_enemy = Enemy.from_json(enemigo_raw)
                player_battle = copy.deepcopy(player)  # copia para la batalla (no tocar el jugador global aún) #########
                combat_log = [nodo.get("descripcion", "¡Combate!")]
                selected = 0
                in_combat = True
                last_node_id = nodo.get("id")

            # Construir panel de jugador
            player_stats = (
                f"[bold]{player_battle.name}[/bold] ([cyan]{player_battle.type}[/cyan])\n"
                f"LVL={player_battle.level} VIDA={player_battle.vida} ATK={player_battle.atk} "
                f"MAG={player_battle.mage} ACC={player_battle.accuracy} DEF={player_battle.defense}"
            )
            player_panel = Panel(player_stats, title="[bold green]Jugador[/bold green]", border_style="green")

            # Intentar cargar arte ASCII del enemigo (si hay archivo)
            ascii_text = ""
            if getattr(combat_enemy, "ascii", None):
                try:
                    p = Path(combat_enemy.ascii)
                    if not p.exists():
                        p = Path("./Ascii") / combat_enemy.ascii
                    if not p.exists():
                        p = Path("./Asciis") / combat_enemy.ascii
                    if not p.exists():
                        p = Path("./Jsons") / combat_enemy.ascii
                    if p.exists():
                        ascii_text = p.read_text(encoding="utf-8")
                except Exception:
                    ascii_text = ""

            if not ascii_text:
                ascii_text = "[dim]Arte del enemigo no disponible (placeholder)[/dim]"

            enemy_stats = (
                f"[bold]{combat_enemy.name}[/bold] ([magenta]{combat_enemy.type}[/magenta])\n"
                f"LVL={combat_enemy.level} VIDA={combat_enemy.vida} ATK={combat_enemy.atk} DEF={combat_enemy.defense} SPD={combat_enemy.spd}"
            )
            enemy_panel = Panel(f"{ascii_text}\n\n{enemy_stats}", title=f"[bold red]Enemigo[/bold red]", border_style="red")

            # Opciones de combate
            opciones = ["Atacar", "Huir"]
            # clamp visual del seleccionado para este menú
            if selected < 0:
                selected = len(opciones) - 1
            if selected >= len(opciones):
                selected = 0

            table = Table(show_header=False)
            table.add_column(" ", width=3, justify="center")
            table.add_column("Opción", style="yellow")
            for i, opt in enumerate(opciones):
                if i == selected:
                    cursor = "→" 
                else:
                    cursor = " "
                table.add_row(cursor, opt)

            # registro (últimas líneas)
            log_text = "\n".join(combat_log[-6:])
            log_panel = Panel(log_text, title="[bold]Registro[/bold]", border_style="bright_black")

            header = Panel.fit(
                f"[bold red]{reader.zone_name}[/bold red] • [cyan]{reader.current_file}[/cyan] • "
                f"[magenta]Nodo:[/magenta] [white]{nodo['id']}[/white]",
                border_style="bright_black",
            )

            layout = Table.grid(padding=(0, 1))
            layout.add_row(header)
            side = Table.grid(expand=True)
            side.add_row(player_panel, enemy_panel)
            layout.add_row(side)
            layout.add_row(Align.center(table))
            layout.add_row(log_panel)

            return Panel(layout, border_style="white")

        # --- historia (como antes) ---
        opciones = nodo.get("opciones", [])
        # clamp visual del seleccionado
        
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
            if i == selected:
                cursor = "→" 
            else:
                selected = " "
            table.add_row(cursor, opt["texto"])

        layout = Table.grid(padding=(0, 1))
        layout.add_row(header)
        layout.add_row(desc_panel)
        layout.add_row(Align.center(table))

        return Panel(layout, border_style="white")

    try:
        with Live(render_screen(), refresh_per_second=30, screen=True) as live: ###### ?? Como funciona
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

                        # Si no hay estado de combate inicializado, lo hará render_screen() al entrar
                        # Procesar la selección en el combate
                        # selected: 0=Atacar, 1=Huir
                        # Variables de batalla están en scope: player_battle, combat_enemy, combat_log
                        if in_combat and combat_enemy is not None:
                            if selected == 0:  # Atacar
                                if combat_enemy.spd <= player_battle.accuracy:
                                # daño simple: atk - def (mínimo 1)
                                    dado = random.randint(1,20)
                                    if dado < 18:
                                        dmg = max(1, player_battle.atk - combat_enemy.defense)
                                        combat_enemy.vida -= dmg
                                        combat_log.append(f"{player_battle.name} ataca y causa {dmg} de daño a {combat_enemy.name}.")
                                    else:
                                        dmg = max(1, player_battle.atk - combat_enemy.defense)
                                        combat_enemy.vida -= (dmg*2)
                                        combat_log.append(f"FELICIDADES {player_battle.name}!!! Lograste un golpe critico, causa {dmg} de daño a {combat_enemy.name}(Eso debio de doler 😬).")
                                
                                elif  combat_enemy.spd > player_battle.accuracy:
                                    dado= random.randint(1,20)
                                    if dado < 19 :  
                                        edmg = max(1, combat_enemy.atk - player_battle.defense)
                                        player_battle.vida -= edmg
                                        combat_log.append(f"{combat_enemy.name} contraataca e inflige {edmg} de daño.")
                                    else:
                                        edmg = max(1, combat_enemy.atk - player_battle.defense)
                                        player_battle.vida -= (edmg*2)
                                        combat_log.append(f"El diavlo loco - {combat_enemy.name} contraataca e inflige un golpe critico de {edmg} de daño.")
                                # revisar si murió el enemigo
                                if combat_enemy.vida <= 0:
                                    combat_log.append(f"{combat_enemy.name} cae derrotado.")
                                    # ir al nodo de victoria (como antes)
                                    next_str = nodo.get("victoria")
                                    status = reader.jump_to_result(next_str)
                                    in_combat = False
                                    last_node_id = None
                                    selected = 0
                                    # manejar FIN como en tu implementación original
                                    if status == "FIN" or reader.current_node_id is None:
                                        live.update(Panel("[bold green]Fin.[/bold green] (Esc para volver)", border_style="green"))
                                        while not quit_flag:
                                            time.sleep(0.05)
                                        break
                                    # si no fue FIN, actualizamos la pantalla y seguimos el loop
                                    live.update(render_screen())
                                    continue

                                
                                if player_battle.vida <= 0:
                                    combat_log.append(f"{player_battle.name} ha sido derrotado.")
                                    next_str = nodo.get("derrota")
                                    status = reader.jump_to_result(next_str)
                                    in_combat = False
                                    last_node_id = None
                                    selected = 0
                                    if status == "FIN" or reader.current_node_id is None:
                                        live.update(Panel("[bold green]Fin.[/bold green] (Esc para volver)", border_style="green"))
                                        while not quit_flag:
                                            time.sleep(0.05)
                                        break
                                    live.update(render_screen())
                                    continue

                            elif selected == 1:  # Huir (intento simple)
                                chance = random.random()
                                if chance < 0.5:
                                    combat_log.append(f"{player_battle.name} logra huir con éxito.")
                                    # Temporal: mapear huir a la rama 'derrota' (ajustar luego)
                                    next_str = nodo.get("derrota", "FIN")
                                    status = reader.jump_to_result(next_str)
                                    in_combat = False
                                    last_node_id = None
                                    selected = 0
                                    if status == "FIN" or reader.current_node_id is None:
                                        live.update(Panel("[bold green]Fin.[/bold green] (Esc para volver)", border_style="green"))
                                        while not quit_flag:
                                            time.sleep(0.05)
                                        break
                                    live.update(render_screen())
                                    continue
                                else:
                                    combat_log.append(f"{player_battle.name} intenta huir pero falla.")
                                    # penalización: enemigo ataca
                                    edmg = max(1, combat_enemy.atk - player_battle.defense)
                                    player_battle.vida -= edmg
                                    combat_log.append(f"{combat_enemy.name} te golpea por {edmg} de daño por intentar huir.")
                                    if player_battle.vida <= 0:
                                        combat_log.append(f"{player_battle.name} ha sido derrotado.")
                                        next_str = nodo.get("derrota")
                                        status = reader.jump_to_result(next_str)
                                        in_combat = False
                                        last_node_id = None
                                        selected = 0
                                        if status == "FIN" or reader.current_node_id is None:
                                            live.update(Panel("[bold green]Fin.[/bold green] (Esc para volver)", border_style="green"))
                                            while not quit_flag:
                                                time.sleep(0.05)
                                            break
                                    live.update(render_screen())
                                    time.sleep(0.15)
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
                run_game(current_player)  # <- ahora se le pasa el jugador seleccionado

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



