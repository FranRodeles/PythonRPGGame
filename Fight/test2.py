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

        # opcionales / base de combate
        self.vida = vida
        self.defense = defense

    def subir_level(self):
        self.experience = 0
        self.level += 1
        self.puntos_atributos += 3


console = Console()

def render_battle_ui(player: Character, enemy: Character):
    layout = Layout()
    layout.split_column(
        Layout(name="enemy", ratio=1),
        Layout(name="player", ratio=1),
    )

    # --------------------
    # Barra de vida Enemigo
    # --------------------
    enemy_progress = Progress(
        TextColumn("❤️"),
        BarColumn(bar_width=40, complete_style="red", finished_style="grey37"),
        TextColumn("{task.completed}/{task.total}"),
        expand=False,
    )
    enemy_progress.add_task("vida_enemigo", total=100, completed=enemy.vida)

    enemy_title = Text(f"👹 {enemy.name}", style="bold red")
    enemy_panel = Panel(
        Group(
            Align.center(enemy_title),
            Align.center(enemy_progress)
        ),
        title=f"[bold red]{enemy.type}[/]",
        border_style="bright_red"
    )
    layout["enemy"].update(enemy_panel)

    # --------------------
    # Barra de vida Jugador
    # --------------------
    player_progress = Progress(
        TextColumn("💚"),
        BarColumn(bar_width=40, complete_style="green", finished_style="grey37"),
        TextColumn("{task.completed}/{task.total}"),
        expand=False,
    )
    player_progress.add_task("vida_jugador", total=100, completed=player.vida)

    # Stats del jugador en tabla fachera
    stats = Table.grid(expand=True)
    stats.add_column(justify="right", ratio=1)
    stats.add_column(justify="left", ratio=2, style="cyan")
    stats.add_row("⚔️ ATK", str(player.atk))
    stats.add_row("✨ MAG", str(player.mage))
    stats.add_row("🎯 ACC", str(player.accuracy))
    stats.add_row("🛡️ DEF", str(player.defense))
    stats.add_row("⭐ LVL", str(player.level))

    player_title = Text(f"🧝 {player.name}", style="bold green")

    player_panel = Panel(
        Group(
            Align.center(player_title),
            Align.center(player_progress),
            Align.center(stats)
        ),
        title=f"[bold green]{player.type}[/]",
        border_style="green"
    )

    layout["player"].update(player_panel)

    # --------------------
    # Render final
    # --------------------
    console.clear()
    console.print(layout)


# ------------------------
# Ejemplo de uso
# ------------------------
if __name__ == "__main__":
    player = Character("Arthas", "Paladín", atk=25, mage=10, accuracy=85, level=3, vida=90, defense=15)
    enemy = Character("Orco", "Guerrero", atk=18, mage=0, accuracy=70, level=2, vida=65, defense=8)

    render_battle_ui(player, enemy)
