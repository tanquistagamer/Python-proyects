# bench.py
import subprocess, time, csv
from pathlib import Path
import matplotlib.pyplot as plt

FOLDER = r"C:\Users\Tanqu\OneDrive\Documentos\GitHub\School\Files"
STOP   = FOLDER + r"\stoplist_en.txt"
NS = [10,20,30,40,50]  # agrega más si quieres

tok_times=[]; idx_times=[]
for n in NS:
    t0=time.perf_counter()
    subprocess.run(["python","search_index.py","tokenize",FOLDER,FOLDER,"--stoplist",STOP,"--max_docs",str(n)], check=True)
    tok_times.append(time.perf_counter()-t0)

    t0=time.perf_counter()
    subprocess.run(["python","search_index.py","index",FOLDER,FOLDER,"--stoplist",STOP,"--max_docs",str(n)], check=True)
    idx_times.append(time.perf_counter()-t0)

with open(Path(FOLDER)/"times.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["docs","tokenize_s","tokenize+index_s"])
    for n,t1,t2 in zip(NS,tok_times,idx_times): w.writerow([n,round(t1,2),round(t2,2)])

# Gráfica 1: solo tokenización
plt.figure()
plt.plot(NS, tok_times, marker="o")
plt.xlabel("N documentos"); plt.ylabel("Tiempo (s)"); plt.title("Tiempo de Tokenización")
plt.savefig(Path(FOLDER)/"grafica_tokenize.png", dpi=120)

# Gráfica 2: tokenización + indexación
plt.figure()
plt.plot(NS, idx_times, marker="o")
plt.xlabel("N documentos"); plt.ylabel("Tiempo (s)"); plt.title("Tiempo Tokenización + Indexación")
plt.savefig(Path(FOLDER)/"grafica_tokenize_index.png", dpi=120)
