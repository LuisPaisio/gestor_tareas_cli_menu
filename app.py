from flask import Flask, render_template, request, redirect, url_for, session, flash
from gestor_usuarios import GestorUsuarios
from gestor_tareas import GestorTareas
from gestor_recompensa import GestorRecompensas
from constantes_tareas import vida_maxima, mana_maximo
from gestor_notificaciones import GestorNotificaciones
import datetime

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
            "clase_nombre": usuario_actual.clase_nombre,
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
            "clase_nombre": usuario_actual.clase_nombre,
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
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])

    # 🔹 Verificar si el VIP expiró
    eventos_expiracion = usuario_obj.verificar_vip()
    if eventos_expiracion:
        for e in eventos_expiracion:
            flash(e["mensaje"], e["accion"])
        gestor.actualizar_usuario(usuario_obj)

    gestor_tareas = GestorTareas(usuario=usuario_obj, gestor_usuarios=gestor)
    tareas = gestor_tareas.ver_tareas_web()

    # 🔹 Detectar diarias y pendientes vencidas
    vencidas = gestor_tareas.verificar_diarias_web()
    diarias_vencidas = vencidas["diarias_vencidas"]
    pendientes_vencidas = vencidas["pendientes_vencidas"]

    # 🔹 Bonus diario VIP
    bonus = usuario_obj.aplicar_bonus_diario()
    if bonus:
        flash(bonus["mensaje"], bonus["categoria"])

    # 🔹 Recompensa VIP mensual
    eventos_vip = usuario_obj.dar_recompensa_vip()
    if eventos_vip:
        gestor.actualizar_usuario(usuario_obj)
        for e in eventos_vip:
            flash(e["mensaje"], e["accion"])

    vida_max = vida_maxima()
    mana_max = mana_maximo()
    xp_req = usuario_obj.xp_requerida()

    gestor_notificaciones = GestorNotificaciones()
    notificaciones_lista = gestor_notificaciones.obtener_notificaciones(usuario_obj.id_usuario)[:5]

    # 🔹 Mostrar modal solo una vez al día
    hoy = datetime.date.today().strftime("%Y-%m-%d")
    mostrar_modal = False
    if session.get("ultimo_modal") != hoy:
        if diarias_vencidas or pendientes_vencidas:
            mostrar_modal = True
            session["ultimo_modal"] = hoy

    return render_template(
        "dashboard.html",
        usuario=usuario_obj,
        habitos=tareas["habitos"],
        diarias=tareas["diarias"],
        pendientes=tareas["pendientes"],
        vida_maxima=vida_max,
        mana_maximo=mana_max,
        xp_requerida=xp_req,
        notificaciones=notificaciones_lista,
        pagina_actual=1,
        total_paginas=1,
        diarias_vencidas=diarias_vencidas,       # 🔹 para el modal
        pendientes_vencidas=pendientes_vencidas, # 🔹 para el modal
        mostrar_modal=mostrar_modal              # 🔹 flag para abrir modal
    )


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
        habito = habito or "+-"   # por defecto mixto
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
    # Aquí deberías pasar la lista real de recompensas seleccionadas
    recompensas = gestor_recompensas.aplicar_recompensas(usuario_obj, [...], es_penalizacion=False)

    # Pasar resultados como flash messages
    for r in recompensas:
        total = r['resultado']['total']
        tipo = r['tipo'].upper()

        # Usar categorías estándar para los toasts
        if r['tipo'] == "xp":
            flash(f"{tipo} +{total} obtenido", "success")
        elif r['tipo'] == "coin":
            flash(f"{tipo} +{total} obtenido", "success")
        elif r['tipo'] == "vida":
            flash(f"{tipo} +{total} obtenido", "info")  # vida como info, porque es recuperación
        else:
            flash(f"{tipo} +{total} obtenido", "success")

    return redirect(url_for("dashboard"))

