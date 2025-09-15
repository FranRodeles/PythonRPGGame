from rich.console import Console, Group
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.table import Table
from rich.layout import Layout
from rich.align import Align
from rich.text import Text
import time


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


def make_hp_bar(char: Character, color: str):
    progress = Progress(
        TextColumn("❤️"),
        BarColumn(bar_width=40, complete_style=color, finished_style="grey37"),
        TextColumn("{task.completed}/{task.total}"),
        expand=False,
    )
    progress.add_task("vida", total=100, completed=char.vida)
    return progress


def render_battle_ui(player: Character, enemy: Character, log_lines=None):
    layout = Layout()
    layout.split_column(
        Layout(name="enemy", ratio=2),
        Layout(name="player", ratio=2),
        Layout(name="log", ratio=1),
    )

    # --- Enemigo ---
    enemy_panel = Panel(
        Group(
            Align.center(Text(f"👹 {enemy.name}", style="bold red")),
            Align.center(make_hp_bar(enemy, "red")),
            Align.center(Text(f"Lvl {enemy.level} • {enemy.type}", style="italic dim"))
        ),
        title="[bold red]ENEMIGO[/]",
        border_style="red",
    )
    layout["enemy"].update(enemy_panel)

    # --- Jugador ---
    stats = Table.grid(padding=1)
    stats.add_column(justify="center", style="cyan")
    stats.add_column(justify="center", style="yellow")
    stats.add_row("⚔️ ATK", str(player.atk))
    stats.add_row("✨ MAG", str(player.mage))
    stats.add_row("🎯 ACC", str(player.accuracy))
    stats.add_row("🛡️ DEF", str(player.defense))

    player_panel = Panel(
        Group(
            Align.center(Text(f"🧝 {player.name}", style="bold green")),
            Align.center(make_hp_bar(player, "green")),
            Align.center(stats),
        ),
        title=f"[bold green]{player.type.upper()}[/]",
        border_style="green",
    )
    layout["player"].update(player_panel)

    # --- Log de batalla ---
    log_render = "\n".join(log_lines) if log_lines else "Esperando acciones..."
    log_panel = Panel(
        Align.left(Text(log_render, style="bold white")),
        title="[yellow]⚔️ Registro de Batalla[/]",
        border_style="yellow",
    )
    layout["log"].update(log_panel)

    # Render final
    console.clear()
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

    # Simulación simple
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
