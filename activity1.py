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

# Medidor de tiempo...
start = time.time()
#Prueba cada archivo de la carpeta
for f in files:
    file_path = os.path.join(folder, f)
    file_start = time.time()
    # Intentar abrir y leer el archivo
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as archivo:
            archivo.read()
        print(f"[{f[:-5]}] OK -> {time.time() - file_start:.4f} s")
    # Manejar errores de apertura/lectura
    except Exception as e:
        print(f"[{f[:-5]}] ERROR: {e}")

#Tiempo total de la prueba
end = time.time()

output_file = os.path.join(folder, "contenido_archivos.txt")
# Guardar el contenido de todos los archivos en uno solo y también manejar errores aparté de la prueba
with open(output_file, "w", encoding="utf-8") as out:
    out.write("Contenido de los archivos procesados:\n\n")
    for f in files:
        file_path = os.path.join(folder, f)
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as archivo:
                contenido = archivo.read()
                # Eliminar etiquetas HTML
               # contenido_sin_tags = re.sub(r'<[^>]+>', '', contenido)
                #contenido = contenido_sin_tags
                # Separar en palabras y ordenar
               # palabras = contenido.split()
               # palabras_ordenadas = sorted(palabras, key=str.lower)
               # contenido_ordenado = ' '.join(palabras_ordenadas)
            out.write(f"===== {f} =====\n")
            out.write(contenido + "\n\n")
        except Exception as e:
            out.write(f"===== {f} =====\nERROR: {e}\n\n")
#Imprimir tiempo total del contenido
print(f"\nSe guardó el contenido en: {output_file}")
#tiempo total de ordenamiento y guardado de las palabras sin etiquetas
print(f"Tiempo total de procesamiento y guardado: {time.time() - end:.4f} s")
print(f"Tiempo total de la prueba: {end - start:.4f} s")
# === BLOQUE EXTRA (añadir al final, sin modificar nada arriba) ===
# Crear consolidado (minúsculas) y medir tiempos de crear/ordenar/total
t0_total = time.time()
t0_create = time.time()

consolidated_words = []
for f in files:
    file_path = os.path.join(folder, f)
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as archivo:
            contenido = archivo.read()
            # quitar etiquetas HTML de forma simple
            contenido = re.sub(r"<[^>]+>", " ", contenido)
            # extraer solo palabras [a-z] y pasarlas a minúsculas
            consolidated_words.extend(re.findall(r"[a-z]+", contenido.lower()))
    except Exception as e:
        # no detenemos el proceso si un archivo falla
        pass

t1_create = time.time()

# ordenar alfabéticamente
t0_sort = time.time()
consolidated_words.sort()
t1_sort = time.time()

# guardar consolidado (una palabra por línea)
consolidated_path = os.path.join(folder, "consolidado_palabras.txt")
with open(consolidated_path, "w", encoding="utf-8") as out:
    out.write("\n".join(consolidated_words))

# tiempos en consola (sin crear archivo de log)
print(f"\nConsolidado guardado en: {consolidated_path}")
print(f"Tiempo en crear el consolidado: {t1_create - t0_create:.2f} s")
print(f"Tiempo en ordenar alfabéticamente: {t1_sort - t0_sort:.2f} s")
print(f"Tiempo total del bloque consolidado: {time.time() - t0_total:.2f} s")
#César Fernando Serna Velázquez