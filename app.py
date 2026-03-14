from flask import Flask, render_template, request, redirect, url_for
from gestor_usuarios import GestorUsuarios

app = Flask(__name__)
gestor = GestorUsuarios()

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    usuario_actual = gestor.login_web(username, password)  # método que deberías crear en GestorUsuarios
    if usuario_actual:
        return redirect(url_for("menu_tareas"))
    else:
        return render_template("login.html", error="Usuario o contraseña incorrectos")

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    usuario_actual = gestor.register_web(username, password)  # método que deberías crear en GestorUsuarios
    if usuario_actual:
        return redirect(url_for("menu_tareas"))
    else:
        return render_template("login.html", error="No se pudo registrar")

@app.route("/menu")
def menu_tareas():
    return "Aquí iría tu menú de tareas en versión web"

if __name__ == "__main__":
    app.run(debug=True)
