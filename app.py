from flask import Flask, render_template, request, redirect, url_for, session, flash
from gestor_usuarios import GestorUsuarios
from gestor_tareas import GestorTareas
from gestor_recompensa import GestorRecompensas
from constantes_tareas import vida_maxima, mana_maximo
from gestor_notificaciones import GestorNotificaciones
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "clave-secreta"  # necesaria para usar session
app.permanent_session_lifetime = datetime.timedelta(days=30) # Duración de vida de sesión permanente
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
    mantener_sesion = request.form.get("mantener-sesion")

    # 🔹 obtener el objeto Usuario por nombre
    usuario_actual = gestor.get_usuario_por_nombre(nombre_usuario)

    # 🔹 validar contraseña contra el hash
    if usuario_actual and check_password_hash(usuario_actual.contraseña, password):
        # guardamos datos básicos en sesión
        session["usuario"] = {
            "id_usuario": usuario_actual.id_usuario,
            "nombre": usuario_actual.usuario,  # identificador real
            "usuario": usuario_actual.nombre_publico if usuario_actual.nombre_publico else usuario_actual.usuario,
            "nivel": usuario_actual.nivel_usuario,
            "clase_nombre": usuario_actual.clase_nombre,
            "foto_perfil": usuario_actual.foto_perfil
        }

        session.permanent = bool(mantener_sesion)
        return redirect(url_for("dashboard"))  # directo al dashboard
    else:
        return render_template("home.html", error="Usuario o contraseña incorrectos")

@app.route("/register", methods=["POST"])
def register():
    nombre_usuario = request.form["username"]
    password = request.form["password"]
    mantener_sesion = request.form.get("mantener-sesion")

    # 🔹 Generar el hash de la contraseña antes de guardar
    password_hash = generate_password_hash(password)

    # Pasar el hash al gestor, no la contraseña en texto plano
    usuario_actual = gestor.register_web(nombre_usuario, password_hash)
    if usuario_actual:
        session["usuario"] = {
            "id_usuario": usuario_actual.id_usuario,
            "nombre": usuario_actual.usuario,
            "usuario": usuario_actual.nombre_publico if usuario_actual.nombre_publico else usuario_actual.usuario,
            "nivel": usuario_actual.nivel_usuario,
            "clase_nombre": usuario_actual.clase_nombre,
            "foto_perfil": usuario_actual.foto_perfil
        }

        session.permanent = bool(mantener_sesion)
        return redirect(url_for("dashboard"))  # directo al dashboard
    else:
        return render_template("home.html", error="No se pudo registrar")

@app.route("/logout")
def logout():
    session.clear()  # 🔹 limpia toda la sesión, no solo el usuario
    flash("Sesión cerrada correctamente", "info")  # 🔹 mensaje para el usuario
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

    # 🔹 Mostrar modal de muerte si el flag está activo
    mostrar_modal_muerte = False
    if session.get("mostrar_modal_muerte"):
        mostrar_modal_muerte = True
        # limpiar flag para que no se repita en cada carga
        session["mostrar_modal_muerte"] = False
    
    dias_semana = {
        "Monday": "lunes",
        "Tuesday": "martes",
        "Wednesday": "miercoles",
        "Thursday": "jueves",
        "Friday": "viernes",
        "Saturday": "sabado",
        "Sunday": "domingo"
    }
    
    hoy_dia = dias_semana[datetime.date.today().strftime("%A")]
    hoy_iso = datetime.date.today().strftime("%Y-%m-%d")  # formato YYYY-MM-DD

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
        diarias_vencidas=diarias_vencidas,       #  para el modal de vencidas
        pendientes_vencidas=pendientes_vencidas, #  para el modal de vencidas
        mostrar_modal=mostrar_modal,             #  flag para modal de vencidas
        mostrar_modal_muerte=mostrar_modal_muerte, #  flag para modal de muerte
        hoy=hoy_dia,
        min_fecha=hoy_iso
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

