# app.py
from pathlib import Path
from flask import Flask, render_template, request
from retrieve13 import run_query  # usamos la función wrapper que hicimos

app = Flask(__name__)

# carpeta donde están dictionary_hash*.txt, posting*.txt, documents*.txt
BASE = Path("Files")

@app.route("/", methods=["GET"])
def index():

    # solo muestra el formulario vacío
    return render_template("index.html")

@app.route("/buscar", methods=["GET"])
def buscar():
    # leer parámetros del formulario
    palabras = request.args.get("q", "").strip()
    modo = request.args.get("modo", "stop")  # 'stop' o 'nostop'

    use_stop = (modo != "nostop")  # True = con stoplist, False = sin stoplist

    # si no hay texto, regresamos la página sin resultados
    if not palabras:
        return render_template(
            "index.html",
            query=palabras,
            modo=modo,
            resultados=[],
            tiempo_ms=0,
        )

    # ejecutar buscador A13
    resultados, tiempo_ms = run_query(palabras, BASE, use_stop=use_stop)

    # renderizar la misma página pero con resultados
    return render_template(
        "index.html",
        query=palabras,
        modo=modo,
        resultados=resultados,
        tiempo_ms=tiempo_ms,
    )

if __name__ == "__main__":
    # IMPORTANTE: desde la carpeta School ejecuta: python app.py
    app.run(debug=True)
