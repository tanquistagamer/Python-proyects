#A10: columnas fijas + tf-idf + log ===
from pathlib import Path
from collections import defaultdict, Counter
import re, time, math

FOLDER    = Path(r"C:\Users\Tanqu\OneDrive\Documentos\GitHub\School\Files")
STOPLIST  = FOLDER / "stoplist_en.txt"  # el TXT con tu lista (una palabra por línea)
MATRICULA = "2955178"
MIN_FREQ  = 2                            # elimina tokens con frecuencia global < 2
DECIMALS  = 4                            # decimales para el peso
# Anchos fijos (divisores de 80B)
W_TOKEN, W_DF, W_START = 13, 3, 4        # 13+3+4=20 → 4 registros ≈ 80B
W_DOC,   W_WEIGHT      = 3, 7            # 3+7=10   → 8 registros ≈ 80B


TOKEN_RE = re.compile(r"[a-z0-9áéíóúüñ']+", re.I)

# 1) Archivos 000.html, 001.html, ...
files = sorted([p for p in FOLDER.iterdir() if p.suffix==".html" and p.stem.isdigit()],
               key=lambda p: int(p.stem))
N_DOCS = len(files)

# 2) Cargar stoplist
stop = set(w.strip().lower() for w in STOPLIST.read_text(encoding="utf-8").splitlines() if w.strip())

# 3) Tokenizar, filtrar (stoplist + len>1), y armar postings
tokdir = FOLDER / "tokens"; tokdir.mkdir(exist_ok=True)
t0 = time.perf_counter(); log = []; postings = defaultdict(list)

for p in files:
    t1 = time.perf_counter()
    txt  = re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8", errors="replace"))
    toks = [t for t in TOKEN_RE.findall(txt.lower()) if len(t) > 1 and t not in stop]
    (tokdir/f"{p.stem}.tok.txt").write_text("\n".join(toks), encoding="utf-8")
    for w, c in Counter(toks).items(): postings[w].append((p.name, c))
    log.append(f"{p}\t{time.perf_counter()-t1:.2f}")

# 4) Filtro por frecuencia global mínima
if MIN_FREQ > 1:
    totals = {w: sum(c for _, c in pairs) for w, pairs in postings.items()}
    postings = {w: pairs for w, pairs in postings.items() if totals[w] >= MIN_FREQ}

# 5) Ordena docs por número para cada token
for w in postings: postings[w].sort(key=lambda dc: int(dc[0][:-5]))

# 6) Hash table (linear probing) para el diccionario con huecos ;0;-1
def djb2(s:str)->int:
    h=5381
    for ch in s: h=((h<<5)+h)+ord(ch)
    return h & 0xFFFFFFFF

def next_prime(n:int)->int:
    if n<2: return 2
    def is_p(x):
        if x%2==0: return x==2
        r=int(math.isqrt(x))
        for i in range(3,r+1,2):
            if x%i==0: return False
        return True
    while not is_p(n): n+=1
    return n

n_tokens = len(postings)
size = next_prime(max(2, math.ceil(n_tokens/0.70)))   # 70% de carga
table = [None]*size
for w in postings:
    i = djb2(w) % size
    while table[i] and table[i][0] != w:
        i = (i+1) % size
    table[i] = (w, len(postings[w]))  # (token, df)

# 7) Escribir dictionary_hash (20B por registro) y posting (10B por registro con PESO tf-idf)
dict_path = FOLDER/"dictionary_hash.txt"
post_path = FOLDER/"posting.txt"

cursor, dict_lines, post_lines = 0, [], []
for slot in table:
    if slot is None:
        # hueco: token vacío; df=0; start=-1 → 20B exactos
        dict_lines.append("".ljust(W_TOKEN) + "0".rjust(W_DF) + "-1".rjust(W_START))
    else:
        w, df = slot
        # línea de diccionario: TOKEN(13, cortado) + DF(3) + START(4)
        dict_lines.append(w[:W_TOKEN].ljust(W_TOKEN) + str(df).rjust(W_DF) + str(cursor).rjust(W_START))

        # posting: DOCID(3) + PESO(7) por cada doc del token
        idf = math.log10(N_DOCS/df) if df else 0.0
        for doc, freq in postings[w]:
            tf = 1.0 + math.log10(freq) if freq > 0 else 0.0
            weight = tf * idf
            docid = int(Path(doc).stem)
            post_lines.append(str(docid).rjust(W_DOC) + f"{weight:{W_WEIGHT}.{DECIMALS}f}")
        cursor += df

# Guardar
dict_path.write_text("\n".join(dict_lines)+"\n", encoding="utf-8")
post_path.write_text("\n".join(post_lines)+"\n", encoding="utf-8")

# 8) Log A10 con tiempos por archivo y total
total = time.perf_counter() - t0
(FOLDER/f"a10_{MATRICULA}.txt").write_text(
    "\n".join(log)
    + f"\n\nReg. diccionario: {W_TOKEN+W_DF+W_START} bytes (≈ {80//(W_TOKEN+W_DF+W_START)} regs por 80B)\n"
      f"Reg. posting:     {W_DOC+W_WEIGHT} bytes (≈ {80//(W_DOC+W_WEIGHT)} regs por 80B)\n"
    + f"Tiempo total de ejecucion del programa: {int(total)} segundos\n",
    encoding="utf-8"
)

print(f"OK → {dict_path.name} (20B/registro), {post_path.name} (10B/registro) y a10_{MATRICULA}.txt  (Total {total:.2f}s)")
