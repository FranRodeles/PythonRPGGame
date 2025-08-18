from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich import box
from pynput import keyboard
import os

console = Console()

class Menu():
    def __init__(self, text, options, console):
        self.text = text
        self.options = options
        self.current_option = 0
        self.choice_made = False
        self.console = console

    # Printea el título
    def print_menu(self):
        self.console.print(Panel(self.text, width=64), justify="center")

    # Printea las opciones
    def print_option(self):
        options_text = ""
        for option in self.options:
            if option == self.current_option:
                options_text += f">[bold red on white] {self.options[option]} [/bold red on white]<\n"
            else:
                options_text += self.options[option] + "\n"

        options_text = options_text.rstrip("\n")

        self.console.print(
            Panel(Text.from_markup(options_text, justify="center"), box=box.SIMPLE, width=64),
            justify="center",
        )

    # Mostrar el menú completo
    def show(self):
        os.system("cls" if os.name == "nt" else "clear")
        self.print_menu()
        self.print_option()

    # Control del teclado
    def controll_keyboard(self, tecla):
        if self.choice_made:
            return False  # cortar listener si ya eligió

        try:
            if tecla == keyboard.Key.up:
                self.current_option = (self.current_option - 1) % len(self.options)
                self.show()
            elif tecla == keyboard.Key.down:
                self.current_option = (self.current_option + 1) % len(self.options)
                self.show()
            elif tecla == keyboard.Key.enter:
                self.choice_made = True
                os.system("cls" if os.name == "nt" else "clear")
                console.print(f"[bold green]Seleccionaste: {self.options[self.current_option]}[/bold green]")
                return False  # detiene el listener
        except:
            pass
