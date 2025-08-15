#!/usr/bin/env python3  # Shebang: permite ejecutar el script con Python 3 directamente desde la terminal

from pynput import keyboard  # Importa la librería para escuchar eventos del teclado (globales)

from rich.console import Console  # Rich: consola enriquecida
from rich.panel import Panel       # Rich: paneles con borde y título
from rich.text import Text         # Rich: manejo de texto con estilos
from rich.columns import Columns   # Rich: disposición en columnas
from rich import box               # Rich: estilos de bordes
import os                          # Módulo del sistema operativo (limpiar pantalla, listar archivos, etc.)
import random                      # Generación de números aleatorios
import time                        # Pausas (sleep) y tiempos
import sys                         # Interfaz con el intérprete de Python
import subprocess                  # Ejecutar comandos externos del sistema
import re                          # Expresiones regulares

sys.path.append("Characters")  # Agrega la carpeta Characters al path de importación
sys.path.append("Adventures")  # Agrega la carpeta Adventures al path de importación
sys.path.append("Saves")       # Agrega la carpeta Saves al path de importación
try:
    import characters as cha    # Importa tu módulo de personajes
    import adventures as adv    # Importa tu módulo de aventuras
    import saves as sav         # Importa tu módulo de guardado/carga
except ModuleNotFoundError:
    print("Couldn't find the necessary functions, closing the game...")  # Mensaje si faltan módulos
    time.sleep(2)               # Espera 2 segundos
    sys.exit()                  # Sale del programa ordenadamente


class GameState:
    def __init__(self):
        self.next_encounter = "first_encounter"  # Siguiente encuentro a resolver (clave en el dict de la aventura)
        self.game_over = False                    # Flag del fin del juego
        # NOTA: en tiempo de ejecución se agregan más atributos, p.ej. self.character, self.adventure


class Menu:
    def __init__(self, text, options, console, game_window):
        self.text = text                          # Texto a mostrar encima de opciones
        self.options = options                    # Dict: clave interna -> texto visible
        self.current_option = 0                   # Índice de la opción seleccionada
        self.choice_made = False                  # (No usado directamente) bandera de elección
        self.console = console                    # Instancia de Rich Console
        self.game_window = game_window            # Nombre de ventana activa del juego (para filtrar teclas)

    def print_menu(self):
        self.console.print(Panel(self.text, width=64), justify="center")  # Muestra panel con el texto del menú

    def print_options(self):
        current_option_key = list(self.options.keys())[self.current_option]  # Clave de la opción actual
        options_text = ""                                                   # Acumula el texto formateado
        for option in self.options:                                          # Recorre opciones en orden de inserción
            if option == current_option_key:
                options_text = options_text + "> " + self.options[option] + " <\n"  # Resalta opción activa
            else:
                options_text = options_text + self.options[option] + "\n"           # Opción normal
        options_text = options_text.rstrip("\n")                                      # Quita salto final

        self.console.print(                                                         
            Panel(Text(options_text, justify="center"), box=box.SIMPLE, width=64),  # Panel simple con opciones
            justify="center",
        )

    def on_press(self, key):
        if get_active_window_title() == self.game_window:      # Solo reacciona si la ventana activa es el juego
            if key == keyboard.Key.up:                         # Flecha arriba: subir selección
                if self.current_option > 0:
                    self.current_option = self.current_option - 1
                os.system("clear")                            # Limpia la terminal
                self.print_menu()                              # Re-dibuja menú
                self.print_options()                           # Re-dibuja opciones

            elif key == keyboard.Key.down:                     # Flecha abajo: bajar selección
                if self.current_option < len(self.options) - 1:
                    self.current_option = self.current_option + 1
                os.system("clear")
                self.print_menu()
                self.print_options()

            elif key == keyboard.Key.enter:                    # Enter: confirma
                return False                                   # Detiene el listener (salir de listener.join)

            else:                                              # Cualquier otra tecla: refresca
                os.system("clear")
                self.print_menu()
                self.print_options()

    def choice(self):
        with keyboard.Listener(on_press=self.on_press) as listener:  # Inicia escucha de teclado
            listener.join()                                          # Bloquea hasta que on_press devuelva False

        return list(self.options.keys())[self.current_option]        # Devuelve la clave elegida


