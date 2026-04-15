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
    return render_template("home.html")

@app.route("/login", methods=["POST"])
def login():
    nombre_usuario = request.form["username"]
    password = request.form["password"]
    usuario_actual = gestor.login_web(nombre_usuario, password)
    if usuario_actual:
        # guardamos el usuario en sesión
        session["usuario"] = {
            #"usuario": usuario_actual.usuario,
            "usuario": usuario_actual.nombre_publico if usuario_actual.nombre_publico else usuario_actual.usuario,
            "nivel": usuario_actual.nivel_usuario,
            "clase": usuario_actual.clase.nombre if usuario_actual.clase else None,
            "foto_perfil": usuario_actual.foto_perfil
        }
        return redirect(url_for("menu_tareas"))
    else:
        return render_template("home.html", error="Usuario o contraseña incorrectos")

@app.route("/register", methods=["POST"])
def register():
    nombre_usuario = request.form["username"]
    password = request.form["password"]
    usuario_actual = gestor.register_web(nombre_usuario, password)
    if usuario_actual:
        session["usuario"] = {
            "usuario": usuario_actual.nombre_publico if usuario_actual.nombre_publico else usuario_actual.usuario,
            "nivel": usuario_actual.nivel_usuario,
            "clase": usuario_actual.clase.nombre if usuario_actual.clase else None,
            "foto_perfil": usuario_actual.foto_perfil
        }
        return redirect(url_for("menu_tareas"))
    else:
        return render_template("home.html", error="No se pudo registrar")

@app.route("/menu")
def menu_tareas():
    usuario = session.get("usuario")
    if usuario:
        return render_template("dashboard.html", usuario=usuario)
    else:
        return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("home"))

@app.route("/register_page")
def register_page():
    return render_template("soloregister.html")

@app.route("/login_page")
def login_page():
    return render_template("solologin.html")

@app.route("/dashboard")
def dashboard():
    usuario = session.get("usuario")
    if not usuario:
        return redirect(url_for("home"))

    gestor_tareas = GestorTareas(usuario_actual, gestor)
    tareas_usuario = gestor_tareas.tareas_usuario()

    gestor_recompensas = GestorRecompensas()
    recompensas_usuario = gestor_recompensas.recompensas_usuario(usuario_actual)

    return render_template("dashboard.html", usuario=usuario, tareas=tareas_usuario, recompensas=recompensas_usuario)

@app.route("/nueva_recompensa", methods=["GET", "POST"])
def nueva_recompensa():
    usuario = session.get("usuario")
    if not usuario:
        return redirect(url_for("home"))

    if request.method == "POST":
        titulo = request.form["titulo"]
        costo = int(request.form["costo"])

        gestor_recompensas = GestorRecompensas()
        gestor_recompensas.nueva_recompensa(usuario_actual, titulo, costo)

        return redirect(url_for("dashboard"))

    return render_template("nueva_recompensa.html", usuario=usuario)


@app.route("/estadisticas")
def estadisticas():
    usuario = session.get("usuario")
    if not usuario:
        return redirect(url_for("home"))
    # acá podrías mostrar estadísticas del usuario
    return render_template("estadisticas.html", usuario=usuario)

@app.route("/poderes")
def menu_poderes():
    usuario = session.get("usuario")
    if not usuario:
        return redirect(url_for("home"))
    return render_template("poderes.html", usuario=usuario)

@app.route("/inventario")
def menu_inventario():
    usuario = session.get("usuario")
    if not usuario:
        return redirect(url_for("home"))
    return render_template("inventario.html", usuario=usuario)

@app.route("/mascotas")
def menu_mascotas():
    usuario = session.get("usuario")
    if not usuario:
        return redirect(url_for("home"))
    return render_template("mascotas.html", usuario=usuario)

@app.route("/tienda")
def menu_tienda():
    usuario = session.get("usuario")
    if not usuario:
        return redirect(url_for("home"))
    return render_template("tienda.html", usuario=usuario)

@app.route("/nueva_tarea", methods=["GET", "POST"])
def nueva_tarea():
    usuario = session.get("usuario")
    if not usuario:
        return redirect(url_for("home"))

    if request.method == "POST":
        titulo = request.form["titulo"]
        tipo = int(request.form["tipo"])
        dificultad = request.form["dificultad"]

        gestor_tareas = GestorTareas(usuario_actual, gestor)
        gestor_tareas.nueva_tarea(titulo, tipo, dificultad)
        return redirect(url_for("dashboard"))

    return render_template("nueva_tarea.html", usuario=usuario)

if __name__ == "__main__":
    app.run(debug=True)
