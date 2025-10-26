# === A9: stop-list + min freq + diccionario hash + tiempos ===
from pathlib import Path
from collections import defaultdict, Counter
import re, time, math

# ---------- CONFIG ----------
FOLDER    = Path(r"C:\Users\Tanqu\OneDrive\Documentos\GitHub\School\Files")
STOPLIST  = FOLDER / "stoplist_en.txt"   # <- el TXT con tu lista, una palabra por línea
MATRICULA = "2955178"
MIN_FREQ  = 2                            # elimina tokens con frecuencia global < 2
# ----------------------------

TOKEN_RE = re.compile(r"[a-z0-9áéíóúüñ']+", re.I)

# 1) Archivos 000.html, 001.html, ...
files = sorted([p for p in FOLDER.iterdir() if p.suffix==".html" and p.stem.isdigit()],
               key=lambda p: int(p.stem))

# 2) Cargar stoplist
stop = set(w.strip().lower() for w in STOPLIST.read_text(encoding="utf-8").splitlines() if w.strip())

# 3) Tokenizar, filtrar y armar postings
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

# 6) Diccionario con hash table (linear probing) y huecos ;0;-1
def djb2(s:str)->int:
    h = 5381
    for ch in s: h = ((h<<5)+h) + ord(ch)
    return h & 0xFFFFFFFF

def next_prime(n:int)->int:
    if n < 2: return 2
    def is_p(x):
        if x % 2 == 0: return x == 2
        r = int(math.isqrt(x))
        for i in range(3, r+1, 2):
            if x % i == 0: return False
        return True
    while not is_p(n): n += 1
    return n

n_tokens = len(postings)
size = next_prime(max(2, math.ceil(n_tokens / 0.70)))  # ~70% de carga
table = [None] * size

for w in postings:
    i = djb2(w) % size
    while table[i] and table[i][0] != w:
        i = (i + 1) % size
    table[i] = (w, len(postings[w]))  # (token, df)

# 7) Escribir dictionary_hash y posting en el orden de la tabla
cursor, dict_lines, post_lines = 0, [], []
for slot in table:
    if slot is None:
        dict_lines.append(";0;-1")            # hueco
    else:
        w, df = slot
        dict_lines.append(f"{w};{df};{cursor}")
        post_lines += [f"{d};{c}" for d, c in postings[w]]
        cursor += df

(FOLDER/"dictionary_hash.txt").write_text("\n".join(dict_lines)+"\n", encoding="utf-8")
(FOLDER/"posting.txt").write_text("\n".join(post_lines)+"\n", encoding="utf-8")

# 8) Log A9 con tiempos por archivo y total (formato ejemplo)
total = time.perf_counter() - t0
(FOLDER/f"a9_{MATRICULA}.txt").write_text(
    "\n".join(log) + f"\n\nTiempo total de ejecucion del programa: {int(total)} segundos\n",
    encoding="utf-8"
)

print(f"OK → dictionary_hash.txt, posting.txt y a9_{MATRICULA}.txt  (Total {total:.2f}s)")
