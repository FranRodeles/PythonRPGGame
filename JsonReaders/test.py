from pathlib import Path
from reader import JsonReader  # tu archivo se llama reader.py

r = JsonReader(Path("./Jsons"))   # carpeta donde están los .json
r.load_zone("zona1_tutorial.json") # nombre del archivo json

print("Archivo actual:", r.current_file)
print("Nombre de la zona:", r.zone_name)
print("IDs de nodos:", list(r.nodes_index.keys()))

print(r.current_node_id)
