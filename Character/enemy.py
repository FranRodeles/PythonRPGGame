from pathlib import Path
from pynput import keyboard
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.align import Align
import time

from JsonReaders import JsonReader
from character import Character

class Enemy(Character):
    def __init__(self, name, vida, type, atk, mage, accuracy, defense, level):
        super().__init__(name, vida, type, atk, mage, accuracy, defense, level)
        

def Cargar_datos():
    name = ""
    vida = ""
    type = ""
    atk = ""
    mage = ""
    accuracy = ""
    defense = ""
    level = ""

    enemigo = Enemy(name,vida,type,atk,mage,accuracy,defense,level)
    return enemigo

Enemigo_1= Cargar_datos()    