from menu import Menu

class main_character(Menu):
    def __init__(self, text, character,console,):
        super().__init__(text, options, console)
        self.current_character = 0
        self.choice_made = False
        self.character = character






    def print_menu(self):
        os.system("cls" if os.name == "nt" else "clear")
        self.console.rule(self.text)
    
    def print_option(self):
        for char in self.character:
            content = f"[bold]{char['name']}[/bold]\n\n{char['role']}\n\n{char['desc']}\n\n[bold red]ATK[/bold red]: {char['atk']}  [bold blue]MAGE[/bold blue]: {char['mag']}  [bold green]ACCURACY[/bold green]: {char['acu']}"

        




#------LOGICA------    
text= "[bold magenta]⚔️ Selección de Personajes ⚔️[/bold magenta]"
character = [
    {"id" : 0,"name": "Lobo","role": "Paladin","desc":"El personaje mas basado 😎", "atk" : 9, "acu" : 9, "mag" : 0 },
    {"id" : 1,"name": "Gandalf","role": "Wizard","desc" : "pi piri piri pi PI PI PIPI", "atk" : 3, "acu" : 4, "mag" : 11 },
    {"id" : 2,"name": "Robin Hood", "role": "Archer","desc":"SI SACO LA GUN", "atk" : 5, "acu" : 9, "mag" : 4 }
]
options = 