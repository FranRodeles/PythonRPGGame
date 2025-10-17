# launcher.py
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
from Figth.fight import resolve_turn

console = Console()

# ----- estados del launcher -----
# Estos strings son el “modo” actual de la app: menú principal, selección de personaje, etc.
STATE_MAIN = "main"
STATE_CHAR = "characters"

# Archivo de la primera zona del juego. run_game() lo carga con JsonReader.
FIRST_ZONE_FILE = "zona1_afueras_castillo.json"  # archivo inicial en ./Jsons/


def clear():
    """Helper para limpiar pantalla. Usamos esto cada vez que cambiamos de vista."""
    os.system("cls" if os.name == "nt" else "clear")

def level_up_menu(player):
    """
    Menú de subida de nivel con Rich + teclas (↑/↓/Enter/Esc).
    - Este menú NO sube vida: la vida +10 se suma automáticamente al subir de nivel (se hace en Control_vida()).
    - Acá solo se reparten los 3 puntos en: Ataque, Defensa, Magia, Precisión.
    - Este menú corre en su propio mini-loop con su propio Listener.
    - Al salir, se hace clear() para no dejar “basura” visual.
    """
    selected = 0
    confirm = False
    quit_flag = False

    # Opciones de atributos y acción de terminar. Cada ítem: (texto, atributo_del_player, incremento)
    opciones = [
        ("Ataque",    "atk",      1),
        ("Defensa",   "defense",  1),
        ("Magia",     "mage",     1),
        ("Precisión", "accuracy", 1),
        ("Terminar",  None,       None),
    ]

    def on_press(key):
        """
        Listener local para este submenú de level-up.
        Solo mueve cursor y asigna puntos. No sale del programa, solo cierra este submenú.
        """
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

    # Importes locales de Rich para dibujar el panel de este submenú.
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live

    def render_panel():
        """Dibuja el panel del submenú de level-up con las opciones y valores actuales del player."""
        nonlocal selected
        if selected < 0:
            selected = len(opciones) - 1
        if selected >= len(opciones):
            selected = 0

        header = Panel.fit(
            f"[bold green]{player.name}[/bold green]  •  Nivel [cyan]{player.level}[/cyan]\n"
            f"Puntos disponibles: [bold yellow]{player.puntos_atributos}[/bold yellow]",
            border_style="bright_black"
        )

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column(" ", width=3, justify="center")
        table.add_column("Atributo / Acción", style="yellow")
        table.add_column("Valor actual", justify="center")

        # Miro los valores actuales del player para mostrarlos en la tabla
        valores = {
            "atk": player.atk,
            "defense": player.defense,
            "mage": player.mage,
            "accuracy": player.accuracy,
        }

        # Pinto cada fila del selector
        for i, (texto, clave, inc) in enumerate(opciones):
            cursor = "→" if i == selected else " "
            if clave is None:
                table.add_row(cursor, texto, "[dim]-[/dim]")  # “Terminar”
            else:
                table.add_row(cursor, texto, str(valores[clave]))

        footer = Panel(
            "[dim]Usá ↑/↓ para elegir • Enter para asignar • Esc para salir[/dim]",
            border_style="bright_black"
        )

        layout = Table.grid(padding=(0,1))
        layout.add_row(header)
        layout.add_row(table)
        layout.add_row(footer)

        return Panel(layout, border_style="white")

    # Loop del submenú de level-up
    try:
        with Live(render_panel(), refresh_per_second=30, screen=True) as live:
            while True:
                if quit_flag or player.puntos_atributos <= 0:
                    break

                live.update(render_panel())

                if confirm:
                    confirm = False
                    texto, clave, inc = opciones[selected]
                    if clave is None:
                        # “Terminar”
                        break
                    if player.puntos_atributos <= 0:
                        continue
                    current = getattr(player, clave, None)
                    if isinstance(current, int):
                        # Asigno el punto y resto del pool
                        setattr(player, clave, current + inc)
                        player.puntos_atributos -= 1

                time.sleep(0.05)
    finally:
        # Cierro listener local del submenú y limpio pantalla
        listener.stop()
        clear()


# =========================
# GAME LOOP
# =========================

