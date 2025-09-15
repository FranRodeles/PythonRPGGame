from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.align import Align

console = Console()

def barra_vida(vida, vida_max, ancho=20, color="green"):
    llenado = int((vida / vida_max) * ancho)
    vacio = ancho - llenado
    return f"[{color}]" + "█" * llenado + f"[/]" + " " * vacio + f" {vida}/{vida_max}"

def crear_interfaz():
    # --- Panel Héroe ---
    heroe = Table.grid(padding=0, expand=True)
    heroe.add_row("❤️ Vida:", barra_vida(80, 100, color="green"))
    heroe.add_row("⚔️ Ataque: 25    🛡️ Defensa: 15")
    heroe.add_row("✨ Magia: 10     🎯 Precisión: 85")
    heroe.add_row("⭐ Nivel: [bold yellow]3[/]")
    panel_heroe = Panel(
        heroe,
        title="👑 Arthas (Paladín)",
        border_style="green",
        box=box.DOUBLE,
        padding=(0,1)
    )

    # --- Panel Enemigo ---
    enemigo = Table.grid(padding=1, expand=True)
    ascii_enemigo = """ 
      (｡♥‿♥｡)
       /︶＼
      | -  - |
       \\  =  /
        `---´
    """
    enemigo.add_row(Align.center(ascii_enemigo))
    enemigo.add_row("❤️ Vida:", barra_vida(0, 100, color="red"))
    enemigo.add_row("⚔️ Ataque: 18    🛡️ Defensa: 8")
    enemigo.add_row("✨ Magia: 0      🎯 Precisión: 70")
    enemigo.add_row("⭐ Nivel: [bold yellow]2[/]")
    panel_enemigo = Panel(
        enemigo,
        title="👹 Orco (Guerrero)",
        border_style="red",
        box=box.DOUBLE,
        padding=(0,1)
    )

    # --- Registro de combate ---
    combate = Table.grid(padding=0, expand=True)
    combate.add_row("👑 Arthas ataca con su espada y causa 15 de daño ⚔️")
    combate.add_row("👹 Orco golpea y causa 10 de daño 💥")
    combate.add_row("👑 Arthas lanza un hechizo sagrado ✨ → Orco derrotado ☠️")
    panel_combate = Panel(
        combate,
        title="⚔️ Registro de Combate",
        border_style="yellow",
        box=box.DOUBLE,
        padding=(0,1)
    )

    # --- Layout Final ---
    layout = Table.grid(expand=True)
    layout.add_row(panel_heroe, panel_enemigo, panel_combate)

    console.print(layout)

crear_interfaz()

