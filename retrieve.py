# retrieve.py – A12: consulta por término/frase, imprime lista de documentos
from pathlib import Path
import argparse, re, time

W_TOKEN, W_DF, W_START = 13, 3, 4                  # campos fijos del diccionario
TOKEN_RE = re.compile(r"[a-z0-9áéíóúüñ']+", re.I)  # misma normalización que A10/A11

def toks(q: str):
    return [t for t in TOKEN_RE.findall(q.lower()) if len(t) > 1]

def load_docs(p: Path):
    m = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line: continue
        did = line[:3].strip()
        name = line[4:].strip()
        if did.isdigit(): m[int(did)] = name
    return m

def load_dict(p: Path):
    d = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        if len(line) < W_TOKEN+W_DF+W_START: continue
        tok   = line[:W_TOKEN].strip()
        df    = int(line[W_TOKEN:W_TOKEN+W_DF] or 0)
        start = int(line[W_TOKEN+W_DF:W_TOKEN+W_DF+W_START] or -1)
        if tok and df>0 and start>=0: d[tok]=(df,start)
    return d

def search(query, dictfile: Path, postfile: Path, docsfile: Path):
    D   = load_dict(dictfile)
    DOC = load_docs(docsfile)
    P   = postfile.read_text(encoding="utf-8").splitlines()

    scores = {}
    for t in toks(query):                 # OR de términos, suma tf-idf
        if t not in D: continue
        df, start = D[t]
        for line in P[start:start+df]:    # cada línea: DOCID(3) + PESO(7)
            if len(line) < 10: continue
            did = int(line[:3]); w = float(line[3:])
            scores[did] = scores.get(did, 0.0) + w

    return [DOC.get(did, f"{did:03d}.html")
            for did,_ in sorted(scores.items(), key=lambda x: (-x[1], x[0]))]

def main():
    ap = argparse.ArgumentParser(description="retrieve <query> [--nostop] [--dir DIR] [--log LOG]")
    ap.add_argument("query", nargs="+")
    ap.add_argument("--nostop", action="store_true", help="usar versión SIN stop-list (*_all.txt)")
    ap.add_argument("--dir", default=".", help="carpeta con los archivos")
    ap.add_argument("--log", default=None, help="ruta del log A12")
    a = ap.parse_args()

    base = Path(a.dir)
    if a.nostop:
        dic, pos, docs = base/"dictionary_hash_all.txt", base/"posting_all.txt", base/"documents_all.txt"
    else:
        dic, pos, docs = base/"dictionary_hash.txt", base/"posting.txt", base/"documents.txt"

    q = " ".join(a.query)
    t0 = time.perf_counter()
    res = search(q, dic, pos, docs)
    dt = time.perf_counter() - t0

    if res:
        for i, name in enumerate(res, 1): print(f"{i}. {name}")
    else:
        print("(sin resultados)")

    if a.log:
        Path(a.log).write_text("", encoding="utf-8") if not Path(a.log).exists() else None
        with open(a.log, "a", encoding="utf-8") as f:
            f.write(f"{'nostop' if a.nostop else 'stop'}\t{q}\t{dt:.4f}s\t{len(res)} resultados\n")

if __name__ == "__main__":
    main()
