import os
import time
from rich.console import Console, Group
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.table import Table
from rich.layout import Layout
from rich.align import Align
from rich.text import Text


class Character:
    def __init__(self, name, type, atk, mage, accuracy, level,
                 experience=0, vida=0, defense=0):
        self.name = name
        self.type = type
        self.atk = atk
        self.mage = mage
        self.accuracy = accuracy
        self.level = level
        self.experience = experience
        self.puntos_atributos = 0
        self.vida = vida
        self.defense = defense

    def subir_level(self):
        self.experience = 0
        self.level += 1
        self.puntos_atributos += 3


console = Console()


def clear_screen():
    """Limpia la terminal (Windows = cls, Linux/Mac = clear)."""
    os.system("cls" if os.name == "nt" else "clear")


def make_stats_panel(char: Character, color: str, title: str):
    """Panel compacto con barra de vida y stats"""
    progress = Progress(
        TextColumn("❤️"),
        BarColumn(bar_width=15, complete_style=color, finished_style="grey37"),
        TextColumn("{task.completed}/{task.total}"),
        expand=False,
    )
    progress.add_task("vida", total=100, completed=char.vida)

    stats = Table.grid(padding=(0, 1))  # sin espacios extras
    stats.add_column(justify="right", style="cyan", no_wrap=True)
    stats.add_column(justify="left", style="white", no_wrap=True)
    stats.add_row("⚔️", str(char.atk))
    stats.add_row("✨", str(char.mage))
    stats.add_row("🎯", str(char.accuracy))
    stats.add_row("🛡️", str(char.defense))
    stats.add_row("⭐", str(char.level))

    return Panel(
        Group(progress, stats),
        title=f"[bold {color}]{title}[/]",
        border_style=color,
        padding=(0, 1),  # ajustado
    )


def render_battle_ui(player: Character, enemy: Character, log_lines=None):
    layout = Layout()

    # Dividir la terminal
    layout.split_column(
        Layout(name="top", ratio=5),
        Layout(name="log", ratio=2)
    )
    layout["top"].split_row(
        Layout(name="sidebar", ratio=1),
        Layout(name="ascii_area", ratio=3)
    )
    layout["sidebar"].split_column(
        Layout(name="player", ratio=1),
        Layout(name="enemy", ratio=1)
    )

    # Panel jugador y enemigo
    player_panel = make_stats_panel(player, "green", player.name)
    enemy_panel = make_stats_panel(enemy, "red", enemy.name)

    layout["player"].update(player_panel)
    layout["enemy"].update(enemy_panel)

    # Panel ASCII enemigo (más compacto)
    ascii_enemy = r"""
      ,      ,
     /(.-""-.)\
 |\  \/      \/  /|
 | \ / =.  .= \ / |
 \( \   o\/o   / )/
  \_, '-/  \-' ,_/
    /   \__/   \
    \ \__/\__/ /
  ___\ \|--|/ /___
 /`    \    /    `\
    """
    layout["ascii_area"].update(
        Panel(
            Align.center(Text(ascii_enemy, style="bold")),
            title="[red]👹 Enemigo[/]",
            border_style="magenta",
            padding=(0, 1)  # sin espacios extras
        )
    )

    # Log de combate compacto
    log_render = "\n".join(log_lines) if log_lines else "Esperando acciones..."
    layout["log"].update(
        Panel(
            Align.left(Text(log_render, style="bold white")),
            title="[yellow]⚔️ Registro de Combate[/]",
            border_style="yellow",
            padding=(0, 1)
        )
    )

    # Refrescar pantalla con os.system
    clear_screen()
    console.print(layout)


# ------------------------
# Ejemplo de uso
# ------------------------
if __name__ == "__main__":
    player = Character("Arthas", "Paladín", atk=25, mage=10, accuracy=85, level=3, vida=90, defense=15)
    enemy = Character("Orco", "Guerrero", atk=18, mage=0, accuracy=70, level=2, vida=65, defense=8)

    logs = []
    render_battle_ui(player, enemy, logs)
    time.sleep(2)

    logs.append("🧝 Arthas ataca con su espada y causa 15 de daño ⚔️")
    enemy.vida -= 15
    render_battle_ui(player, enemy, logs)
    time.sleep(2)

    logs.append("👹 Orco responde con un golpe brutal y causa 10 de daño 💥")
    player.vida -= 10
    render_battle_ui(player, enemy, logs)
    time.sleep(2)

    logs.append("🧝 Arthas lanza un hechizo sagrado ✨ y derrota al Orco ☠️")
    enemy.vida = 0
    render_battle_ui(player, enemy, logs)

