from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from pynput import keyboard
import os

class Menu():
    def __init__(self, text, options, console, game_window):
        self.text = text
        self.options = options
        self.current_option = 0
        self.choice_made = False
        self.console = console
        self.game_window = game_window
        
    def print_menu(self,text,options):
        text = ([red] "Divine Light" [/red]"\n"
                [yellow]"This Game is Awesome" [/yellow])           #Titulo con una breve descripcion

        options = { 01 : "Nuevo Juego",
                    02 : "Cargar Partida",
                    03 : "Salir del Juego"}
        
        self.text = text
        self.options = options

        os.system("clear")

