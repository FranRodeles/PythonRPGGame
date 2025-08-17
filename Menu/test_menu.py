from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich import box
from pynput import keyboard
import os
import sys
import time

#Esto nos sirve para llamar a las distitas funciones que se encuentran en estas carpetas
def enlace_opciones():
    sys.path.append("Nuevo juego")
    sys.path.append("Cargar partida")
    sys.path.append("Salir")
    try:
        import characters as cha
        import saves as sav
    except ModuleNotFoundError:
        print("Couldn't find the necessary functions, closing the game...")
        time.sleep(2)
        sys.exit()

console = Console()
game_window = None

class Menu():
    def __init__(self, text, options, console, game_window):
        self.text = text
        self.options = options
        self.current_option = 0
        self.choice_made = False
        self.console = console
        self.game_window = game_window
 
    #Printea El titulo
    def print_menu(self):
        self.console.print(Panel(self.text, width=64), justify="center")

    #Printea Las opciones
    def print_option(self):
        current_option_key = list(self.options.keys())[self.current_option]
        options_text = ""
        for option in self.options:
            if option == current_option_key:
                options_text += f"> {self.options[option]} <\n"
            else:
                options_text += self.options[option] + "\n"
        options_text = options_text.rstrip("\n")

        self.console.print(
            Panel(Text(options_text, justify="center"), box=box.SIMPLE, width=64),
            justify="center",
        )

    #Mostrar el menú completo
    def show(self):
        os.system("cls")
        self.print_menu()
        self.print_option()

#Texto del Juego.El titulo-una breve descripcion y las opciones a elegir
text = "[bold red] Divine Light [/bold red]\n[yellow] This Game is Awesome [/yellow]"

options = { 
    0 : "Nuevo Juego",
    1 : "Cargar Partida",    
    2 : "Salir del Juego"
}

#Crear el Menu Principal
Menu_Principal = Menu(text, options, console, game_window)
Menu_Principal.show()