class Encounter(Menu):
    def __init__(self, name, text, options, results, console, game_window):
        self.name = name                 # Nombre del encuentro (clave identificadora)
        self.results = results           # Dict: opción -> [siguiente_encuentro] o [enemigo, siguiente]
        Menu.__init__(self, text, options, console, game_window)  # Inicializa como menú

    def resolve_encounter(self, game_state):
        encounter_resolved = False

        while encounter_resolved is False:
            os.system("clear")              # Limpia pantalla
            self.print_menu()                # Muestra texto del encuentro
            self.print_options()             # Muestra opciones

            choice = self.choice()           # Espera elección del jugador

            if choice != "menu":            # Si no es opción de abrir menú del juego
                result = self.results[choice]  # Obtiene resultado asociado

                if len(result) == 1:         # Caso: solo cambia al siguiente encuentro
                    game_state.next_encounter = result[0]
                    encounter_resolved = True
                else:
                    enemy = cha.read_character(result[0])  # Carga definición del enemigo

                    battle = Battle(                        # Crea el combate
                        game_state.character, enemy, self.console, self.game_window
                    )
                    battle.resolve_battle(game_state, self.console)  # Resuelve la pelea
                    game_state.next_encounter = result[1]            # Siguiente encuentro post-batalla
                    del self.options[choice]                          # Elimina opción usada (p.ej. no repetir combate)
                    self.current_option = 0                           # Resetea selección
                    encounter_resolved = True

            elif choice == "menu":         # Abre menú del juego (guardar/salir)
                game_menu(game_state, self.console, self.game_window)


class Character:
    def __init__(self, name, strength, agility, intelligence, charisma, hp, defense):
        self.name = name
        self.strength = strength
        self.agility = agility
        self.intelligence = intelligence
        self.charisma = charisma
        self.hp = hp
        self.defense = defense

    def attack(self, enemy, battle_log, console, turn):
        if self.hp > 0:                                                     # Solo ataca si está vivo
            roll = random.randint(1, 6) + random.randint(1, 6) + self.strength  # 2d6 + fuerza
            if (roll > enemy.defense) & (roll < 12 + self.strength):       # Éxito normal
                # AVISO: aquí sería más idiomático usar 'and' en lugar de '&' (bit a bit) para booleanos
                console.print(
                    " "
                    + self.name
                    + "'s attacking roll: "
                    + str(roll)
                    + "[bold green] (success)",
                    justify="center",
                )
                damage = self.strength                                     # Daño base: fuerza
                enemy.hp = enemy.hp - damage                                # Resta HP al enemigo
                battle_log.append(                                          # Registra en el log
                    "Turn "
                    + str(turn)
                    + ": "
                    + self.name
                    + " attacked "
                    + enemy.name
                    + " for "
                    + str(damage)
                    + " damage.\n"
                )

            elif roll == 12 + self.strength:                                # Crítico (doble de daño)
                console.print(
                    " "
                    + self.name
                    + "'s attacking roll: "
                    + str(roll)
                    + "[bold yellow] (CRITICAL)",
                    justify="center",
                )
                damage = self.strength * 2                                  # Doble fuerza
                enemy.hp = enemy.hp - damage
                battle_log.append(
                    "Turn "
                    + str(turn)
                    + ": "
                    + self.name
                    + " attacked "
                    + enemy.name
                    + " for "
                    + str(damage)
                    + " damage.\n"
                )
            else:                                                           # Fallo
                console.print(
                    " "
                    + self.name
                    + "'s attacking roll: "
                    + str(roll)
                    + "[bold red] (fail)",
                    justify="center",
                )
                battle_log.append(
                    "Turn "
                    + str(turn)
                    + ": "
                    + self.name
                    + " attacked "
                    + enemy.name
                    + " but couldn't hit. \n"
                )
        else:
            console.print(" " + self.name + " is dead.", justify="center")  # Si está muerto, no ataca


