#!C:\Python312\python.exe
# -*- coding: utf-8 -*-

import os, sys, cgi, json
from pathlib import Path

# Haz visible tu paquete School para importar retrieve13.py
sys.path.append(r"C:\Users\Tanqu\OneDrive\Documentos\GitHub\School")
import retrieve13  # tu módulo

# Ruta base a tus índices (puede ser otra si copiaste a inetpub\data)
BASE = Path(r"C:\Users\Tanqu\OneDrive\Documentos\GitHub\School\Files")
LOG  = BASE / "a13_2955178.txt"

def _b(s: str) -> bool:
    return s.lower() in ("1","true","yes","on")

def main():
    form = cgi.FieldStorage()
    q      = (form.getfirst("q", "") or "").strip()
    nostop = _b(form.getfirst("nostop", "0"))
    topk   = int(form.getfirst("k", "10") or "10")
    fmt    = (form.getfirst("fmt", "html") or "html").lower()

    results, elapsed = retrieve13.run_query(
        q=q, base=BASE, use_stop=(not nostop), topk=topk
    )

    # Log
    try:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"retrieve q={q!r} nostop={nostop} k={topk} -> {len(results)} hits in {elapsed:.3f}s\n")
    except Exception:
        pass

    if fmt == "json":
        print("Content-Type: application/json; charset=utf-8"); print()
        print(json.dumps({
            "q": q, "nostop": nostop, "time_s": round(elapsed, 3),
            "results": [{"doc": d, "score": s} for d, s in results]
        }, ensure_ascii=False))
        return

    print("Content-Type: text/html; charset=utf-8"); print()
    print("<html><head><meta charset='utf-8'><title>Search CGI</title></head><body>")
    print("<form method='get'><input name='q' style='width:350px' placeholder='consulta'>")
    print("<label><input type='checkbox' name='nostop' value='1'> sin stoplist</label>")
    print("<input name='k' value='10' size='3'><button>Buscar</button></form><hr>")
    print(f"<p><b>Consulta:</b> {q or '(vacía)'} | stoplist: {'ON' if not nostop else 'OFF'} | k={topk} | <b>tiempo:</b> {elapsed:.3f}s</p>")
    if not results:
        print("<p><em>(sin resultados)</em></p>")
    else:
        print("<ol>")
        for doc, sc in results:
            print(f"<li>{doc} &mdash; <code>{sc:.4f}</code></li>")
        print("</ol>")
    print("</body></html>")

if __name__ == "__main__":
    main()
