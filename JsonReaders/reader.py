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

        # 5) Apuntar al primer nodo
        if self.nodes_index:  
            self.current_node_id = list(self.nodes_index.keys())[0]
        else:
            self.current_node_id = None

    def get_current_node(self) -> dict:
        if self.current_node_id is None:
            raise RuntimeError("No hay nodo actual. Cargá una zona y seteá el nodo.")
        if self.current_node_id not in self.nodes_index:
            raise KeyError(f"Nodo '{self.current_node_id}' no existe en '{self.current_file}'.")
        return self.nodes_index[self.current_node_id]


    #Leemos resultado para interpretarlo, para ver si seguimos en el archivo
    def jump_to_by_index(self, index: int):
        """Salta al nodo destino según la opción elegida."""
        nodo = self.get_current_node()
        opciones = nodo.get("opciones", [])
        if not opciones:
            return "FIN"

        if index < 0 or index >= len(opciones):
            raise IndexError(f"Índice fuera de rango: {index}")

        resultado = opciones[index].get("resultado", "").strip()

        # caso fin
        if resultado.upper() == "FIN":
            self.current_node_id = None
            return "FIN"

        # caso archivo#nodo
        if "#" in resultado:
            archivo, nodo_id = resultado.split("#", 1)
            archivo = archivo.strip()
            nodo_id = nodo_id.strip()

            if archivo:  # cambiar de archivo
                self.load_zone(archivo)
                self.set_current_node(nodo_id)
            else:  # mismo archivo
                self.set_current_node(nodo_id)

            return "OK"

        raise ValueError(f"Formato de resultado inválido: {resultado}")

    def set_current_node(self, node_id: str):
        # 1) validar que haya zona cargada
        if not self.nodes_index:
            raise RuntimeError("No hay zona cargada. Llamá primero a load_zone().")

        # 2) normalizar y validar el id
        if node_id is None:
            raise ValueError("node_id no puede ser None.")
        node_id = node_id.strip()
        if not node_id:
            raise ValueError("node_id vacío.")
        if node_id not in self.nodes_index:
            raise KeyError(f"El nodo '{node_id}' no existe en '{self.current_file}'.")

        # 3) asignar
        self.current_node_id = node_id