class Battle(Menu):
    def __init__(self, character, enemy, console, game_window):
        self.character = character
        self.enemy = enemy
        self.battle_log = []
        Menu.__init__(
            self,
            "",                                                # Sin texto superior; se arma con print_details
            {"attack": "Attack your enemy", "flee": "Try to flee"},  # Opciones del combate
            console,
            game_window,
        )

    def make_sheet(self, character):
        sheet = Text()                                                   # Construye una ficha textual Rich
        sheet.append(Text("- Strength:             " + str(character.strength)))
        sheet.append(Text("\n- Agility:              " + str(character.agility)))
        sheet.append(Text("\n- Intelligence:         " + str(character.intelligence)))
        sheet.append(Text("\n- Charisma:             " + str(character.charisma)))
        sheet.append(Text("\n- HP:                   " + str(character.hp)))
        sheet.append(Text("\n- Defense:              " + str(character.defense)))

        return sheet                                                     # Devuelve el bloque de texto estilizado

    def on_press(self, key):
        if get_active_window_title() == self.game_window:                # Mismo filtro de ventana activa
            if key == keyboard.Key.up:                                   # Navegación arriba
                if self.current_option > 0:
                    self.current_option = self.current_option - 1
                os.system("clear")
                self.print_details()                                     # Dibuja fichas + log
                self.print_options()

            elif key == keyboard.Key.down:                               # Navegación abajo
                if self.current_option < len(self.options) - 1:
                    self.current_option = self.current_option + 1
                os.system("clear")
                self.print_details()
                self.print_options()

            elif key == keyboard.Key.enter:                              # Confirmar
                return False

            else:                                                        # Refrescar
                os.system("clear")
                self.print_details()
                self.print_options()

    def choice(self, numbered_choices=False):
        with keyboard.Listener(on_press=self.on_press) as listener:       # Escucha teclas durante el combate
            listener.join()

        return list(self.options.keys())[self.current_option]             # Devuelve la acción elegida

    def print_details(self):
        character_sheet = self.make_sheet(self.character)                 # Ficha del jugador
        enemy_sheet = self.make_sheet(self.enemy)                         # Ficha del enemigo

        columns = Columns(
            [
                Panel(character_sheet, title=self.character.name),       # Panel izquierdo: personaje
                Panel(enemy_sheet, title=self.enemy.name),               # Panel derecho: enemigo
            ],
            width=30,
        )

        self.console.print(                                              # Título "Battle"
            Panel(Text("Battle", justify="center"), width=62), justify="center"
        )
        self.console.print(columns, justify="center")                    # Fichas lado a lado
        self.console.print(
            Panel(
                "".join(self.battle_log[-6:]), title="Battle Log", width=62, height=8  # Últimos 6 eventos
            ),
            justify="center",
        )

    def roll_initiative(self):
        draw = True

        while draw is True:                                              # Repite si hay empate (no contemplado, ver abajo)
            character_initiative = random.randint(1, 6) + self.character.agility  # 1d6 + agilidad
            enemy_initiative = random.randint(1, 6) + self.enemy.agility

            if character_initiative > enemy_initiative:
                winner = self.character.name
                draw = False
                enemy_won_roll = False                                   # False -> jugador actúa primero
            elif character_initiative < enemy_initiative:
                winner = self.enemy.name
                draw = False
                enemy_won_roll = True                                    # True  -> enemigo actúa primero
            # Si hay empate, el while repite (no se define rama explícita)

        self.battle_log.append(winner + " takes the initiative... \n")  # Agrega al log
        return enemy_won_roll

    def resolve_battle(self, game_state, console):
        battle_finished = False
        enemy_won_roll = self.roll_initiative()    # Determina quién empieza
        turn = 0

        while battle_finished is False:
            os.system("clear")                      # Limpia
            turn = turn + 1                          # Incrementa turno
            self.print_details()                     # Muestra fichas y log
            self.print_options()                     # Muestra opciones (attack/flee)
            choice = self.choice()                   # Espera elección
            if choice == "attack":
                if enemy_won_roll is True:          # Si el enemigo ganó iniciativa
                    self.enemy.attack(self.character, self.battle_log, console, turn)  # Enemigo ataca primero
                    time.sleep(1.0)
                    self.character.attack(self.enemy, self.battle_log, console, turn)  # Luego jugador
                    time.sleep(1.5)
                else:                               # Jugador ganó iniciativa
                    self.character.attack(self.enemy, self.battle_log, console, turn)
                    time.sleep(1.0)
                    self.enemy.attack(self.character, self.battle_log, console, turn)
                    time.sleep(1.5)

            elif choice == "flee":                 # Huir: termina el combate
                battle_finished = True

            if self.enemy.hp <= 0:                  # Victoria del jugador
                os.system("clear")
                self.print_details()
                console.print(
                    "[bold yellow]\n You won the battle! Your enemy "
                    "lays dead before you...",
                    justify="center",
                )
                time.sleep(3)
                battle_finished = True
            elif self.character.hp <= 0:            # Derrota del jugador
                os.system("clear")
                self.print_details()
                console.print(
                    "[bold red]\n Even with all your might, this enemy "
                    "proved too powerful for you.\n Your adventure "
                    "ends here...",
                    justify="center",
                )
                time.sleep(3)
                battle_finished = True
                game_state.game_over = True         # Marca fin de juego


