# launcher.py (con inventario integrado)
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
from rich.live import Live

from Menu.menu import Menu
from Menu.menu_character import main_character, text as CHAR_TEXT, character as CHAR_DATA
from Character.player import create_player_from_menu_dict
from JsonReaders.reader import JsonReader
from Character.enemy import Enemy

console = Console()

STATE_MAIN = "main"
STATE_CHAR = "characters"
FIRST_ZONE_FILE = "zona1_tutorial.json"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

# =========================
# GAME LOOP
# =========================
def run_game(player):
    reader = JsonReader(Path("./Jsons"))
    reader.load_zone(FIRST_ZONE_FILE)

    selected = 0
    confirm = False
    quit_flag = False

    # Combate
    in_combat = False
    combat_enemy = None
    player_battle = None
    combat_log = []
    last_node_id = None

    # Inventario
    in_inventory = False
    inventory_selected = 0

    # Inicializar inventario si no existe
    if not hasattr(player, "inventory"):
        player.inventory = [
            {"name": "Poción Pequeña", "effect": "heal", "value": 20},
            {"name": "Poción Grande", "effect": "heal", "value": 50},
        ]

    def on_press(key):
        nonlocal selected, confirm, quit_flag, in_inventory, inventory_selected
        try:
            ch = key.char.lower() if hasattr(key, "char") and key.char else None
        except:
            ch = None

        if in_inventory:
            if key == keyboard.Key.up or ch == "w":
                inventory_selected -= 1
            elif key == keyboard.Key.down or ch == "s":
                inventory_selected += 1
            elif key == keyboard.Key.enter:
                confirm = True
            elif key == keyboard.Key.esc or ch == "q":
                in_inventory = False
        else:
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

    def render_inventory():
        nonlocal inventory_selected
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column(" ", width=3, justify="center")
        table.add_column("Item", style="yellow")
        for i, item in enumerate(player.inventory):
            cursor = "→" if i == inventory_selected else " "
            table.add_row(cursor, f"{item['name']} ({item['effect']}: {item['value']})")

        player_stats = (
            f"[bold]{player.name}[/bold] ([cyan]{player.type}[/cyan])\n"
            f"LVL={player.level} VIDA={player.vida} ATK={player.atk} "
            f"MAG={player.mage} ACC={player.accuracy} DEF={player.defense}"
        )
        player_panel = Panel(player_stats, title="[bold green]Jugador[/bold green]", border_style="green")

        layout = Table.grid(padding=(0,1))
        layout.add_row(Panel("[bold yellow]Inventario[/bold yellow]", border_style="yellow"))
        layout.add_row(player_panel)
        layout.add_row(Align.center(table))
        return Panel(layout, border_style="white")

    def render_screen():
        nonlocal selected, in_combat, combat_enemy, player_battle, combat_log, last_node_id, in_inventory, inventory_selected

        nodo = reader.get_current_node()

        # Inventario activo
        if in_inventory:
            return render_inventory()

        # --- Combate ---
        if nodo.get("tipo") == "combate":
            if last_node_id != nodo.get("id"):
                enemigo_raw = nodo["enemigos"][0]
                combat_enemy = Enemy.from_json(enemigo_raw)
                player_battle = copy.deepcopy(player)
                combat_log = [nodo.get("descripcion", "¡Combate!")]
                selected = 0
                in_combat = True
                last_node_id = nodo.get("id")

            player_stats = (
                f"[bold]{player_battle.name}[/bold] ([cyan]{player_battle.type}[/cyan])\n"
                f"LVL={player_battle.level} VIDA={player_battle.vida} ATK={player_battle.atk} "
                f"MAG={player_battle.mage} ACC={player_battle.accuracy} DEF={player_battle.defense}"
            )
            player_panel = Panel(player_stats, title="[bold green]Jugador[/bold green]", border_style="green")

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
                ascii_text = "[dim]Arte del enemigo no disponible[/dim]"

            enemy_stats = (
                f"[bold]{combat_enemy.name}[/bold] ([magenta]{combat_enemy.type}[/magenta])\n"
                f"LVL={combat_enemy.level} VIDA={combat_enemy.vida} ATK={combat_enemy.atk} DEF={combat_enemy.defense} SPD={combat_enemy.spd}"
            )
            enemy_panel = Panel(f"{ascii_text}\n\n{enemy_stats}", title="[bold red]Enemigo[/bold red]", border_style="red")

            opciones = ["Atacar", "Huir", "Inventario"]
            selected = selected % len(opciones)

            table = Table(show_header=False)
            table.add_column(" ", width=3, justify="center")
            table.add_column("Opción", style="yellow")
            for i, opt in enumerate(opciones):
                cursor = "→" if i == selected else " "
                table.add_row(cursor, opt)

            log_text = "\n".join(combat_log[-6:])
            log_panel = Panel(log_text, title="[bold]Registro[/bold]", border_style="bright_black")

            header = Panel.fit(
                f"[bold red]{reader.zone_name}[/bold red] • [cyan]{reader.current_file}[/cyan] • "
                f"[magenta]Nodo:[/magenta] [white]{nodo['id']}[/white]",
                border_style="bright_black",
            )

            layout = Table.grid(padding=(0,1))
            layout.add_row(header)
            side = Table.grid(expand=True)
            side.add_row(player_panel, enemy_panel)
            layout.add_row(side)
            layout.add_row(Align.center(table))
            layout.add_row(log_panel)

            return Panel(layout, border_style="white")

        # --- Historia ---
        opciones = nodo.get("opciones", [])
        opciones.append({"texto": "Abrir Inventario", "tipo": "inventario"})
        if opciones:
            selected = selected % len(opciones)

        header = Panel.fit(
            f"[bold red]{reader.zone_name}[/bold red] • [cyan]{reader.current_file}[/cyan] • "
            f"[magenta]Nodo:[/magenta] [white]{nodo['id']}[/white]",
            border_style="bright_black",
        )

        desc_panel = Panel(nodo.get("descripcion",""), title="[bold]Descripción[/bold]", border_style="cyan")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column(" ", width=3, justify="center")
        table.add_column("Opción", style="yellow")
        for i,opt in enumerate(opciones):
            cursor = "→" if i==selected else " "
            table.add_row(cursor,opt["texto"])

        layout = Table.grid(padding=(0,1))
        layout.add_row(header)
        layout.add_row(desc_panel)
        layout.add_row(Align.center(table))
        return Panel(layout, border_style="white")

    try:
        with Live(render_screen(), refresh_per_second=30, screen=True) as live:
            while True:
                if quit_flag:
                    clear()
                    break

                nodo = reader.get_current_node()

                if in_combat:
                    live.update(render_screen())
                    if confirm:
                        confirm = False
                        # Inventario en combate
                        if selected == 2:
                            in_inventory = True
                            inventory_selected = 0
                            continue
                        elif selected == 0:  # Atacar
                            dmg = max(1, player_battle.atk - combat_enemy.defense)
                            combat_enemy.vida -= dmg
                            combat_log.append(f"{player_battle.name} ataca e inflige {dmg} a {combat_enemy.name}")
                        elif selected == 1:  # Huir
                            chance = random.random()
                            if chance < 0.5:
                                combat_log.append(f"{player_battle.name} huye con éxito")
                                next_str = nodo.get("derrota","FIN")
                                reader.jump_to_result(next_str)
                                in_combat = False
                                last_node_id = None
                            else:
                                combat_log.append(f"{player_battle.name} falla al intentar huir")
                    continue

                # Historia: abrir inventario
                opciones = nodo.get("opciones", [])
                opciones.append({"texto": "Abrir Inventario", "tipo": "inventario"})
                if confirm:
                    confirm = False
                    if opciones[selected]["tipo"]=="inventario":
                        in_inventory=True
                        inventory_selected=0
                        continue
                    reader.jump_to_by_index(selected)
                    selected=0

                live.update(render_screen())
                time.sleep(0.05)
    finally:
        listener.stop()


