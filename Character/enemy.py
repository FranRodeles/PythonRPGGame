# Character/enemy.py
from Character.character import Character

class Enemy(Character):
    def __init__(self,
                 name, type, atk, mage, accuracy, level,
                 experience, vida, defense, spd,
                 habilidades=None, ascii_path=None, xp_reward=0):
        # todo lo base vive en Character (incluye vida y defense)
        super().__init__(name, type, atk, mage, accuracy, level,
                         experience=experience, vida=vida, defense=defense)
        # campos específicos del enemigo
        self.spd = spd
        self.habilidades = habilidades or []
        self.ascii = ascii_path
        self.xp_reward = xp_reward

    @classmethod
    def from_json(cls, data: dict) -> "Enemy":
        s = data.get("stats", {})
        lvl = s.get("LEVEL", data.get("level", 1))
        return cls(
            name=data["nombre"],
            type=data.get("tipo", "neutral"),
            atk=s.get("ATK", 0),
            mage=0,
            accuracy=s.get("ACC", 100),
            level=lvl,
            experience=0,
            vida=s.get("HP", 1),        # ← HP del JSON mapeado a vida
            defense=s.get("DEF", 0),
            spd=s.get("AG", 0),
            habilidades=data.get("habilidades", []),
            ascii_path=data.get("ascii"),
            xp_reward=data.get("xp", 0),
        )

    def __repr__(self):
        return (f"<Enemy name={self.name} LVL={self.level} "
                f"VIDA={self.vida} ATK={self.atk} DEF={self.defense} "
                f"SPD={self.spd} XP={self.xp_reward}>")
