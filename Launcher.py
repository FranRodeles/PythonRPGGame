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
STATE_MAIN = "main"        # Estado: estamos en el menú principal
STATE_CHAR = "characters"  # Estado: estamos en el menú de selección de personaje

FIRST_ZONE_FILE = "zona1_tutorial.json"  # archivo inicial en ./Jsons/ (punto de entrada de la historia)


def clear():
    """
    Limpiar la consola. Esto se usa n todo el proyecto para “refrescar” la pantalla
    sin depender de Rich cuando NO estamos usando Live. En Windows usa 'cls', en Unix 'clear'.
    """
    os.system("cls" if os.name == "nt" else "clear")


# =========================
# GAME LOOP (como test.py)
# =========================

def run_game():
    """
    Game loop , o sea, el corredor de nodos:
      - Tiene su propio estado de input (selected/confirm/quit_flag).
      - Tiene su propio keyboard.Listener (↑/↓/Enter/Esc).
      - Tiene su propio Live con render_screen() para dibujar (como en test.py).
    Sale cuando el jugador aprieta Esc (quit_flag) o cuando el JSON devuelve FIN.

    Flujo:
      1) Cargamos el lector de JSON y la primera zona.
      2) render_screen() arma el panel según el nodo (historia vs combate).
      3) En el while, si es historia: ↑/↓ mueven selección, Enter salta de nodo.
         Si es combate: mostramos enemigo y con Enter simulamos victoria/derrota
         para probar el salto 'victoria'/'derrota' del JSON.
    """
    reader = JsonReader(Path("./Jsons"))                  # 1) Lector de zonas
    reader.load_zone(FIRST_ZONE_FILE)  # arranca en el primer nodo

    # Estado de input local del loop 
    selected = 0
    confirm = False
    quit_flag = False

    def on_press(key):
        """
        Listener interno SOLO para este loop del juego.
        - ↑ / 'w': subir opción
        - ↓ / 's': bajar opción
        - Enter: confirmar (seteamos confirm=True)
        - Esc / 'q': salir del loop (seteamos quit_flag=True)
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


    # Arrancamos el listener SOLO para el game loop.
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    def render_screen():
        """
        Dibuja la pantalla actual (un Panel):
          - Si el nodo es de 'combate': muestra el enemigo (1) y sus stats.
          - Si el nodo es de 'historia': muestra descripción + tabla de opciones,
            con la fila seleccionada marcada con '→'.
        """
        nodo = reader.get_current_node()

        # --- combate (1 enemigo) ---
        if nodo.get("tipo") == "combate":
            enemigo_raw = nodo["enemigos"][0]     # por ahora 1 solo enemigo
            enemigo = Enemy.from_json(enemigo_raw)  # acá convertimos dict -> objeto Enemy

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
        # clamp visual del seleccionado — este es el wrap-around de la selección
        nonlocal selected
        if opciones:
            if selected < 0:
                selected = len(opciones) - 1
            if selected >= len(opciones):
                selected = 0

        # Header con metadatos de la zona y el nodo actual
        header = Panel.fit(
            f"[bold red]{reader.zone_name}[/bold red] • [cyan]{reader.current_file}[/cyan] • "
            f"[magenta]Nodo:[/magenta] [white]{nodo['id']}[/white]",
            border_style="bright_black",
        )

        # Descripción principal del nodo
        desc_panel = Panel(
            nodo.get("descripcion", ""),
            title="[bold]Descripción[/bold]",
            border_style="cyan"
        )

        # Tabla de opciones. Marcamos la seleccionada con "→"
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column(" ", width=3, justify="center")
        table.add_column("Opción", style="yellow")
        for i, opt in enumerate(opciones):
            cursor = "→" if i == selected else " "
            table.add_row(cursor, opt["texto"])

        # Layout final para devolver un único Panel
        layout = Table.grid(padding=(0, 1))
        layout.add_row(header)
        layout.add_row(desc_panel)
        layout.add_row(Align.center(table))

        return Panel(layout, border_style="white")

    try:
        # Live mantiene la pantalla “viva” . Solo actualizamos el Panel.
        with Live(render_screen(), refresh_per_second=30, screen=True) as live:
            while True:
                if quit_flag:
                    # salir al menú principal si apretaron Esc en el loop
                    clear()
                    break

                nodo = reader.get_current_node()

                # --- combate ---
                if nodo.get("tipo") == "combate":
                    live.update(render_screen())  # redibuja panel de combate

                    if confirm:
                        confirm = False
                        # Simulación: por ahora victoria. Acá luego va el sistema real de combate.
                        outcome = "victoria"
                        next_str = nodo["victoria"] if outcome == "victoria" else nodo["derrota"]
                        status = reader.jump_to_result(next_str)

                        # Reseteo de selección cuando cambiamos de nodo
                        selected = 0
                        if status == "FIN" or reader.current_node_id is None:
                            # Mensaje final y esperar Esc para salir al menú
                            live.update(Panel("[bold green]Fin.[/bold green] (Esc para volver)", border_style="green"))
                            while not quit_flag:
                                time.sleep(0.05)
                            break

                    time.sleep(0.05)
                    continue  # seguimos al próximo ciclo sin pasar por historia

                # --- historia ---
                live.update(render_screen())  # redibuja panel de historia

                if confirm:
                    status = reader.jump_to_by_index(selected)  # mover según opción elegida
                    confirm = False
                    selected = 0
                    if status == "FIN" or reader.current_node_id is None:
                        live.update(Panel("[bold green]Fin.[/bold green] (Esc para volver)", border_style="green"))
                        while not quit_flag:
                            time.sleep(0.05)
                        break

                time.sleep(0.05)
    finally:
        # Al salir del loop, apagamos el listener del juego sí o sí.
        listener.stop()


# LAUNCHER (menús)
def main():
    """
    Launcher del juego:
      - Maneja el menú principal (Nuevo juego / Cargar / Salir).
      - En 'Nuevo juego', abre el menú de personajes.
      - Al confirmar personaje, entra al game loop (run_game) y cuando éste termina, vuelve al menú principal.

    Ojo: acá el listener es SOLO para menús. El game loop tiene su propio listener (aislamos responsabilidades).
    """
    state = STATE_MAIN
    running = True

    # Menú principal: texto y opciones
    text_menu = "[bold red] Divine Light [/bold red]\n[yellow] This Game is Awesome [/yellow]"
    options = {
        0: "Nuevo Juego",
        1: "Cargar Partida",
        2: "Salir del Juego",
    }
    main_menu = Menu(text_menu, options, console)
    main_menu.show()

    # Menú de personajes (se crea on-demand)
    char_menu = None
    current_player = None

    def on_press(key):
        """
        Listener del LAUNCHER (no del game loop). Solo maneja:
          - Navegación en MAIN (↑/↓/Enter/Esc).
          - Navegación en CHAR (↑/↓/Enter/Esc).
          - En Enter con personaje, crea el objeto Player desde el dict del menú
            y llama a run_game() (que es el “test.py embebido”).
        """
        nonlocal state, running, char_menu, current_player

        # Esc en MAIN: salir del programa
        if key == keyboard.Key.esc and state == STATE_MAIN:
            console.print("[bold red]Saliendo...[/bold red]")
            running = False
            return False

        # --- MAIN ---
        # Menú principal con sus opciones (mover y confirmar)
        if state == STATE_MAIN:
            if key == keyboard.Key.up:
                main_menu.move_up()
            elif key == keyboard.Key.down:
                main_menu.move_down()
            elif key == keyboard.Key.enter:
                choice = main_menu.current_choice()

                if choice == 0:  # Nuevo juego -> ir a selección de personaje
                    if char_menu is None:
                        char_menu = main_character(CHAR_TEXT, CHAR_DATA, console)
                    state = STATE_CHAR
                    char_menu.show()

                elif choice == 1:  # Cargar 
                    clear()
                    console.print(Panel("[yellow]Cargar partida: funcionalidad en desarrollo.[/yellow]", border_style="yellow"))
                    time.sleep(1.0)
                    main_menu.show()

                elif choice == 2:  # Salir
                    console.print("[bold red]Saliendo...[/bold red]")
                    running = False
                    return False

        # --- CHAR SELECT ---
        # Cuando apretamos Enter, creamos el Player con create_player_from_menu_dict(sel)
        # (diccionario -> objeto) y arrancamos el game loop.
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

                # Entrar al game loop estilo test.py (se bloquea hasta que volvemos)
                clear()
                run_game()  # <- vuelve aquí al terminar/escapar

                # Al volver del juego, regresamos al menú principal
                state = STATE_MAIN
                main_menu.show()

        return True
    # La función (interna) se encuentra en línea 200

    # Listener del launcher (sólo para menús). El while mantiene vivo el programa.
    with keyboard.Listener(on_press=on_press) as listener:
        while running:
            time.sleep(0.05)



if __name__ == "__main__":
    main()  # Punto de entrada: arranca el launcher con su listener de menús.


