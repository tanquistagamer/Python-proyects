from pathlib import Path
from collections import defaultdict, Counter
import re, time, math

#  CONFIG 
FOLDER    = Path(r"C:\Users\Tanqu\OneDrive\Documentos\GitHub\School\Files")
MATRICULA = "2955178"
# 

TOKEN_RE = re.compile(r"[a-záéíóúüñ]+", re.I)
files = sorted([p for p in FOLDER.iterdir() if p.suffix==".html" and p.stem.isdigit()],
               key=lambda p: int(p.stem))
tokdir = FOLDER/"tokens"; tokdir.mkdir(exist_ok=True)

t0, log, postings = time.perf_counter(), [], defaultdict(list)
for p in files:
    t1 = time.perf_counter()
    s  = re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8", errors="replace"))
    toks = [t.lower() for t in TOKEN_RE.findall(s)]
    (tokdir/f"{p.stem}.tok.txt").write_text("\n".join(toks), encoding="utf-8")
    for w,c in Counter(toks).items(): postings[w].append((p.name,c))
    log.append(f"{p}\t{time.perf_counter()-t1:.2f}")

# ordenar docs por número para cada token 
for w in postings: postings[w].sort(key=lambda dc:int(dc[0][:-5]))

# HASH TABLE (linear probing con DJB2) 
def djb2(s:str)->int:
    h = 5381
    for ch in s: h = ((h<<5)+h) + ord(ch)
    return h & 0xFFFFFFFF

def next_prime(n:int)->int:
    if n<2: return 2
    def is_prime(x:int)->bool:
        if x%2==0: return x==2
        r=int(math.isqrt(x))
        for i in range(3,r+1,2):
            if x%i==0: return False
        return True
    while not is_prime(n): n+=1
    return n

tokens = list(postings.keys())
n = len(tokens)
size = next_prime(int(math.ceil(n/0.70)))   # ~70% load
table = [None]*size
collisions = 0

for w in tokens:
    i = djb2(w) % size
    while table[i] is not None and table[i][0] != w:
        collisions += 1
        i = (i+1) % size
    table[i] = (w, len(postings[w]))  # (token, df)

# Escribir dictionary + posting en orden de la tabla 
cursor, dict_lines, post_lines = 0, [], []
for slot in table:
    if slot is None:
        dict_lines.append(f";0;-1")
    else:
        w, df = slot
        dict_lines.append(f"{w};{df};{cursor}")
        post_lines += [f"{d};{c}" for d,c in postings[w]]
        cursor += df

(FOLDER/"dictionary_hash.txt").write_text("\n".join(dict_lines)+"\n", encoding="utf-8")
(FOLDER/"posting.txt").write_text("\n".join(post_lines)+"\n", encoding="utf-8")

total = time.perf_counter() - t0
log_text = (
    "\n".join(log)
    + "\n\n"
    + f"Tiempo total de ejecucion del programa: {int(total)} segundos\n"
    + f"(equivale a {total:.2f} s)\n"
)

(FOLDER / f"a8_{MATRICULA}.txt").write_text(log_text, encoding="utf-8")

print(f"\nTiempo total de ejecucion del programa: {total:.2f} s")