def get_active_window_title():
    root = subprocess.Popen(                                   # Ejecuta 'xprop -root _NET_ACTIVE_WINDOW'
        ["xprop", "-root", "_NET_ACTIVE_WINDOW"], stdout=subprocess.PIPE
    )
    stdout, stderr = root.communicate()                        # Captura salida del comando

    m = re.search(b"^_NET_ACTIVE_WINDOW.* ([\\w]+)$", stdout)  # Extrae ID de la ventana activa (hex)
    if m is not None:
        window_id = m.group(1)
        window = subprocess.Popen(                            # Ejecuta 'xprop -id <id> WM_NAME'
            ["xprop", "-id", window_id, "WM_NAME"], stdout=subprocess.PIPE
        )
        stdout, stderr = window.communicate()
    else:
        return None

    match = re.match(b"WM_NAME\\(\\w+\\) = (?P<name>.+)$", stdout)  # Extrae nombre (título) de la ventana
    if match is not None:
        return match.group("name").strip(b'"')               # Devuelve título sin comillas

    return None                                                # Si no pudo determinarlo


def game_menu(game_state, console, game_window):
    text = Text(
        "After a very tiring adventure, you finnaly find a place to rest",  # Texto del menú de juego
        justify="center",
    )
    options = {
        "save": "Save current adventure and exit",   # Guardar y salir
        "exit": "Exit without saving",               # Salir sin guardar
        "return": "Return to your adventure",        # Volver a la aventura
    }

    game_menu = Menu(text, options, console, game_window)  # Crea un menú reutilizando la clase Menu
    game_menu.print_menu()                                  # Dibuja el menú
    choice = game_menu.choice()                             # Espera elección

    if choice == "save":
        sav.save_game(game_state, console)                  # Llama a función de guardado
        sys.exit()                                          # Sale del juego
    elif choice == "exit":
        sys.exit()                                          # Sale sin guardar
    # Si choice == 'return' no hace nada y vuelve a la aventura


def initialize_game(game_state, console, game_window):

    text = (
        "[bold red]Welcome, adventurer! Are you ready for your next challenge?\n"
        "The world out there is full of monsters and treasures, and\n"
        "they are both waiting for you!\n"
        "Remember: Your choices always matter, so choose wisely."
    )

    options = {
        "create": "Create a character",   # Crear personaje
        "start": "Start an adventure",    # Empezar aventura (con personaje ya creado)
        "load": "Load a saved game",      # Cargar partida
        "exit": "Exit",                   # Salir
    }

    os.system("clear")

    starting_menu = Menu(text, options, console, game_window)  # Menú inicial
    starting_menu.print_menu()
    starting_menu.print_options()
    choice = starting_menu.choice()                             # Espera selección

    if choice == "create":
        os.system("clear")
        cha.create_character(save_folder="Characters/")        # Crea personaje y guarda en carpeta Characters
        initialize_game(game_state, console, game_window)       # Vuelve al menú inicial recursivamente
    elif choice == "start":
        character_list = [                                      # Lista de personajes disponibles (archivos .json)
            f.split(".")[0] for f in os.listdir("Characters") if f.endswith("json")
        ]
        if len(character_list) > 0:
            cha.choose_character(game_state, console, character_list, game_window)  # Elige personaje y lo asigna a game_state
            console.print("\n")
            adv.choose_adventure(game_state, console, game_window)                   # Elige aventura (define game_state.adventure)
        elif len(character_list) == 0:
            console.print(
                " Looks like you have not created any characters yet,"  # Mensaje si no hay personajes
                " try doing that first"
            )
            time.sleep(2)
            initialize_game(game_state, console, game_window)           # Regresa al menú inicial

    elif choice == "load":
        save_list = [f.split(".")[0] for f in os.listdir("Saves") if f.endswith("sav")]  # Partidas guardadas
        if len(save_list) > 0:
            game_state = sav.choose_save(game_state, console, save_list)  # Carga partida (probablemente muta game_state)
        elif len(save_list) == 0:
            console.print(" Looks like you don't have any saved files...")
            time.sleep(2)
            initialize_game(game_state, console, game_window)
    elif choice == "exit":
        console.print("Very well, see you next time, adventurer!")
        time.sleep(2)
        sys.exit()


def main_game():
    sys.stdout.write("\x1b[8;30;80t")         # Secuencia ANSI para redimensionar terminal (30 filas x 80 columnas). Puede no funcionar en todas las terminales.
    console = Console(width=80, height=30)   # Consola Rich con ancho/alto objetivo
    game_window = get_active_window_title()  # Guarda el título de la ventana activa al lanzar el juego (filtro de teclas)
    gs = GameState()                         # Instancia del estado del juego

    initialize_game(gs, console, game_window)  # Arranca flujo de menús iniciales
    exit_game = False
    while exit_game is False:                  # Bucle principal de la aventura
        gs.adventure[gs.next_encounter].resolve_encounter(gs)  # Resuelve el encuentro actual


if __name__ == "__main__":  # Punto de entrada si se ejecuta directamente (no como módulo)
    main_game()               # Llama a la función principal
