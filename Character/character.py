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
