from pathlib import Path
from typing import Dict, Any, Optional #Para hacer las cosas mas legibles
import os
import json

#-----------LÓGICA-----------
class JsonReader():
    def __init__(self, json_dir: Path):
        #Ruta de los .json
        self.json_dir: Path = json_dir 

        #Json actual cargado
        self.current_file: Optional[str] = None

        #Nombre descriptivo de la zona de json
        self.zone_name: Optional[str] = None

        #Indice de nodos de la zona actual(el nodo bruto sin tratar)
        self.nodes_index: dict[str, dict[str,Any]] = {} 

        #Guarda id del nodo actual
        self.current_node_id: Optional[str] = None

    def load_zone(self, filename: str):
        #Cargar ruta del archivo
        path = self.json_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"No existe el archivo: {path}")
        
        #Leer JSON
        with open(path, "r", encoding = "utf-8") as f:
            data = json.load(f)

        self.current_file = filename
        self.zone_name = data.get("zona", None)

        #Indice de nodos
        self.nodes_index= {}
        for nodo in data.get("nodos",[]):
            node_id = nodo["id"]
            if node_id in self.nodes_index:
                raise ValueError(f"ID de nodo duplicado: {node_id}")
            self.nodes_index[node_id] = nodo

        # 5) al terminar, apuntar al primer nodo
        if self.nodes_index:  
            self.current_node_id = list(self.nodes_index.keys())[0]
        else:
            self.current_node_id = None

    def set_current_node(self,node_id):
        if not self.nodes_index:
            raise RuntimeError("Llamar a load_zone()")

        self.current_node_id = node_id