@app.route("/perfil")
def perfil():
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])
    perfil_data = usuario_obj.ver_perfil_web()

    return render_template("perfil.html", perfil=perfil_data)

@app.route("/editar_perfil", methods=["POST"])
def editar_perfil():
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])

    # Nombre y descripción
    usuario_obj.nombre_publico = request.form.get("nombre_publico", usuario_obj.nombre_publico).strip() or usuario_obj.nombre_publico
    usuario_obj.descripcion = request.form.get("descripcion", usuario_obj.descripcion).strip() or usuario_obj.descripcion

    # Foto de perfil → mantener la anterior si el campo está vacío
    foto_input = request.form.get("foto_perfil", "").strip()
    if foto_input:
        usuario_obj.foto_perfil = foto_input
    # si no hay input, no se toca el valor actual

    # Clase si nivel >= 10
    if usuario_obj.nivel_usuario >= 10:
        clase_nombre = request.form.get("clase")
        if clase_nombre:
            usuario_obj.clase = Clase.cargar_clase(clase_nombre, usuario_obj.rol == "vip")

    gestor.actualizar_usuario(usuario_obj)
    flash("Perfil actualizado exitosamente", "success")
    return redirect(url_for("dashboard"))

@app.route("/editar_credenciales", methods=["POST"])
def editar_credenciales_route():
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])
    usuario_obj.editar_credenciales(request.form)

    flash("Credenciales actualizadas exitosamente", "success")
    return redirect(url_for("dashboard"))

@app.route("/eliminar_usuario", methods=["POST"])
def eliminar_usuario():
    nombre_usuario = request.form["usuario"]
    password = request.form["contraseña"]

    usuario_obj = gestor.eliminar_usuario_web(nombre_usuario)
    if usuario_obj and check_password_hash(usuario_obj.contraseña, password):
        gestor_tareas.eliminar_tareas_de_usuario(usuario_obj.id_usuario)
        gestor_inventario.eliminar_inventario_de_usuario(usuario_obj.id_usuario)
        gestor.usuarios.remove(usuario_obj)
        gestor.guardar_usuarios()
        session.clear()
        flash("Cuenta eliminada exitosamente. Este proceso es irreversible.", "success")
        return redirect(url_for("home"))
    else:
        flash("Credenciales inválidas. No se pudo eliminar la cuenta.", "error")
        return redirect(url_for("dashboard"))

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

    ids_completadas = request.form.getlist("tareas_completadas[]")

    total_recompensas = {"xp": 0, "coins": 0, "mana": 0, "vida": 0}
    total_penalizaciones = {"vida": 0, "xp": 0, "coins": 0}

    # 🔹 Dos formatos distintos según tipo de tarea
    hoy_diaria = datetime.date.today().strftime("%d-%m-%Y")  # para diarias
    hoy_pendiente = datetime.date.today() # para pendientes

    # Procesar diarias vencidas
    for d in diarias_vencidas:
        if str(d.id) in ids_completadas:
            resultado = gestor_tareas.marcar_tarea_web(
                tarea_id=d.id,
                accion="completar",
                retroactivo=True,
                por_medianoche=False
            )
            for r in resultado["recompensas"]:
                tipo = r["tipo"]
                total_recompensas[tipo] += r["resultado"]["total"]
        else:
            resultado = gestor_tareas.marcar_tarea_web(
                tarea_id=d.id,
                accion="incompleta",
                retroactivo=False,
                por_medianoche=True
            )
            for p in resultado["penalizaciones"]:
                tipo = p["tipo"]
                total_penalizaciones[tipo] += p["resultado"]["total"]

        d.fecha_creacion = hoy_diaria
        d.completada = False
        gestor_tareas.actualizar_tarea(d)

    # Procesar pendientes vencidas
    for p in pendientes_vencidas:
        if str(p.id) in ids_completadas:
            resultado = gestor_tareas.marcar_tarea_web(
                tarea_id=p.id,
                accion="completar",
                retroactivo=True,
                por_medianoche=False
            )
            for r in resultado["recompensas"]:
                tipo = r["tipo"]
                total_recompensas[tipo] += r["resultado"]["total"]

            p.completada = True

            # 👇 Comparar fechas en formato ISO
            fecha_venc = datetime.date.fromisoformat(p.fecha_vencimiento)
            if fecha_venc <= hoy_pendiente:
                p.fecha_vencimiento = hoy_pendiente.strftime("%Y-%m-%d")

        else:
            resultado = gestor_tareas.marcar_tarea_web(
                tarea_id=p.id,
                accion="incompleta",
                retroactivo=False,
                por_medianoche=False
            )
            for pz in resultado["penalizaciones"]:
                tipo = pz["tipo"]
                total_penalizaciones[tipo] += pz["resultado"]["total"]
            p.completada = False

        gestor_tareas.actualizar_tarea(p)

    # ✅ Toast resumen recompensas
    if any(v != 0 for v in total_recompensas.values()):
        flash(
            f"Completaste {len(ids_completadas)} tareas retroactivamente: "
            f"+{total_recompensas['xp']} XP, "
            f"+{total_recompensas['coins']} COINS, "
            f"+{total_recompensas['mana']} MANÁ.",
            "xp"
        )

    # ✅ Toast resumen penalizaciones
    total_falladas = (len(diarias_vencidas) + len(pendientes_vencidas)) - len(ids_completadas)
    if total_falladas > 0:
        flash(
            f"No completaste {total_falladas} tareas: "
            f"{abs(total_penalizaciones['vida'])} HP, "
            f"{abs(total_penalizaciones['xp'])} XP, "
            f"{abs(total_penalizaciones['coins'])} COINS.",
            "vida"
        )

    session["mostrar_modal"] = False
    session["ultimo_procesado"] = hoy_diaria  # mantener coherencia con diarias

    gestor.actualizar_usuario(usuario_obj)
    return ("", 204)

