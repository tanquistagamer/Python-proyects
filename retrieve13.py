# retrieve13.py — A13: consulta sin cargar índices en memoria (Top-10)
from pathlib import Path
import argparse, re, time, math

# Campos de ancho fijo (A10/A11)
W_TOKEN, W_DF, W_START = 13, 3, 4       # diccionario (20B)
W_DOC,   W_WEIGHT      = 3, 7           # posting (10B)
REC_DICT = W_TOKEN + W_DF + W_START
REC_POST = W_DOC + W_WEIGHT

# Normalización igual que el indexador
TOKEN_RE = re.compile(r"[a-z0-9áéíóúüñ']+", re.I)

def toks(q: str):
    return [t for t in TOKEN_RE.findall(q.lower()) if len(t) > 1]

# ---------- utilidades de lectura línea-a-línea (no offsets de bytes) ----------
def read_line(fp, n: int) -> str:
    """Lee la línea n (1-based) sin \r\n."""
    fp.seek(0)
    for _ in range(n - 1):
        if not fp.readline():
            return ""
    s = fp.readline()
    return s.rstrip("\r\n")

def read_dict_slot(fp, lineno: int):
    """Devuelve (token, df, start) desde el diccionario fijo."""
    raw = read_line(fp, lineno)
    if len(raw) < REC_DICT:
        raw += " " * (REC_DICT - len(raw))
    tok  = raw[:W_TOKEN].rstrip()
    df_s = raw[W_TOKEN:W_TOKEN+W_DF].strip() or "0"
    st_s = raw[W_TOKEN+W_DF:W_TOKEN+W_DF+W_START].strip() or "-1"
    try:
        df    = int(df_s)
        start = int(st_s)
    except ValueError:
        df, start = 0, -1
    return tok, df, start

def read_post_record(fp, lineno: int):
    """Devuelve (docID, weight) desde posting fijo."""
    raw = read_line(fp, lineno)
    if len(raw) < REC_POST:
        raw += " " * (REC_POST - len(raw))
    did = int((raw[:W_DOC].strip() or "0"))
    try:
        w = float((raw[W_DOC:W_DOC+W_WEIGHT].strip() or "0"))
    except ValueError:
        w = 0.0
    return did, w

def read_docname(documents_path: Path, docid: int) -> str:
    """Lee el nombre del documento con ese docID (1-based)."""
    with documents_path.open("r", encoding="utf-8") as f:
        line = read_line(f, docid)
    return line.split(maxsplit=1)[-1] if line else f"{docid:03d}.html"

def count_lines(p: Path) -> int:
    n = 0
    with p.open("r", encoding="utf-8") as f:
        for _ in f: n += 1
    return n

# ---------- hash y búsqueda en el diccionario ----------
def djb2(s: str) -> int:
    h = 5381
    for ch in s:
        h = ((h << 5) + h) + ord(ch)
    return h & 0xFFFFFFFF

def find_token_in_dict(dict_path: Path, token: str):
    """Linear probing sobre archivo: regresa (df, start). Si no está → (0, -1)."""
    size = count_lines(dict_path)                 # tamaño de la tabla hash (= #líneas)
    with dict_path.open("r", encoding="utf-8") as f:
        i0 = djb2(token) % size                   # índice 0-based
        for step in range(size):
            lineno = (i0 + step) % size + 1       # 1-based
            tok, df, start = read_dict_slot(f, lineno)
            # hueco: token vacío + start -1
            if (not tok) and start == -1:
                return 0, -1
            if tok == token:
                return df, start
    return 0, -1

# ---------- búsqueda ----------
def search(query_tokens, base: Path, use_stop: bool, log_path: Path|None):
    # Selección de archivos (con o sin stoplist)
    suf = "" if use_stop else "_all"
    dict_path = base / f"dictionary_hash{suf}.txt"
    post_path = base / f"posting{suf}.txt"
    docs_path = base / f"documents{suf}.txt"

    t0 = time.perf_counter()
    scores = {}  # docID -> acumulado de pesos

    with post_path.open("r", encoding="utf-8") as post_fp:
        for q in query_tokens:
            df, start = find_token_in_dict(dict_path, q)
            if df <= 0 or start < 0:
                continue
            # leer df registros a partir de start (start es 0-based en el indexador)
            for k in range(df):
                did, w = read_post_record(post_fp, start + k + 1)  # 1-based
                if did:
                    scores[did] = scores.get(did, 0.0) + w

    elapsed = time.perf_counter() - t0

    # Top-10 por score
    top = sorted(scores.items(), key=lambda x: (-x[1], x[0]))[:10]

    # ----- salida en consola -----
    print("Retrieve", " ".join(query_tokens))
    if not top:
        print("(sin resultados)")
    else:
        print("Top documents")
        for i, (did, sc) in enumerate(top, 1):
            name = read_docname(docs_path, did)
            print(f"{i:2d}. {name}")

    # ----- log -----
    if log_path:
        log_path = Path(log_path)
        with log_path.open("a", encoding="utf-8") as lg:
            lg.write(f"QUERY: {' '.join(query_tokens)} | "
                     f"stoplist={'ON' if use_stop else 'OFF'} | "
                     f"time={elapsed:.4f}s\n")
            if not top:
                lg.write("  (sin resultados)\n\n")
            else:
                for i, (did, sc) in enumerate(top, 1):
                    name = read_docname(docs_path, did)
                    lg.write(f"  {i:2d}. {did:03d} {name}  score={sc:.6f}\n")
                lg.write("\n")

def main():
    ap = argparse.ArgumentParser(
        description="retrieve13: consulta de términos/frases (Top-10) sin cargar índices en memoria")
    ap.add_argument("query", nargs="+")
    ap.add_argument("--dir", default=".", help="carpeta con dictionary*/posting*/documents*")
    ap.add_argument("--nostop", action="store_true", help="usar archivos *_all (sin stoplist)")
    ap.add_argument("--log", default=None, help="archivo log (a13_matricula.txt)")
    args = ap.parse_args()

    base = Path(args.dir)
    qtokens = []
    # Acepta varias palabras y frases; cada arg se tokeniza con la misma regex del índice
    for part in args.query:
        qtokens += toks(part)

    if not qtokens:
        print("No hay tokens de búsqueda después de normalizar.")
        return

    search(qtokens, base, use_stop=(not args.nostop), log_path=Path(args.log) if args.log else None)

if __name__ == "__main__":
    main()