def run_game(player):
    """
    Loop del juego 
    Acá se carga el JSON inicial, se navega por nodos de historia y combate,
    y se integra el motor de pelea externo a través de resolve_turn().

    Flujo general:
      - Renderizamos pantalla según el tipo de nodo (historia/combate).
      - En combate, si el usuario elige “Atacar” y confirma: LLAMAMOS resolve_turn(...)
        resolve_turn actualiza los HP y escribe en combat_log.
      - Control_vida(...) revisa muertes y hace los saltos de nodo.
    """
    reader = JsonReader(Path("./Jsons"))
    reader.load_zone(FIRST_ZONE_FILE)

    # Estado del input para este loop (independiente del launcher)
    selected = 0
    confirm = False
    quit_flag = False

    # Estado de combate e info transitoria por nodo
    in_combat = False
    combat_enemy = None
    player_battle = None
    combat_log = []
    last_node_id = None  # para detectar cuando entramos por primera vez a un nodo y setear batalla

    def Control_vida(nodo):
        """
        Revisa si alguien murió y maneja salto de nodo.
        Devuelve:
          - ("FIN", status): hay que mostrar pantalla FIN y romper el loop de juego
          - ("CONTINUE", status): se saltó a otro nodo distinto de FIN; seguir corriendo
          - ("OK", None): nadie murió; seguir turno a turno
        """
        nonlocal combat_enemy, player_battle, combat_log, in_combat, last_node_id, selected

        # Enemigo murió
        if combat_enemy is not None and combat_enemy.vida <= 0:
            combat_log.append(f"{combat_enemy.name} cae derrotado.")

            # Experiencia y subida de nivel 
            player.experience += 80
            if player.experience >= 100:
                player.experience -= 100
                player.level += 1
                player.puntos_atributos += 3
                player.vida += 10  # +10 vida automática al subir de nivel 
                combat_log.append(
                    f"¡Subiste al nivel {player.level}! +10 VIDA. Puntos para asignar: {player.puntos_atributos}."
                )
                time.sleep(0.6)
                # Abrimos submenú de asignación de puntos
                level_up_menu(player)
                clear()

            # Saltamos al nodo de victoria de este nodo de combate
            next_str = nodo.get("victoria")
            status = reader.jump_to_result(next_str)

            # Limpieza de estado transitorio de combate
            in_combat = False
            last_node_id = None
            selected = 0

            if status == "FIN" or reader.current_node_id is None:
                return ("FIN", status)
            return ("CONTINUE", status)

        # Jugador murió
        if player_battle is not None and player_battle.vida <= 0:
            combat_log.append(f"{player_battle.name} ha sido derrotado.")
            next_str = nodo.get("derrota")
            status = reader.jump_to_result(next_str)
            in_combat = False
            last_node_id = None
            selected = 0
            if status == "FIN" or reader.current_node_id is None:
                return ("FIN", status)
            return ("CONTINUE", status)

        return ("OK", None)

    def on_press(key):
        """
        Listener de teclado para este loop del juego.
        Flechas/W-S mueven el cursor; Enter confirma; Esc sale al menú anterior.
        """
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
        """
        Dibuja la pantalla según el tipo de nodo:
          - En historia: descripción + opciones
          - En combate: panel jugador + panel enemigo + selector (Atacar/Huir) + registro (combat_log)
        Inicializa estado de combate la primera vez que entra a un nodo de tipo "combate".
        """
        nonlocal selected, in_combat, combat_enemy, player_battle, combat_log, last_node_id

        nodo = reader.get_current_node()

        # --- combate ---
        if nodo.get("tipo") == "combate":
            # Si es la primera vez que vemos ESTE nodo, armamos la batalla
            if last_node_id != nodo.get("id"):
                enemigo_raw = nodo["enemigos"][0]
                combat_enemy = Enemy.from_json(enemigo_raw)  # construyo objeto enemigo desde el JSON del nodo
                player_battle = copy.deepcopy(player)        # “snapshot” del player para el combate actual
                combat_log = [nodo.get("descripcion", "¡Combate!")]
                selected = 0
                in_combat = True
                last_node_id = nodo.get("id")

            # Panel jugador (stats visibles)
            player_stats = (
                f"[bold]{player_battle.name}[/bold] ([cyan]{player_battle.type}[/cyan])\n"
                f"LVL={player_battle.level} VIDA={player_battle.vida} ATK={player_battle.atk} "
                f"MAG={player_battle.mage} ACC={player_battle.accuracy} DEF={player_battle.defense}"
            )
            player_panel = Panel(player_stats, title="[bold green]Jugador[/bold green]", border_style="green")

            # Arte ASCII del enemigo 
            ascii_text = ""
            if getattr(combat_enemy, "ascii", None):
                try:
                    p = Path("./Jsons") / combat_enemy.ascii    
                    ascii_text = p.read_text(encoding="utf-8")
                except Exception:
                    ascii_text = ""
            if not ascii_text:
                ascii_text = "[dim]Arte del enemigo no disponible (placeholder)[/dim]"

            # Panel enemigo (stats visibles)
            enemy_stats = (
                f"[bold]{combat_enemy.name}[/bold] ([magenta]{combat_enemy.type}[/magenta])\n"
                f"LVL={combat_enemy.level} VIDA={combat_enemy.vida} ATK={combat_enemy.atk} DEF={combat_enemy.defense} SPD={combat_enemy.spd}"
            )
            enemy_panel = Panel(f"{ascii_text}\n\n{enemy_stats}", title=f"[bold red]Enemigo[/bold red]", border_style="red")

            # Opciones del “menú” de combate
            opciones = ["Atacar", "Huir"]
            if selected < 0:
                selected = len(opciones) - 1
            if selected >= len(opciones):
                selected = 0

            # Tabla de opciones (selector)
            table = Table(show_header=False)
            table.add_column(" ", width=3, justify="center")
            table.add_column("Opción", style="yellow")
            for i, opt in enumerate(opciones):
                cursor = "→" if i == selected else " "
                table.add_row(cursor, opt)

            # Registro de eventos (limito a las últimas 6 líneas para que no explote la UI)
            log_text = "\n".join(combat_log[-6:])
            log_panel = Panel(log_text, title="[bold]Registro[/bold]", border_style="bright_black")

            # Header común
            header = Panel.fit(
                f"[bold red]{reader.zone_name}[/bold red] • [cyan]{reader.current_file}[/cyan] • "
                f"[magenta]Nodo:[/magenta] [white]{nodo['id']}[/white]",
                border_style="bright_black",
            )

            # Composición de layout (header, paneles, opciones, registro)
            layout = Table.grid(padding=(0, 1))
            layout.add_row(header)
            side = Table.grid(expand=True)
            side.add_row(player_panel, enemy_panel)
            layout.add_row(side)
            layout.add_row(Align.center(table))
            layout.add_row(log_panel)

            return Panel(layout, border_style="white")

        # --- historia ---
        # Mismo patrón de navegación por opciones, pero acá no hay combate.
        opciones = nodo.get("opciones", [])
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

    # Loop principal del juego (historia/combate)
    try:
        with Live(render_screen(), refresh_per_second=30, screen=True) as live:
            while True:
                if quit_flag:
                    # Esc o “q”: salimos y volvemos al launcher (menú principal)
                    clear()
                    break

                nodo = reader.get_current_node()

                # --- combate ---
                if nodo.get("tipo") == "combate":
                    live.update(render_screen())
                    if confirm:
                        confirm = False
                        if in_combat and combat_enemy is not None:
                            if selected == 0:  # Atacar
                                # >>> ACÁ SE LLAMA AL MÓDULO DE COMBATE <<<
                                # resolve_turn vive en Figth/fight.py, recibe (player_battle, combat_enemy, combat_log)
                                # y se encarga de calcular quién pega primero, daño, críticos y loguear el resultado.
                                resolve_turn(player_battle, combat_enemy, combat_log)

                                # Después de resolver el turno, chequeamos si alguien murió y saltamos de nodo si corresponde.
                                action, status = Control_vida(nodo)
                                if action == "FIN":
                                    live.update(Panel("[bold green]Fin.[/bold green]", border_style="green"))
                                    while not quit_flag:
                                        time.sleep(0.05)
                                    break
                                elif action == "CONTINUE":
                                    live.update(render_screen())
                                    continue

                            elif selected == 1:  # Huir
                                # Intento simple de escape. Si falla, el enemigo pega “de penalización”.
                                chance = random.random()
                                if chance < 0.5:
                                    combat_log.append(f"{player_battle.name} logra huir con éxito.")
                                    next_str = nodo.get("derrota", "FIN")
                                    status = reader.jump_to_result(next_str)
                                    in_combat = False
                                    last_node_id = None
                                    selected = 0
                                    if status == "FIN" or reader.current_node_id is None:
                                        live.update(Panel("[bold green]Fin.[/bold green]", border_style="green"))
                                        while not quit_flag:
                                            time.sleep(0.05)
                                        break
                                    live.update(render_screen())
                                    continue
                                else:
                                    combat_log.append(f"{player_battle.name} intenta huir pero falla.")
                                    edmg = max(1, combat_enemy.atk - player_battle.defense)
                                    player_battle.vida -= edmg
                                    combat_log.append(f"{combat_enemy.name} te golpea por {edmg} de daño por intentar huir.")
                                    action, status = Control_vida(nodo)
                                    if action == "FIN":
                                        live.update(Panel("[bold green]Fin.[/bold green]", border_style="green"))
                                        while not quit_flag:
                                            time.sleep(0.05)
                                        break
                                    if action == "CONTINUE":
                                        live.update(render_screen())
                                        continue
                                    live.update(render_screen())
                                    time.sleep(0.15)
                                    continue

                # --- historia ---
                # Mismo patrón que siempre: pintamos y si confirman, saltamos de nodo según el índice seleccionado.
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
        # Importante cerrar el listener de este loop para no “robar” teclado al launcher.
        listener.stop()


