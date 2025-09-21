# Menu/menu_character.py
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
import os

from Menu.menu import Menu

class main_character(Menu):
    def __init__(self, text, options, console: Console):
        """
        options: list[dict] con claves:
            id, name, role, desc, atk, acu, mag, def
        """
        super().__init__(text, options, console)
        self.current_option = 0  # índice dentro de la lista de personajes

    def _print_title(self):
        os.system("cls" if os.name == "nt" else "clear")
        self.console.rule(self.text)

    def _print_options(self):
        panels = []
        for i, char in enumerate(self.options):
            content = (
                f"[bold]{char['name']}[/bold]\n\n"
                f"{char['role']}\n\n"
                f"{char['desc']}\n\n"
                f"[bold red]ATK[/bold red]: {char['atk']}  "
                f"[bold blue]MAGE[/bold blue]: {char['mag']}  "
                f"[bold white]ACCURACY[/bold white]: {char['acu']}  "
                f"[bold green]DEFENSE[/bold green]: {char['def']}"
            )
            if i == self.current_option:
                panel = Panel(content, title="▶ Seleccionado ◀", border_style="bold yellow")
            else:
                panel = Panel(content, title="No Seleccionado", border_style="dim")
            panels.append(panel)

        self.console.print()
        self.console.print(*panels, justify="center")
        self.console.print()
        self.console.rule("[green]   [Enter] Seleccionar   [Esc] Volver    [/green]")

    def show(self):
        self._print_title()
        self._print_options()

    # sobrescribimos para usar longitud de la lista
    def move_up(self):
        self.current_option = (self.current_option - 1) % len(self.options)
        self.show()

    def move_down(self):
        self.current_option = (self.current_option + 1) % len(self.options)
        self.show()

    def get_selected_character(self) -> dict:
        return self.options[self.current_option]


# ------ datos del submenú (pueden venir de un JSON si querés) ------
text = "[bold magenta]⚔️ Selección de Personajes ⚔️[/bold magenta]"
# ... (resto igual)

character = [
    {"id": 0, "name": "Lobo",       "role": "Paladin", "desc": "El personaje más basado 😎",
     "atk": 40, "acu": 7, "mag": 0,  "def": 5, "vida": 100, "level": 1},

    {"id": 1, "name": "Gandalf",    "role": "Wizard",  "desc": "pi piri piri pi PI PI PIPI",
     "atk": 3, "acu": 4, "mag": 10, "def": 2, "vida": 60,  "level": 1},

    {"id": 2, "name": "Robin Hood", "role": "Archer",  "desc": "SI SACO LA GUN",
     "atk": 3, "acu": 7, "mag": 4,  "def": 4, "vida": 80,  "level": 1},
]


# Este módulo ya no maneja teclado por sí mismo: lo hace launcher.py
