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

class main_character(Menu):

    def __init__(self, text, options ,console):
        super().__init__(text, options, console)
        self.current_option = 0   #Indice de opciones
        self.choice_made = False    #Si se realiza una accion
        self.options = options      #Lista con todos los personajes y sus caracteristicas
        self.console = console      #Console
        self.text = text            #Titulo del menu

    def print_menu(self):            #Muestra el titulo
        os.system("cls" if os.name == "nt" else "clear")
        self.console.rule(self.text)
    
    def print_option(self):   #Muestra las opciones

        panels = []
        for char in self.options:
            content = f"[bold]{char['name']}[/bold]\n\n{char['role']}\n\n{char['desc']}\n\n[bold red]ATK[/bold red]:{char['atk']}  [bold blue]MAGE[/bold blue]:{char['mag']}  [bold white]ACCURACY[/bold white]:{char['acu']}  [bold green]DEFENSE[/bold green]: {char['def']}"

            if char["id"] == self.current_option:
                panel = Panel(content, title="▶ Seleccionado ◀", border_style="bold yellow")
            
            else:
                panel = Panel(content, title = "No Seleccionado", border_style="dim")

            panels.append(panel)  

        console.print()
        console.print(*panels, justify="center")  #Desempaqueta todas las opciones de la lista panels y las muestra centradas
        console.print()
        console.rule("[green]   [Enter] Seleccionar   [Esc] Salir    [/green]")
    
    def show(self): #Muestra el titulo y las opciones
        return super().show()
    
    def controll_keyboard(self, tecla): #Manejo de teclas en el menu
        
        if tecla == keyboard.Key.up:
                self.current_option = (self.current_option - 1) % len(self.options)
                self.show()
        elif tecla == keyboard.Key.down:
                self.current_option = (self.current_option + 1) % len(self.options)
                self.show()
        elif tecla == keyboard.Key.enter:
                self.choice_made = True
                os.system("cls" if os.name == "nt" else "clear")
                console.print(f"[bold green]Seleccionaste: {self.options[self.current_option]["name"]} [/bold green]")
        elif tecla == keyboard.Key.esc:
                self.choice_made = True
                os.system("cls" if os.name == "nt" else "clear")
                console.print(f"[bold green]Seleccionaste: Salir [/bold green]")


#------LOGICA------    
text= "[bold magenta]⚔️ Selección de Personajes ⚔️[/bold magenta]"
character = [
    {"id" : 0,"name": "Lobo","role": "Paladin","desc":"El personaje mas basado 😎", "atk" : 7, "acu" : 7, "mag" : 0 ,"def":5},
    {"id" : 1,"name": "Gandalf","role": "Wizard","desc" : "pi piri piri pi PI PI PIPI", "atk" : 3, "acu" : 4, "mag" : 10,"def":2 },
    {"id" : 2,"name": "Robin Hood", "role": "Archer","desc":"SI SACO LA GUN", "atk" : 3, "acu" : 7, "mag" : 4,"def":4 }
]

if __name__ == "__main__":
    Menu_Personajes = main_character(text,character, console)
    Menu_Personajes.show()

    with keyboard.Listener(on_press=Menu_Personajes.controll_keyboard) as listener:
        listener.join()