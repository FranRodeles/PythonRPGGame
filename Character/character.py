
class Character():
    def __init__(self,name,vida,type,atk,mage,accuracy,defense,level):
        self.name = name
        self.vida = vida
        self.type = type
        self.atk = atk
        self.mage = mage
        self.accuracy = accuracy
        self.defense = defense
        self.level = level










    def subir_level(self):
        self.experience = 0
        self.level = self.level + 1
        self.puntos_atributos = self.puntos_atributos + 3

        


        