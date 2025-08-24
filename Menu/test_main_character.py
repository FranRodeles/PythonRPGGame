from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich import box
from pynput import keyboard
import os
import sys
import time
from menu import Menu

console = Console()

class main_character(Menu):

    def __init__(self, text, options ,console):
        super().__init__(text, options, console)
        self.current_option = 0
        self.choice_made = False
        self.options = options
        self.console = console
        self.text = text

    def print_menu(self):
        os.system("cls" if os.name == "nt" else "clear")
        self.console.rule(self.text)
    
    def print_option(self):

        panels = []
        for char in self.options:
            content = f"[bold]{char['name']}[/bold]\n\n{char['role']}\n\n{char['desc']}\n\n[bold red]ATK[/bold red]: {char['atk']}  [bold blue]MAGE[/bold blue]: {char['mag']}  [bold green]ACCURACY[/bold green]: {char['acu']}"

            if char["id"] == self.current_option:
                panel = Panel(content, title="▶ Seleccionado ◀", border_style="bold yellow")
            
            else:
                panel = Panel(content, title = "No Seleccionado", border_style="dim")

            panels.append(panel)  

        console.print()
        console.print(*panels, justify="center")
        console.print()
        console.rule("[green]   [Enter] Seleccionar   [Esc] Salir    [/green]")
    
    def show(self):
        return super().show()
    
    def controll_keyboard(self, tecla):
        
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
    {"id" : 0,"name": "Lobo","role": "Paladin","desc":"El personaje mas basado 😎", "atk" : 9, "acu" : 9, "mag" : 0 },
    {"id" : 1,"name": "Gandalf","role": "Wizard","desc" : "pi piri piri pi PI PI PIPI", "atk" : 3, "acu" : 4, "mag" : 11 },
    {"id" : 2,"name": "Robin Hood", "role": "Archer","desc":"SI SACO LA GUN", "atk" : 5, "acu" : 9, "mag" : 4 }
]

if __name__ == "__main__":
    Menu_Personajes = main_character(text,character, console)
    Menu_Personajes.show()

    with keyboard.Listener(on_press=Menu_Personajes.controll_keyboard) as listener:
        listener.join()