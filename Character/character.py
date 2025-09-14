
class Character():
    def __init__(self,name,type,atk,mage,accuracy,level,experience):
        self.name = name
        self.type = type
        self.atk = atk
        self.mage = mage
        self.accuracy = accuracy
        self.level = level
        self.experience = experience
        self.puntos_atributos = 0

    def subir_level(self):
        self.experience = 0
        self.level = self.level + 1
        self.puntos_atributos = self.puntos_atributos + 3
        


        