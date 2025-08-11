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
 
        #Printea El titulo
    def print_menu(self):
        self.console.print(Panel(self.text,width=64),justify="center")
        #Printea Las opciones
    def print_option(self):



        #Texto del Juego.El titulo-una breve descripcion y las opciones a elegir
    def text_menu(self):
        text = ([red] "Divine Light" [/red]"\n"
                [yellow]"This Game is Awesome" [/yellow])           #Titulo con una breve descripcion

        options = { 01 : "Nuevo Juego",
                    02 : "Cargar Partida",    
                    03 : "Salir del Juego"}   #Opciones

        os.system("clear")

        #Crear el Menu
        starting_menu = Menu(text,options,console,game_window)

        #Mostrar el menu
        os.system("clear")
        starting_menu.print_menu()
        starting_menu.print_option()
