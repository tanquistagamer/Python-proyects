# Big Data – Tokenization & Indexing (A8–A10) — Evidence Package

> **Repo folder:** `School/`  
> **Dataset folder:** `School/Files/`  
> **Student:** 2955178 (César Fernando Serna Velázquez)

Este README reúne lo necesario para entregar la evidencia final de **tokenización**, **diccionario (hash)** y **posting** con **tf–idf**, además de los artefactos **Scrum** y **métricas** (gráficas y logs).

---

## 1) Qué hace el sistema

1. **Tokeniza** `.html` numerados (`000.html`, `001.html`, …): elimina etiquetas, pasa a minúsculas y **filtra** stop-words + tokens de longitud 1.  
2. **Indexa**: construye
   - **Diccionario (hash table)** con *linear probing* y huecos (`;0;-1`), **20 bytes por registro**.
   - **Posting** con `docId` y **peso tf–idf**, **10 bytes por registro**.
3. **Mide tiempos** y deja **logs**.
4. **CLI** con dos subcomandos:
   - `tokenize input-dir output-dir --stoplist ...`
   - `index input-dir output-dir --stoplist ...`
5. **Benchmarks** para graficar tiempos vs. número de documentos.

---

## 2) Estructura / salidas

School/
├─ search_index.py # CLI: tokenize / index
├─ bench.py # Benchmarks + gráficas
└─ Files/
├─ stoplist_en.txt # Stop-list (una palabra por línea)
├─ *.html # 000.html, 001.html, ...
├─ tokens/ # .tok.txt por documento (salida de tokenización)
├─ dictionary_hash.txt # 20B: TOKEN(13)+#DOC(3)+START(4)
├─ posting.txt # 10B: DOCID(3)+PESO(7) (tf–idf)
├─ a_tokenize_2955178.txt # tiempos tokenización + tokens totales
├─ a10_2955178.txt # tiempos indexación + tokens únicos
├─ grafica_tokenize.png
├─ grafica_tokenize_index.png
└─ times.csv


---

## 3) Cómo ejecutar (CLI)

> Requisitos: Python 3.12+. Para `bench.py` instala `matplotlib`:
>
> ```powershell
> python -m pip install matplotlib
> ```

### 3.1 Tokenización
```powershell
python search_index.py tokenize ^
  C:\Users\Tanqu\OneDrive\Documentos\GitHub\School\Files ^
  C:\Users\Tanqu\OneDrive\Documentos\GitHub\School\Files ^
  --stoplist C:\Users\Tanqu\OneDrive\Documentos\GitHub\School\Files\stoplist_en.txt

python search_index.py index ^
  C:\Users\Tanqu\OneDrive\Documentos\GitHub\School\Files ^
  C:\Users\Tanqu\OneDrive\Documentos\GitHub\School\Files ^
  --stoplist C:\Users\Tanqu\OneDrive\Documentos\GitHub\School\Files\stoplist_en.txt ^
  --min_freq 2
