from pathlib import Path
from collections import defaultdict, Counter
import re, time

FOLDER     = Path(r"C:\Users\Tanqu\OneDrive\Documentos\GitHub\School\Files")
MATRICULA  = "2955178"  # matrícula

files = sorted([p for p in FOLDER.iterdir() if p.suffix==".html" and p.stem.isdigit()],
               key=lambda p: int(p.stem))
tokdir = (FOLDER/"tokens"); tokdir.mkdir(exist_ok=True)
TOKEN_RE = re.compile(r"[a-záéíóúüñ]+", re.I)

t0, log, postings = time.perf_counter(), [], defaultdict(list)

for p in files:
    t1 = time.perf_counter()
    s  = re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8", errors="replace"))
    toks = [t.lower() for t in TOKEN_RE.findall(s)]
    (tokdir/f"{p.stem}.tok.txt").write_text("\n".join(toks), encoding="utf-8")
    for w, c in Counter(toks).items(): postings[w].append((p.name, c))
    log.append(f"{p}\t{time.perf_counter()-t1:.2f}")

# ordenar: tokens alfabético y docs por número
tokens = sorted(postings)
for w in tokens: postings[w].sort(key=lambda dc: int(dc[0][:-5]))

# escribir dictionary y posting
cursor, dict_lines, post_lines = 0, [], []
for w in tokens:
    pairs = postings[w]; dict_lines.append(f"{w};{len(pairs)};{cursor}")
    post_lines += [f"{d};{c}" for d,c in pairs]; cursor += len(pairs)

(FOLDER/"dictionary.txt").write_text("\n".join(dict_lines)+"\n", encoding="utf-8")
(FOLDER/"posting.txt").write_text("\n".join(post_lines)+"\n", encoding="utf-8")
(FOLDER/f"a7_{MATRICULA}.txt").write_text(
    "\n".join(log)+f"\n\nTiempo total de ejecucion del programa: {time.perf_counter()-t0:.2f} segundos\n",
    encoding="utf-8"
)

print("OK → dictionary.txt, posting.txt y log A7 generados.")
