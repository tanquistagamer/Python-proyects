import os
import time
import re

# Carpeta con los archivos
folder = r"C:\Users\Tanqu\OneDrive\Documentos\GitHub\School\Files"

# Obtener lista de archivos que sean solo números con .html
files = []
for f in os.listdir(folder):
    if f.endswith(".html") and f[:-5].isdigit():
        files.append(f)

# Ordenarlos por número
files.sort(key=lambda x: int(x[:-5]))

# inicializaciones para diccionario/tiempos 
start_total = time.time()                              # MOD: tiempo total
tok_dir = os.path.join(folder, "tokens")               # MOD: dir tokenizados (por archivo)
os.makedirs(tok_dir, exist_ok=True)                    # MOD
freq = {}                                              # MOD: repeticiones totales
doc_count = {}                                         # MOD: # de archivos que contienen el token
time_lines = []                                        # MOD: para archivo de tiempos
# 

# Prueba cada archivo de la carpeta + tokenizar y contar
for f in files:
    file_path = os.path.join(folder, f)
    file_start = time.time()
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as archivo:
            contenido = archivo.read()                 # lectura original

        # tokenizar y guardar por archivo 
        contenido = re.sub(r"<[^>]+>", " ", contenido)             # quitar html básico
        toks = re.findall(r"[a-z]+", contenido.lower())            # sólo palabras minúsculas
        with open(os.path.join(tok_dir, f[:-5] + ".tok.txt"), "w", encoding="utf-8") as ft:
            ft.write("\n".join(toks))                               # tokenizado por archivo

        # acumular repeticiones y #docs (set por archivo)
        for w in toks:
            freq[w] = freq.get(w, 0) + 1
        for w in set(toks):
            doc_count[w] = doc_count.get(w, 0) + 1
        # 

        dt = time.time() - file_start
        print(f"[{f[:-5]}] OK -> {dt:.2f} s")
        time_lines.append(f"{file_path}\t{dt:.2f}")     # MOD: para archivo de tiempos
    except Exception as e:
        print(f"[{f[:-5]}] ERROR: {e}")

# escribir diccionario 3 columnas (no ordenado) 
dict_path = os.path.join(folder, "tokens_dictionary.tsv")  # tabs como separador
with open(dict_path, "w", encoding="utf-8") as fd:
    # encabezado opcional (déjalo si tu profe lo quiere; si no, comenta esta línea)
    fd.write("token\trepeticiones\t#docs\n")
    for w, c in freq.items():                             # SIN ordenar para máxima velocidad
        fd.write(f"{w}\t{c}\t{doc_count.get(w,0)}\n")
# 

#archivo de tiempos 
times_path = os.path.join(folder, "a6_tiempos.txt")
with open(times_path, "w", encoding="utf-8") as flog:
    flog.write("\n".join(time_lines) + "\n\n")
    flog.write(f"Tiempo total de ejecucion del programa: {int(time.time() - start_total)} segundos\n")
# 

# Reporte en consola
print("\n=== Salidas ===")
print(f"Tokenizados por archivo: {tok_dir}")
print(f"Diccionario 3 columnas:  {dict_path}")
print(f"Archivo de tiempos:      {times_path}")