# =========================
# LAUNCHER
# =========================
def main():
    state = STATE_MAIN
    running = True
    text_menu = "[bold red] Divine Light [/bold red]\n[yellow] This Game is Awesome [/yellow]"
    options = {0:"Nuevo Juego",1:"Cargar Partida",2:"Salir del Juego"}
    main_menu = Menu(text_menu, options, console)
    main_menu.show()
    char_menu = None
    current_player = None

    def on_press(key):
        nonlocal state, running, char_menu, current_player
        if key == keyboard.Key.esc and state==STATE_MAIN:
            console.print("[bold red]Saliendo...[/bold red]")
            running=False
            return False

        if state==STATE_MAIN:
            if key==keyboard.Key.up:
                main_menu.move_up()
            elif key==keyboard.Key.down:
                main_menu.move_down()
            elif key==keyboard.Key.enter:
                choice=main_menu.current_choice()
                if choice==0:
                    if char_menu is None:
                        char_menu = main_character(CHAR_TEXT, CHAR_DATA, console)
                    state=STATE_CHAR
                    char_menu.show()
                elif choice==1:
                    clear()
                    console.print(Panel("[yellow]Cargar partida: funcionalidad en desarrollo.[/yellow]", border_style="yellow"))
                    time.sleep(1.0)
                    main_menu.show()
                elif choice==2:
                    console.print("[bold red]Saliendo...[/bold red]")
                    running=False
                    return False

        elif state==STATE_CHAR:
            if key==keyboard.Key.esc:
                state=STATE_MAIN
                main_menu.show()
            elif key==keyboard.Key.up:
                char_menu.move_up()
            elif key==keyboard.Key.down:
                char_menu.move_down()
            elif key==keyboard.Key.enter:
                sel = char_menu.get_selected_character()
                current_player = create_player_from_menu_dict(sel)
                clear()
                console.print(Panel(
                    f"[bold green]Seleccionaste:[/bold green] {current_player.name} ([cyan]{current_player.type}[/cyan])\n"
                    f"LVL={current_player.level} VIDA={current_player.vida} ATK={current_player.atk} MAG={current_player.mage} "
                    f"ACC={current_player.accuracy} DEF={current_player.defense}",
                    title="Jugador creado", border_style="green"
                ))
                time.sleep(0.8)
                clear()
                run_game(current_player)
                state=STATE_MAIN
                main_menu.show()
        return True

    with keyboard.Listener(on_press=on_press) as listener:
        while running:
            time.sleep(0.05)

if __name__=="__main__":
    main()
