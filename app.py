from flask import Flask, render_template, request, redirect, url_for, session, flash
from gestor_usuarios import GestorUsuarios
from gestor_tareas import GestorTareas
from gestor_recompensa import GestorRecompensas

app = Flask(__name__)
app.secret_key = "clave-secreta"  # necesaria para usar session
gestor = GestorUsuarios()

@app.route("/")
def home():
    if "usuario" in session:
        return redirect(url_for("dashboard"))  # ahora va directo al dashboard
    return render_template("home.html")

@app.route("/login", methods=["POST"])
def login():
    nombre_usuario = request.form["username"]
    password = request.form["password"]
    usuario_actual = gestor.login_web(nombre_usuario, password)
    if usuario_actual:
        # guardamos datos básicos en sesión
        session["usuario"] = {
            "id_usuario": usuario_actual.id_usuario,
            "nombre": usuario_actual.usuario,  # identificador real
            "usuario": usuario_actual.nombre_publico if usuario_actual.nombre_publico else usuario_actual.usuario,
            "nivel": usuario_actual.nivel_usuario,
            "clase": usuario_actual.clase.nombre if usuario_actual.clase else None,
            "foto_perfil": usuario_actual.foto_perfil
        }
        return redirect(url_for("dashboard"))  # directo al dashboard
    else:
        return render_template("home.html", error="Usuario o contraseña incorrectos")

@app.route("/register", methods=["POST"])
def register():
    nombre_usuario = request.form["username"]
    password = request.form["password"]
    usuario_actual = gestor.register_web(nombre_usuario, password)
    if usuario_actual:
        session["usuario"] = {
            "id_usuario": usuario_actual.id_usuario,
            "nombre": usuario_actual.usuario,
            "usuario": usuario_actual.nombre_publico if usuario_actual.nombre_publico else usuario_actual.usuario,
            "nivel": usuario_actual.nivel_usuario,
            "clase": usuario_actual.clase.nombre if usuario_actual.clase else None,
            "foto_perfil": usuario_actual.foto_perfil
        }
        return redirect(url_for("dashboard"))  # directo al dashboard
    else:
        return render_template("home.html", error="No se pudo registrar")

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
    print("DEBUG: Entrando al route /dashboard")
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    # recuperar objeto usuario real desde gestor usando id_usuario
    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])

    gestor_tareas = GestorTareas(usuario=usuario_obj, gestor_usuarios=gestor)
    tareas = gestor_tareas.ver_tareas_web()  # devuelve habitos, diarias, pendientes

    gestor_recompensas = GestorRecompensas()
    recompensas_usuario = []

    return render_template(
        "dashboard.html",
        usuario=usuario_dict,
        habitos=tareas["habitos"],
        diarias=tareas["diarias"],
        pendientes=tareas["pendientes"],
        recompensas=recompensas_usuario
    )

@app.route("/nueva_recompensa", methods=["GET", "POST"])
def nueva_recompensa():
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])

    if request.method == "POST":
        titulo = request.form["titulo"]
        costo = int(request.form["costo"])

        gestor_recompensas = GestorRecompensas()
        gestor_recompensas.nueva_recompensa(usuario_obj, titulo, costo)

        flash("Recompensa creada exitosamente.", "success")
        return redirect(url_for("dashboard"))

    return render_template("nueva_recompensa.html", usuario=usuario_dict)

@app.route("/estadisticas")
def estadisticas():
    usuario = session.get("usuario")
    if not usuario:
        return redirect(url_for("home"))
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

@app.route("/nueva_tarea", methods=["POST"])
def nueva_tarea():
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])

    titulo = request.form["titulo"]
    tipo = int(request.form["tipo"])
    dificultad = request.form.get("dificultad", "1")  # default fácil
    dias = request.form.getlist("dias") or []         # default lista vacía
    fecha = request.form.get("fecha_vencimiento")     # puede venir vacío
    habito = request.form.get("habito")               # puede venir vacío

    # Defaults según tipo
    if tipo == 1:  # hábito
        habito = habito or "+"
        dificultad = dificultad or "1"
    elif tipo == 2:  # diaria
        dificultad = dificultad or "1"
        if not dias:  # si no se mandaron días, poner todos
            dias = ["lunes","martes","miercoles","jueves","viernes","sabado","domingo"]
    elif tipo == 3:  # pendiente
        dificultad = dificultad or "1"
        if not fecha:  # si no se mandó fecha, poner hoy + 7 días
            from datetime import date, timedelta
            fecha = (date.today() + timedelta(days=7)).isoformat()

    gestor_tareas = GestorTareas(usuario=usuario_obj, gestor_usuarios=gestor)
    gestor_tareas.crear_tarea_web(
        titulo, tipo, dificultad,
        dias_semana=dias,
        fecha_str=fecha,
        habito=habito
    )

    flash("Tarea creada exitosamente.", "success")
    return redirect(url_for("dashboard"))

@app.route("/usar_recompensa", methods=["POST"])
def usar_recompensa():
    usuario_dict = session.get("usuario")
    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])

    gestor_recompensas = GestorRecompensas()
    recompensas = gestor_recompensas.aplicar_recompensas(usuario_obj, [...])  # lista de recompensas

    # Pasar resultados como flash messages
    for r in recompensas:
        mensaje = f"{r['tipo'].upper()} {r['resultado']['total']} obtenido"
        flash(mensaje, "success")

    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
