from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from pynput import keyboard
import os


opciones = ["Nuevo juego", "Cargar juego", "Salir"]
indice_actual = 0
console = Console()


def dibujar_menu():
    os.system('cls')  # o 'cls' en Windows
    menu_renderizado = []

    for i, opcion in enumerate(opciones):
        prefijo = "➤" if i == indice_actual else "  "
        linea = f"[red]{prefijo} {opcion}[/red]" if i == indice_actual else f"  {opcion}"
        menu_renderizado.append(linea)

    panel = Panel(Align.center("\n".join(menu_renderizado), vertical="middle"),
                  title="Menú principal", width=40, height=10)
    console.print(panel)


def main():

    dibujar_menu()

if __name__ == "__main__":
    main()

