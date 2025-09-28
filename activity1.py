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

# === medidor de tiempo total
start_total = time.time()

# =dir de salida para tokenizados y acumulador de frecuencias
tok_dir = os.path.join(folder, "tokens")
os.makedirs(tok_dir, exist_ok=True)
freq = {}

# Prueba cada archivo de la carpeta + tokenización y conteo
for f in files:
    file_path = os.path.join(folder, f)
    file_start = time.time()
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as archivo:
            contenido = archivo.read()

        # tokenizar (minúsculas, solo letras) y guardar .tok.txt
        contenido = re.sub(r"<[^>]+>", " ", contenido)                 # quitar etiquetas html simple
        toks = re.findall(r"[a-z]+", contenido.lower())                # palabras minúsculas
        with open(os.path.join(tok_dir, f[:-5] + ".tok.txt"), "w", encoding="utf-8") as ft:
            ft.write("\n".join(toks))

        # acumular frecuencias
        for w in toks:
            freq[w] = freq.get(w, 0) + 1

        print(f"[{f[:-5]}] OK -> {time.time() - file_start:.4f} s")
    except Exception as e:
        print(f"[{f[:-5]}] ERROR: {e}")

# consolidado A–Z
t_alpha0 = time.time()
items_alpha = sorted(freq.items(), key=lambda kv: kv[0])               # orden alfabético
alpha_path = os.path.join(folder, "tokens_alpha.txt")
with open(alpha_path, "w", encoding="utf-8") as fa:
    for w, c in items_alpha:
        fa.write(f"{w} {c}\n")
t_alpha1 = time.time()

# consolidado por frecuencia (desc; empate A–Z)
t_freq0 = time.time()
items_byfreq = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
byfreq_path = os.path.join(folder, "tokens_byfreq.txt")
with open(byfreq_path, "w", encoding="utf-8") as ff:
    for w, c in items_byfreq:
        ff.write(f"{w} {c}\n")
t_freq1 = time.time()

# tiempos y rutas de salida
print("\n=== Salidas ===")
print(f"Tokenizados por archivo: {tok_dir}")
print(f"Consolidado A–Z:        {alpha_path}")
print(f"Consolidado por freq.:  {byfreq_path}")

print("\n=== Tiempos ===")
print(f"A–Z:         {t_alpha1 - t_alpha0:.2f} s")
print(f"Por frec.:   {t_freq1 - t_freq0:.2f} s")
print(f"Total todo:  {time.time() - start_total:.2f} s")

# César Fernando Serna Velázquez
