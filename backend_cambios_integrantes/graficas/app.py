# NUEVO: SERVICIO PYTHON (FLASK + MATPLOTLIB) QUE DIBUJA LAS GRAFICAS
# NUEVO: EL BACKEND JAVA LE ENVIA LOS DATOS EN JSON Y ESTE SERVICIO RESPONDE UNA IMAGEN PNG
import os

from flask import Flask, Response, abort, jsonify, request

from charts import GRAFICAS
from samples import MUESTRAS

app = Flask(__name__)

# NUEVO: CLAVE OPCIONAL COMPARTIDA CON EL BACKEND JAVA (VARIABLE DE ENTORNO GRAFICAS_API_KEY)
API_KEY = os.environ.get("GRAFICAS_API_KEY", "")


def _png(datos):
    # NUEVO: ARMA LA RESPUESTA HTTP CON LA IMAGEN
    return Response(datos, mimetype="image/png", headers={"Cache-Control": "no-store"})


@app.get("/health")
def health():
    # NUEVO: VERIFICA QUE EL SERVICIO ESTE VIVO Y LISTA LAS GRAFICAS DISPONIBLES
    return jsonify(status="ONLINE", graficas=sorted(GRAFICAS.keys()))


@app.post("/render/<nombre>")
def render(nombre):
    # NUEVO: RUTA QUE USA EL BACKEND JAVA (RECIBE JSON, DEVUELVE PNG)
    if API_KEY and request.headers.get("X-Graficas-Key") != API_KEY:
        abort(401)
    if nombre not in GRAFICAS:
        abort(404)
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        abort(400)
    return _png(GRAFICAS[nombre](datos))


@app.get("/demo/<nombre>.png")
def demo(nombre):
    # NUEVO: RUTA DE PRUEBA CON DATOS DE EJEMPLO, SIRVE PARA VER LAS GRAFICAS SIN BASE DE DATOS
    if nombre not in GRAFICAS:
        abort(404)
    return _png(GRAFICAS[nombre](MUESTRAS[nombre]))


@app.get("/")
def indice():
    # NUEVO: PAGINA SIMPLE PARA VER TODAS LAS GRAFICAS DE EJEMPLO DIRECTAMENTE EN EL NAVEGADOR
    items = "".join(
        f'<h3 style="font-family:sans-serif">{n}</h3><img style="max-width:100%" src="/demo/{n}.png">'
        for n in sorted(GRAFICAS.keys())
    )
    return f"<!doctype html><meta charset='utf-8'><title>Graficas (demo)</title><body style='margin:24px'>{items}</body>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
