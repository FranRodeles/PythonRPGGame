from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich import box
from pynput import keyboard
import os
import sys
import time


console = Console()

class Menu():
    def __init__(self, text, options, console):
        self.text = text
        self.options = options
        self.current_option = 0
        self.choice_made = False
        self.console = console

 
    #Printea El titulo
    def print_menu(self):
        self.console.print(Panel(self.text, width=64), justify="center")

    #Printea Las opciones
    def print_option(self):
        current_option_key = self.current_option #Convierte el Diccionario en Lista
        options_text = ""
        for option in self.options: #Si coincide el indice de la opcion
           if option == current_option_key:
              options_text += f">[bold red on white] {self.options[option]} [/bold red on white]<\n"       #Muestra la opcion seleccionada
           else:
                options_text += self.options[option] + "\n"
        options_text = options_text.rstrip("\n") #Saca el ultimo salto de linea 

        self.console.print(
            Panel(Text.from_markup(options_text, justify="center"), box=box.SIMPLE, width=64),
            justify="center",)

    #Mostrar el menú completo
    def show(self):
        os.system("cls")
        self.print_menu()
        self.print_option()

    def controll_keyboard(self,tecla):
            indice = self.current_option()

            try:
                if tecla == keyboard.key.up:
                        indice_actual = (indice - 1) % len(self.opciones)
                        self.show()
                elif tecla == keyboard.key.down:
                        indice_actual = (indice - 1) % len(self.opciones)
                        self.show()
                elif tecla == keyboard.Key.enter:
                        self.choice_made = True
                        os.system("cls")
                        console.print(f"[bold green]Seleccionaste: {indice_actual} [/bold green]")


                     
                     



    

#Texto del Juego.El titulo-una breve descripcion y las opciones a elegir
text = "[bold red] Divine Light [/bold red]\n[yellow] This Game is Awesome [/yellow]"

options = { 
    0 : "Nuevo Juego",
    1 : "Cargar Partida",    
    2 : "Salir del Juego"
}

#Crear el Menu Principal
Menu_Principal = Menu(text, options, console)
Menu_Principal.show()
