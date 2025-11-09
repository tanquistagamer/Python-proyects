import os
import time
import re
from collections import Counter   # A8: para contar por archivo
import math                       # A8: para primo/tamaño tabla

# Configuraciones
folder     = r"C:\Users\Tanqu\OneDrive\Documentos\GitHub\School\Files"
MATRICULA  = "2955178"


# Obtener lista de archivos que sean solo números con .html
files = []
for f in os.listdir(folder):
    if f.endswith(".html") and f[:-5].isdigit():
        files.append(f)

# Ordenarlos por número
files.sort(key=lambda x: int(x[:-5]))

# inicializaciones para diccionario/tiempos
start_total = time.time()                              # tiempo total
tok_dir = os.path.join(folder, "tokens")               # dir tokenizados (por archivo)
os.makedirs(tok_dir, exist_ok=True)

freq = {}             # (A6/A7) repeticiones totales (no se usa en A8, se deja por compatibilidad)
doc_count = {}        # # de archivos que contienen el token (df)
time_lines = []       # para archivo de tiempos
postings = {}         # A8: token a lista de (doc, freq_en_doc)

# Procesamiento por archivo 
for f in files:
    file_path = os.path.join(folder, f)
    file_start = time.time()
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as archivo:
            contenido = archivo.read()

        # tokenizar y guardar por archivo
        contenido = re.sub(r"<[^>]+>", " ", contenido)      # quitar html básico
        toks = re.findall(r"[a-z]+", contenido.lower())     # sólo palabras minúsculas

        # Guardar tokenizado por archivo (igual que tenías)
        with open(os.path.join(tok_dir, f[:-5] + ".tok.txt"), "w", encoding="utf-8") as ft:
            ft.write("\n".join(toks))

        # (A6/A7) acumulado de repeticiones totales: no es necesario para A8,
        # pero lo dejo por compatibilidad.
        for w in toks:
            freq[w] = freq.get(w, 0) + 1

        # A8: df por token (en cuántos docs aparece)
        for w in set(toks):
            doc_count[w] = doc_count.get(w, 0) + 1

        # A8: construir POSTINGS con frecuencia POR DOCUMENTO
        counts = Counter(toks)                      # w a freq en ESTE doc
        for w, c in counts.items():
            postings.setdefault(w, []).append((f, c))  # guardo el nombre del archivo

        dt = time.time() - file_start
        print(f"[{f[:-5]}] OK -> {dt:.2f} s")
        time_lines.append(f"{file_path}\t{dt:.2f}")
    except Exception as e:
        print(f"[{f[:-5]}] ERROR: {e}")

# Escritura del diccionario viejo
# dict_path = os.path.join(folder, "tokens_dictionary.tsv")
# with open(dict_path, "w", encoding="utf-8") as fd:
#     fd.write("token\trepeticiones\t#docs\n")
#     for w, c in freq.items():
#         fd.write(f"{w}\t{c}\t{doc_count.get(w,0)}\n")
# ordenar docs por número dentro de cada token (más claro/repetible)
for w in postings:
    postings[w].sort(key=lambda dc: int(dc[0][:-5]))

# Hash estable DJB2 + primo cercano para 70% de carga
def djb2(s: str) -> int:
    h = 5381
    for ch in s:
        h = ((h << 5) + h) + ord(ch)
    return h & 0xFFFFFFFF

def next_prime(n: int) -> int:
    if n < 2: return 2
    def is_p(x: int) -> bool:
        if x % 2 == 0: return x == 2
        r = int(math.isqrt(x))
        for i in range(3, r + 1, 2):
            if x % i == 0: return False
        return True
    while not is_p(n): n += 1
    return n

tokens = list(doc_count.keys())
n = len(tokens)
size = next_prime(max(2, math.ceil(n / 0.70)))  # ~70% load
table = [None] * size
collisions = 0

# Insertamos (token, df) con linear probing
for w in tokens:
    df = doc_count[w]
    i = djb2(w) % size
    while table[i] is not None and table[i][0] != w:
        collisions += 1
        i = (i + 1) % size
    table[i] = (w, df)

# Escribir dictionary_hash y posting en el orden de la tabla
dict_hash_path = os.path.join(folder, "dictionary_hash.txt")   # formato: token;docs;start
posting_path    = os.path.join(folder, "posting.txt")          # formato: doc;freq

cursor = 0
dict_lines = []
post_lines = []

for slot in table:
    if slot is None:
        # registro no utilizado (hueco)
        dict_lines.append(f";0;-1")
    else:
        w, df = slot
        dict_lines.append(f"{w};{df};{cursor}")
        # anexar las (doc;freq) de ese token en el mismo orden
        for doc, c in postings.get(w, []):
            post_lines.append(f"{doc};{c}")
        cursor += df

with open(dict_hash_path, "w", encoding="utf-8") as fd:
    fd.write("\n".join(dict_lines) + ("\n" if dict_lines else ""))

with open(posting_path, "w", encoding="utf-8") as fp:
    fp.write("\n".join(post_lines) + ("\n" if post_lines else ""))

# archivo de tiempos/log 
log_path = os.path.join(folder, f"a8_{MATRICULA}.txt")
with open(log_path, "w", encoding="utf-8") as flog:
    flog.write("\n".join(time_lines) + "\n\n")
    flog.write(f"Tokens únicos: {n}\n")
    flog.write(f"Tamaño de la hash table: {size}\n")
    flog.write(f"Factor de carga ~ {n/size:.3f}\n")
    flog.write(f"Colisiones: {collisions}\n")
    flog.write(f"Tiempo total de ejecucion del programa: {int(time.time() - start_total)} segundos\n")

# Reporte en consola
print("\n=== Salidas A8 ===")
print(f"Tokenizados por archivo: {tok_dir}")
print(f"Diccionario HASH:        {dict_hash_path}")   # token;#docs;start (con huecos ;0;-1)
print(f"Posting:                 {posting_path}")     # doc;freq en el orden del diccionario
print(f"Log A8:                  {log_path}")
# print(f"Diccionario 3 columnas:  {dict_path}")     
# print(f"Archivo de tiempos:      {times_path}") 
