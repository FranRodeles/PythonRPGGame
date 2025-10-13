# Character/player.py
from Character.character import Character

class Player(Character):
    """Jugador genérico: se inicializa con un dict del menú (sin defaults ocultos)."""
    def __init__(self, name: str, role: str, atk: int, mage: int, accuracy: int,
                 defense: int, vida: int, level: int, experience: int = 0):
        super().__init__(
            name=name, type=role,
            atk=atk, mage=mage, accuracy=accuracy,
            level=level, experience=experience,
            vida=vida, defense=defense
        )
        self.puntos_atributos = 0

    def __repr__(self):
        return (f"<Player {self.type} name={self.name} LVL={self.level} "
                f"VIDA={self.vida} ATK={self.atk} MAG={self.mage} "
                f"ACC={self.accuracy} DEF={self.defense} XP={self.experience}>")
    
    def subir_level(self):
        self.level += 1
        self.experience -= 100
        self.puntos_atributos += 3
        
        



def create_player_from_menu_dict(d: dict) -> Player:
    """
    Espera EXACTAMENTE las claves usadas en el menú:
      {"id","name","role","desc","atk","acu","mag","def","vida","level"}
    si falta algo, se rompe.
    """
    required = ["name", "role", "atk", "mag", "acu", "def", "vida", "level"]
    missing = [k for k in required if k not in d]
    if missing:
        raise KeyError(f"Faltan claves en el dict de personaje: {missing}")

    return Player(
        name=d["name"],
        role=d["role"],
        atk=d["atk"],
        mage=d["mag"],
        accuracy=d["acu"],
        defense=d["def"],
        vida=d["vida"],
        level=d["level"],
        experience=0,  # experiencia siempre arranca en 0 
    )