@app.route("/marcar_tarea/<int:tarea_id>/<accion>", methods=["POST"])
def marcar_tarea(tarea_id, accion):
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])
    gestor_tareas = GestorTareas(usuario=usuario_obj, gestor_usuarios=gestor)

    # 🔹 Leer flags del formulario (hidden inputs en el modal)
    retroactivo = request.form.get("retroactivo") == "true"
    por_medianoche = request.form.get("por_medianoche") == "true"

    # 🔹 Pasar los flags a marcar_tarea_web
    resultado = gestor_tareas.marcar_tarea_web(
        tarea_id,
        accion,
        retroactivo=retroactivo,
        por_medianoche=por_medianoche
    )

    if "error" in resultado:
        flash(resultado["error"], "error")
    else:
        # mensaje general enriquecido
        flash(resultado["mensaje"], "info")

        # recompensas
        for r in resultado.get("recompensas", []):
            flash(f"{r['tipo'].upper()} +{r['resultado']['total']}", r['tipo'])

        # penalizaciones
        for p in resultado.get("penalizaciones", []):
            flash(p.get("mensaje", f"{p['tipo'].upper()} {p['resultado']['total']}"), f"{p['tipo']}-neg")

        # eventos de progresión (nivel, maná, prestigio)
        for e in resultado.get("eventos", []):
            flash(e["mensaje"], e["accion"])

    return redirect(url_for("dashboard"))

@app.route("/elegir_clase", methods=["POST"])
def elegir_clase():
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])
    clase_nombre = request.form["clase"]

    # asignar clase al usuario
    from clases import Clase
    usuario_obj.clase = Clase.cargar_clase(clase_nombre, usuario_obj.rol == "vip")
    usuario_obj.clase_nombre = clase_nombre

    gestor.actualizar_usuario(usuario_obj)
    flash(f"✨ Has elegido la clase {clase_nombre}. ¡Ya puedes usar poderes!", "success")

    return redirect(url_for("dashboard"))

@app.route("/prestigiar", methods=["POST"])
def prestigiar():
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])
    eventos = usuario_obj.reiniciar_nivel_100()  # ahora devuelve lista de eventos

    gestor.actualizar_usuario(usuario_obj)

    # flashear todos los eventos de prestigio
    for e in eventos:
        flash(e["mensaje"], e["accion"])

    return redirect(url_for("dashboard"))

@app.route("/activar_vip", methods=["POST"])
def activar_vip():
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])
    eventos = usuario_obj.activar_vip()

    # flashear eventos de activación (ej. bienvenida, coins iniciales)
    for e in eventos:
        flash(e["mensaje"], e["accion"])

    # persistir cambios
    gestor.actualizar_usuario(usuario_obj)

    return redirect(url_for("dashboard"))

@app.route("/notificacion/<int:id_notificacion>/leer", methods=["POST", "GET"])
def marcar_leida(id_notificacion):
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])
    gestor_notificaciones = GestorNotificaciones()
    gestor_notificaciones.marcar_leida(usuario_obj.id_usuario, str(id_notificacion))

    flash("Notificación marcada como leída", "success")
    return redirect(url_for("dashboard"))


@app.route("/notificacion/<int:id_notificacion>/eliminar", methods=["POST", "GET"])
def eliminar_notificacion(id_notificacion):
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])
    gestor_notificaciones = GestorNotificaciones()
    gestor_notificaciones.eliminar_notificacion(usuario_obj.id_usuario, str(id_notificacion))

    flash("Notificación eliminada", "success")
    return redirect(url_for("dashboard"))

@app.route("/procesar_vencidas", methods=["POST"])
def procesar_vencidas():
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])
    gestor_tareas = GestorTareas(usuario=usuario_obj, gestor_usuarios=gestor)

    vencidas = gestor_tareas.verificar_diarias_web()
    diarias_vencidas = vencidas["diarias_vencidas"]
    pendientes_vencidas = vencidas["pendientes_vencidas"]

    # Penalizar automáticamente las diarias como incompletas por medianoche
    for d in diarias_vencidas:
        resultado = gestor_tareas.marcar_tarea_web(
            tarea_id=d.id,
            accion="incompleta",
            retroactivo=False,
            por_medianoche=True
        )
        # 🔹 Flashear el mensaje para que aparezca el toast
        flash(resultado["mensaje"], "vida" if resultado["penalizaciones"] else "info")

    # Las pendientes vencidas se dejan sin tocar (solo acumulan bonificación)

    gestor.actualizar_usuario(usuario_obj)
    return ("", 204)  # respuesta vacía



if __name__ == "__main__":
    app.run(debug=True)

