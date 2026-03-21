from flask import Flask, render_template, request, redirect, url_for, session
from gestor_usuarios import GestorUsuarios

app = Flask(__name__)
app.secret_key = "clave-secreta"  # necesaria para usar session
gestor = GestorUsuarios()

@app.route("/")
def home():
    # si ya hay usuario en sesión, mostrar menú
    if "usuario" in session:
        return redirect(url_for("menu_tareas"))
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    usuario_actual = gestor.login_web(username, password)
    if usuario_actual:
        # guardamos el usuario en sesión
        session["usuario"] = {
            "username": usuario_actual.username,
            "nivel": usuario_actual.nivel,
            "clase": usuario_actual.clase
        }
        return redirect(url_for("menu_tareas"))
    else:
        return render_template("login.html", error="Usuario o contraseña incorrectos")

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    usuario_actual = gestor.register_web(username, password)
    if usuario_actual:
        session["usuario"] = {
            "username": usuario_actual.username,
            "nivel": usuario_actual.nivel,
            "clase": usuario_actual.clase
        }
        return redirect(url_for("menu_tareas"))
    else:
        return render_template("login.html", error="No se pudo registrar")

@app.route("/menu")
def menu_tareas():
    usuario = session.get("usuario")
    if usuario:
        return render_template("menu.html", usuario=usuario)
    else:
        return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
