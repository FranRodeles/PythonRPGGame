from pathlib import Path
from typing import Dict, Any, Optional #Para hacer las cosas mas legibles


#------------RUTAS-----------
json_dir = Path("../Jsons") #path general
path = json_dir / "zona1_tutorial.json"

#-----------LÓGICA-----------
class JsonReader():
    def __init__(self, json_dir: Path):
        #Ruta de los .json
        self.json_dir = Path = json_dir 

        #Json actual cargado
        self.current_file = Optional[str] = None

        #Nombre descriptivo de la zona de jso
        self.zona_name = Optional[str] = None

        #Indice de nodos de la zona actual(el nodo bruto sin tratar)
        self.nodes_index = dict[str, dict[str,Any]] = {} 

        #Guarda id del nodo actual
        self.current_node_id = Optional[str] = None

























