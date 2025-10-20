# Menu/menu.py
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
from pathlib import Path
import os

class Menu:
    def __init__(self, text, options, console: Console):
        """
        options: dict
        """
        self.text = text
        self.options = options
        self.current_option = 0
        self.console = console
        #Cargamos arte ASCII, try por si acaso
        try:
            art_path = Path(__file__).parent / "menu_art.txt"
            self._ascii = art_path.read_text(encoding="utf-8")
        except Exception:
            self._ascii = None

    def _print_ascii(self):
        # Muestra el arte si existe
        if not self._ascii:
            return
        self.console.print(
            Panel.fit(
                Text(self._ascii),
                border_style="bright_black"
            ),
            justify="center",
        )

    def _print_title(self):
        self.console.print(Panel(self.text, width=64), justify="center")

    def _print_options(self):
        lines = []
        for idx in sorted(self.options.keys()):
            label = self.options[idx]
            if idx == self.current_option:
                lines.append(f">[bold red on white] {label} [/bold red on white]<")
            else:
                lines.append(label)
        options_text = "\n".join(lines)
        self.console.print(
            Panel(
                Text.from_markup(options_text),
                box=box.SIMPLE,
                width=64
            ),
            justify="center",
        )

    def show(self):
        os.system("cls" if os.name == "nt" else "clear")
        self._print_title()
        self._print_options()
        self._print_ascii()

    # helpers para que el launcher controle el teclado
    def move_up(self):
        self.current_option = (self.current_option - 1) % len(self.options)
        self.show()

    def move_down(self):
        self.current_option = (self.current_option + 1) % len(self.options)
        self.show()

    def current_choice(self) -> int:
        return self.current_option
