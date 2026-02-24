from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)

BASE_URL = "http://127.0.0.1:8000/v1/usuarios/"


@app.route("/")
def inicio():
    respuesta = requests.get(BASE_URL)
    datos = respuesta.json()
    return render_template("index.html", usuarios=datos["usuarios"])



@app.route("/crear", methods=["POST"])
def crear():
    nuevo_usuario = {
        "id": int(request.form["id"]),
        "nombre": request.form["nombre"],
        "edad": int(request.form["edad"])
    }

    requests.post(BASE_URL, json=nuevo_usuario)
    return redirect("/")



@app.route("/actualizar/<int:id>", methods=["POST"])
def actualizar(id):
    usuario_actualizado = {
        "id": id,
        "nombre": request.form["nombre"],
        "edad": int(request.form["edad"])
    }

    requests.put(f"{BASE_URL}{id}", json=usuario_actualizado)
    return redirect("/")

@app.route("/parcial/<int:id>", methods=["POST"])
def parcial(id):
    datos_parciales = {}

    if request.form["nombre"]:
        datos_parciales["nombre"] = request.form["nombre"]

    if request.form["edad"]:
        datos_parciales["edad"] = int(request.form["edad"])

    requests.patch(f"{BASE_URL}{id}", json=datos_parciales)
    return redirect("/")



@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    requests.delete(f"{BASE_URL}{id}")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