@app.route("/simular_nuevo_dia")
def simular_nuevo_dia():
    session["ultimo_procesado"] = "28-04-2026"  # cualquier fecha distinta de hoy
    session["mostrar_modal"] = True
    return "Simulación de nuevo día aplicada."

@app.route("/editar_tarea/<int:tarea_id>", methods=["POST"])
def editar_tarea(tarea_id):
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])
    gestor_tareas = GestorTareas(usuario=usuario_obj, gestor_usuarios=gestor)

    nuevo_titulo = request.form.get("titulo")
    nueva_fecha = request.form.get("fecha_vencimiento")
    nuevos_dias = request.form.getlist("dias")
    nuevo_habito = request.form.get("habito")

    exito = gestor_tareas.editar_tarea(tarea_id, nuevo_titulo, nueva_fecha, nuevos_dias, nuevo_habito)
    if exito:
        flash("Tarea actualizada exitosamente.", "success")
    else:
        flash("No se encontró la tarea.", "error")
    return redirect(url_for("dashboard"))

@app.route("/eliminar_tarea/<int:tarea_id>", methods=["POST"])
def eliminar_tarea(tarea_id):
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])
    gestor_tareas = GestorTareas(usuario=usuario_obj, gestor_usuarios=gestor)

    gestor_tareas.eliminar_tarea(tarea_id)
    flash("Tarea eliminada.", "success")
    return redirect(url_for("dashboard"))

@app.context_processor
def inject_perfil():
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return {}  # no hay usuario en sesión, no se inyecta nada

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])
    perfil_data = usuario_obj.ver_perfil_web()

    # Esto hace que 'perfil' y 'usuario' estén disponibles en todas las plantillas
    return dict(usuario=usuario_obj, perfil=perfil_data)

if __name__ == "__main__":
    app.run(debug=True)

