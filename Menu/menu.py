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
        self.text = text                        #Titulo
        self.options = options                  #Opciones
        self.current_option = 0                 #Indice de las opciones
        self.choice_made = False                #Si se selecciona una opcion, por ende arranca en falso
        self.console = console                  #Nos permite manipular la terminal      

 
    #Printea El titulo y lo posiciona a nuestro gusto
    def print_menu(self):
        self.console.print(Panel(self.text, width=64), justify="center")

    #Printea Las opciones y las pocisiona a nuestro gusto
    def print_option(self):
        current_option_key = self.current_option #Convierte el Diccionario en Lista
        options_text = ""
        for option in self.options: #Si coincide el indice de la opcion
           if option == current_option_key:
              options_text += f">[bold red on white] {self.options[option]} [/bold red on white]<\n"       #Muestra la opcion seleccionada
           else:
                options_text += self.options[option] + "\n"     #Printea las otras opciones no seleccionadas 
        options_text = options_text.rstrip("\n") #Saca el ultimo salto de linea 

        self.console.print(Panel(Text.from_markup(options_text, justify="center"), box=box.SIMPLE, width=64),justify="center",)
        #Modifica la ubicacion de las opciones en la terminal

    #Mostrar el menú completo
    def show(self):
        os.system("cls")
        self.print_menu()
        self.print_option()

    def controll_keyboard(self,tecla):
            indice = self.current_option

            if tecla == keyboard.Key.up:
                    self.current_option = (self.current_option - 1) % len(self.options)
                    self.show()
            elif tecla == keyboard.Key.down:
                    self.current_option = (self.current_option + 1) % len(self.options)
                    self.show()
            elif tecla == keyboard.Key.enter:
                    self.choice_made = True
                    os.system("cls")
                    console.print(f"[bold green]Seleccionaste: {self.options[self.current_option]} [/bold green]")

#Texto del Juego.El titulo-una breve descripcion y las opciones a elegir
text = "[bold red] Divine Light [/bold red]\n[yellow] This Game is Awesome [/yellow]"

options = { 
    0 : "Nuevo Juego",
    1 : "Cargar Partida",    
    2 : "Salir del Juego"}







# ------------------Logica----------------------
#Crear el Menu Principal
if __name__ == "__main__":
    Menu_Principal = Menu(text, options, console)
    Menu_Principal.show()

    with keyboard.Listener(on_press=Menu_Principal.controll_keyboard) as listener:
        listener.join()