# =========================
# LAUNCHER (menús)
# =========================

def main():
    """
    Launcher del juego: menú principal + selección de personaje.
    Este loop escucha teclado y, cuando el usuario confirma “Nuevo Juego”, llama a run_game(player).
    """
    state = STATE_MAIN
    running = True

    # Menú principal base (título y opciones)
    text_menu = "[bold red] Divine Light [/bold red]\n[yellow] This Game is Awesome [/yellow]"
    options = {0: "Nuevo Juego", 1: "Cargar Partida", 2: "Salir del Juego"}
    main_menu = Menu(text_menu, options, console)
    main_menu.show()

    # Submenú de personajes (se instancia on-demand)
    char_menu = None
    current_player = None

    def on_press(key):
        """
        Listener del launcher (solo para menús).
        Maneja navegación por el menú principal y el de personajes.
        """
        nonlocal state, running, char_menu, current_player

        # Esc en MAIN: salir
        if key == keyboard.Key.esc and state == STATE_MAIN:
            console.print("[bold red]Saliendo...[/bold red]")
            running = False
            return False

        # ----- MENÚ PRINCIPAL -----
        if state == STATE_MAIN:
            if key == keyboard.Key.up:
                main_menu.move_up()
            elif key == keyboard.Key.down:
                main_menu.move_down()
            elif key == keyboard.Key.enter:
                choice = main_menu.current_choice()
                if choice == 0:
                    # “Nuevo Juego”: creamos/mostramos el selector de personajes
                    if char_menu is None:
                        char_menu = main_character(CHAR_TEXT, CHAR_DATA, console)
                    state = STATE_CHAR
                    char_menu.show()
                elif choice == 1:
                    # Placeholder para “Cargar partida”
                    clear()
                    console.print(Panel("[yellow]Cargar partida en desarrollo.[/yellow]", border_style="yellow"))
                    time.sleep(1.0)
                    main_menu.show()
                elif choice == 2:
                    # Salir
                    console.print("[bold red]Saliendo...[/bold red]")
                    running = False
                    return False

        # ----- SELECCIÓN DE PERSONAJE -----
        elif state == STATE_CHAR:
            if key == keyboard.Key.esc:
                # Volver al principal
                state = STATE_MAIN
                main_menu.show()
            elif key == keyboard.Key.up:
                char_menu.move_up()
            elif key == keyboard.Key.down:
                char_menu.move_down()
            elif key == keyboard.Key.enter:
                # Tomamos el dict del personaje elegido y creamos el Player real (objeto)
                sel = char_menu.get_selected_character()
                current_player = create_player_from_menu_dict(sel)

                # Muestro “ficha” del personaje elegido
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

                # Entramos al game loop. Al salir (Esc dentro del juego), volvemos acá.
                clear()
                run_game(current_player)

                # Al volver del juego, reponemos el menú principal.
                state = STATE_MAIN
                main_menu.show()

        return True

    # Listener del launcher. Mientras “running” sea True, seguimos en este loop de menús.
    with keyboard.Listener(on_press=on_press) as listener:
        while running:
            time.sleep(0.05)


if __name__ == "__main__":
    main()