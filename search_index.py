
from pathlib import Path
from collections import defaultdict, Counter
import argparse, re, time, math

TOKEN_RE = re.compile(r"[a-z0-9áéíóúüñ']+", re.I)
W_TOKEN, W_DF, W_START = 13, 3, 4
W_DOC,   W_WEIGHT      = 3, 7
DECIMALS = 4

def read_stoplist(path: Path):
    return set(w.strip().lower() for w in path.read_text(encoding="utf-8").splitlines() if w.strip())

def strip_html(s: str) -> str:
    return re.sub(r"<[^>]+>", " ", s)

def tokenize_cmd(input_dir: Path, output_dir: Path, stoplist: Path, max_docs: int | None):
    stop = read_stoplist(stoplist)
    files = sorted([p for p in input_dir.iterdir() if p.suffix==".html" and p.stem.isdigit()],
                   key=lambda p: int(p.stem))
    if max_docs: files = files[:max_docs]
    tokdir = output_dir/"tokens"
    tokdir.mkdir(parents=True, exist_ok=True)

    t0=time.perf_counter(); log=[]
    total_tokens=0
    for p in files:
        t1=time.perf_counter()
        txt = strip_html(p.read_text(encoding="utf-8", errors="replace")).lower()
        toks = [t for t in TOKEN_RE.findall(txt) if len(t)>1 and t not in stop]
        (tokdir/f"{p.stem}.tok.txt").write_text("\n".join(toks), encoding="utf-8")
        total_tokens += len(toks)
        log.append(f"{p}\t{time.perf_counter()-t1:.2f}")
    total=time.perf_counter()-t0
    (output_dir/f"a_tokenize_2955178.txt").write_text(
        "\n".join(log)+f"\n\nTiempo total tokenize: {total:.2f} s\nTokens generados: {total_tokens}\n",
        encoding="utf-8")
    print(f"Tokenize OK ({len(files)} docs) en {total:.2f}s. Tokens: {total_tokens}")

def index_cmd(input_dir: Path, output_dir: Path, stoplist: Path, min_freq: int, max_docs: int | None):
    stop = read_stoplist(stoplist)
    files = sorted([p for p in input_dir.iterdir() if p.suffix==".html" and p.stem.isdigit()],
                   key=lambda p: int(p.stem))
    if max_docs: files = files[:max_docs]
    N=len(files)

    t0=time.perf_counter(); log=[]
    postings=defaultdict(list)
    for p in files:
        t1=time.perf_counter()
        txt = strip_html(p.read_text(encoding="utf-8", errors="replace")).lower()
        toks = [t for t in TOKEN_RE.findall(txt) if len(t)>1 and t not in stop]
        for w,c in Counter(toks).items(): postings[w].append((p.name, c))
        log.append(f"{p}\t{time.perf_counter()-t1:.2f}")

    if min_freq>1:
        totals={w: sum(c for _,c in pairs) for w,pairs in postings.items()}
        postings={w:p for w,p in postings.items() if totals[w]>=min_freq}

    for w in postings: postings[w].sort(key=lambda dc:int(dc[0][:-5]))

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

    n_tokens=len(postings)
    size=next_prime(max(2, math.ceil(n_tokens/0.70)))
    table=[None]*size
    for w in postings:
        i=djb2(w)%size
        while table[i] and table[i][0]!=w: i=(i+1)%size
        table[i]=(w, len(postings[w]))

    dict_lines=[]; post_lines=[]; cursor=0
    for slot in table:
        if slot is None:
            dict_lines.append("".ljust(W_TOKEN) + "0".rjust(W_DF) + "-1".rjust(W_START))
        else:
            w,df=slot
            dict_lines.append(w[:W_TOKEN].ljust(W_TOKEN)+str(df).rjust(W_DF)+str(cursor).rjust(W_START))
            idf = math.log10(N/df) if df else 0.0
            for doc,f in postings[w]:
                tf = 1.0 + math.log10(f) if f>0 else 0.0
                weight = tf*idf
                docid = int(Path(doc).stem)
                post_lines.append(str(docid).rjust(W_DOC) + f"{weight:{W_WEIGHT}.{DECIMALS}f}")
            cursor += df

    (output_dir/"dictionary_hash.txt").write_text("\n".join(dict_lines)+"\n", encoding="utf-8")
    (output_dir/"posting.txt").write_text("\n".join(post_lines)+"\n", encoding="utf-8")
    total=time.perf_counter()-t0
    (output_dir/"a10_2955178.txt").write_text(
        "\n".join(log)+f"\n\nTiempo total index (tokenize+index): {total:.2f} s\nTokens unicos diccionario: {n_tokens}\n",
        encoding="utf-8")
    print(f"Index OK ({n_tokens} tokens) en {total:.2f}s → dictionary_hash.txt / posting.txt")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="cmd", required=True)

    a=sub.add_parser("tokenize")
    a.add_argument("input_dir", type=Path)
    a.add_argument("output_dir", type=Path)
    a.add_argument("--stoplist", type=Path, required=True)
    a.add_argument("--max_docs", type=int, default=None)

    b=sub.add_parser("index")
    b.add_argument("input_dir", type=Path)
    b.add_argument("output_dir", type=Path)
    b.add_argument("--stoplist", type=Path, required=True)
    b.add_argument("--min_freq", type=int, default=2)
    b.add_argument("--max_docs", type=int, default=None)

    args=ap.parse_args()
    if args.cmd=="tokenize":
        tokenize_cmd(args.input_dir, args.output_dir, args.stoplist, args.max_docs)
    else:
        index_cmd(args.input_dir, args.output_dir, args.stoplist, args.min_freq, args.max_docs)
