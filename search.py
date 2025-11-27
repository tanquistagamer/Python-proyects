def search(query_tokens, base: Path, use_stop: bool, log_path: Path|None):
    # Usar la versión sin prints para obtener resultados
    results, elapsed = search_scores(query_tokens, base, use_stop)

    # ----- salida en consola -----
    print("Retrieve", " ".join(query_tokens))
    if not results:
        print("(sin resultados)")
    else:
        print("Top documents")
        for i, (name, sc) in enumerate(results, 1):
            print(f"{i:2d}. {name}")

    # ----- log -----
    if log_path:
        log_path = Path(log_path)
        with log_path.open("a", encoding="utf-8") as lg:
            lg.write(f"QUERY: {' '.join(query_tokens)} | "
                     f"stoplist={'ON' if use_stop else 'OFF'} | "
                     f"time={elapsed:.4f}s\n")
            if not results:
                lg.write("  (sin resultados)\n\n")
            else:
                for i, (name, sc) in enumerate(results, 1):
                    lg.write(f"  {i:2d}. {name}  score={sc:.6f}\n")
                lg.write("\n")
