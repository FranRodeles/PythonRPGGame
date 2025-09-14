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

    #Buscamos el nodo actual dentro del diccionario (para imprimir ejemplo el texto del nodo)
    def get_current_node(self) -> dict:
        return self.nodes_index[self.current_node_id]

    #Cambiamos el nodo segun resultado del JSON
    def set_current_node(self, node_id: str):
        self.current_node_id = node_id

    #Leemos resultado para interpretarlo, para ver si seguimos en el archivo o solo movemos nodo
    def jump_to_by_index(self, index: int):
        nodo = self.get_current_node()
        opciones = nodo["opciones"]                  # asumimos siempre hay opciones
        resultado = opciones[index]["resultado"].strip()  # asumimos index válido

        if resultado.upper() == "FIN":
            self.current_node_id = None
            return "FIN"

        # formato: "#id"  o  "archivo.json#id"
        archivo, nodo_id = ("", "")  # defaults
        if "#" in resultado:
            archivo, nodo_id = resultado.split("#", 1) #parti en #, solo 1 vez
            archivo = archivo.strip()
            nodo_id = nodo_id.strip()

        if archivo == "" or archivo == self.current_file:
            # mismo archivo (o el mismo explícito): solo mover nodo
            self.set_current_node(nodo_id)
            return "OK"

        # archivo distinto: cargar y mover
        self.load_zone(archivo)
        self.set_current_node(nodo_id)
        return "OK"

    # reader.py (dentro de tu clase)
    def jump_to_result(self, result_str: str) -> str:
        s = result_str.strip()
        if s.upper() == "FIN":
            self.current_node_id = None
            return "FIN"

        archivo, nodo_id = "", ""
        if "#" in s:
            archivo, nodo_id = s.split("#", 1)
            archivo = archivo.strip()
            nodo_id = nodo_id.strip()

        if archivo == "" or archivo == self.current_file:
            self.set_current_node(nodo_id)
            return "OK"

        self.load_zone(archivo)
        self.set_current_node(nodo_id)
        return "OK"


