from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from pynput import keyboard
import os

console = Console()
opciones = ["Nuevo juego", "Cargar juego", "Salir"]
indice_actual = 0
seleccion_hecha = False

def dibujar_menu():
    os.system('cls')  # o 'cls' en Windows
    menu_renderizado = []

    for i, opcion in enumerate(opciones):
        prefijo = "➤" if i == indice_actual else "  "
        linea = f"[bold yellow]{prefijo} {opcion}[/bold yellow]" if i == indice_actual else f"  {opcion}"
        menu_renderizado.append(linea)

    panel = Panel(Align.center("\n".join(menu_renderizado), vertical="middle"),
                  title="Menú principal", width=40, height=10)
    console.print(panel)

def manejar_input(tecla):
    global indice_actual, seleccion_hecha

    if seleccion_hecha:
        return False  # Detiene el listener

    try:
        if tecla == keyboard.Key.up:
            indice_actual = (indice_actual - 1) % len(opciones)
            dibujar_menu()
        elif tecla == keyboard.Key.down:
            indice_actual = (indice_actual + 1) % len(opciones)
            dibujar_menu()
        elif tecla == keyboard.Key.enter:
            seleccion_hecha = True
            os.system('clear')
            console.print(f"[bold green]Seleccionaste: {opciones[indice_actual]}[/bold green]")
            return False  # Detiene el listener
    except:
        pass

def main():
    dibujar_menu()
    with keyboard.Listener(on_press=manejar_input) as listener:
        listener.join()

if __name__ == "__main__":
    main()
