# Character/enemy.py
from Character.character import Character

class Enemy(Character):
    def __init__(
        self,
        name, type, atk, mage, accuracy, level, experience,
        hp, defense, spd,
        habilidades=None, ascii_path=None,
        xp_reward=0
    ):
        # lo genérico en la base
        super().__init__(name, type, atk, mage, accuracy, level, experience)
        # lo específico de combate
        self.hp = hp
        self.defense = defense
        self.spd = spd
        self.habilidades = habilidades or []
        self.ascii = ascii_path
        self.xp_reward = xp_reward

    @classmethod
    def from_json(cls, data: dict) -> "Enemy":
        stats = data.get("stats", {})
        level_val = stats.get("LEVEL", data.get("level",1))
        return cls(
            name=data["nombre"],
            type=data.get("tipo", "neutral"),
            atk=stats.get("ATK", 0),
            mage=0,                        # por ahora no viene en JSON
            accuracy=stats.get("ACC", 100),# default
            level=level_val,
            experience=0,
            hp=stats.get("HP", 1),
            defense=stats.get("DEF", 0),
            spd=stats.get("AG", 0),
            habilidades=data.get("habilidades", []),
            ascii_path=data.get("ascii"),
            xp_reward=data.get("xp", 0 )
        )

    def __repr__(self):
        return (
            f"<Enemy name={self.name} HP={self.hp} ATK={self.atk} "
            f"DEF={self.defense} SPD={self.spd} habilidades={self.habilidades}>"
        )
