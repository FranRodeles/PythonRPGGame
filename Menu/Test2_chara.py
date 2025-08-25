from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from pynput import keyboard
import os

console = Console()

class CharacterMenu:
    def __init__(self, characters):
        self.characters = characters
        self.current_index = 0
        self.choice_made = False

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def render(self):
        self.clear()
        console.rule("[bold magenta]⚔️ Selección de Personajes ⚔️[/bold magenta]")

        panels = []
        for i, char in enumerate(self.characters):
            content = (
                f"[bold]{char['name']}[/bold]\n\n"
                f"{char['role']}\n\n"
                f"{char['desc']}\n\n"
                f"[cyan]ATK[/cyan]: {char['atk']}  "
                f"[magenta]MAGIA[/magenta]: {char['magia']}  "
                f"[green]PRECISIÓN[/green]: {char['precision']}"
            )
            if i == self.current_index:
                panel = Panel(content, title="▶ Seleccionado ◀", border_style="bold yellow")
            else:
                panel = Panel(content, title = "no seleccionado", border_style="dim")
            panels.append(panel)

        console.print()
        console.print(*panels, justify="center")
        console.print()
        console.rule("[green]←/→ Mover   [Enter] Seleccionar   [Esc] Salir[/green]")

    def on_press(self, key):
        if key == keyboard.Key.right:
            self.current_index = (self.current_index + 1) % len(self.characters)
            self.render()
        elif key == keyboard.Key.left:
            self.current_index = (self.current_index - 1) % len(self.characters)
            self.render()
        elif key == keyboard.Key.enter:
            self.choice_made = True
            self.clear()
            console.print(f"[bold green]Has elegido a: {self.characters[self.current_index]['name']}![/bold green]")
            return False
        elif key == keyboard.Key.esc:
            self.choice_made = True
            self.clear()
            console.print("[yellow]Selección cancelada.[/yellow]")
            return False

    def run(self):
        self.render()
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

# Datos de ejemplo
characters = [
    {"name": "Aldric", "role": "Guerrero", "desc": "Un maestro de la espada.", "atk": 8, "magia": 2, "precision": 6},
    {"name": "Lyra", "role": "Hechicera", "desc": "Controla el fuego y el hielo.", "atk": 5, "magia": 10, "precision": 4},
    {"name": "Kael", "role": "Arquero", "desc": "Letal a larga distancia.", "atk": 7, "magia": 1, "precision": 9}
]

menu = CharacterMenu(characters)
menu.run()
