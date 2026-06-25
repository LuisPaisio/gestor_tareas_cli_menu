import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from gestor_usuarios import GestorUsuarios
from gestor_tareas import GestorTareas
from gestor_recompensa import GestorRecompensas
from constantes_tareas import vida_maxima, mana_maximo
from gestor_notificaciones import GestorNotificaciones
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from inventario import Inventario
import re
from gestor_inventario import GestorInventario
from tienda import Tienda
from gestor_mascotas import GestorMascotas
from dotenv import load_dotenv
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24).hex())
app.permanent_session_lifetime = datetime.timedelta(days=30)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB límite para subidas
gestor = GestorUsuarios()
tienda = Tienda()

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
            "foto_perfil": usuario_actual.foto_perfil,
            "foto_personaje": usuario_actual.foto_personaje
        }

        session.permanent = bool(mantener_sesion)
        return redirect(url_for("dashboard"))  # directo al dashboard
    else:
        return render_template("home.html", error="Usuario o contraseña incorrectos")

@app.route("/register", methods=["POST"])
def register():
    nombre_usuario = request.form["username"].strip()
    password = request.form["password"].strip()
    mantener_sesion = request.form.get("mantener-sesion")
    acepto_terminos = request.form.get("acepto-terminos")  # 🔹 Nuevo

    # Detectar template según origen
    template = "soloregister.html" if "register_page" in (request.referrer or "") else "home.html"

    # Validación de términos y condiciones
    if not acepto_terminos:
        flash("Debes aceptar los términos y condiciones para completar el registro.", "error")
        return redirect(request.referrer or url_for("home"))

    # Validaciones de usuario primero
    if len(nombre_usuario) < 8:
        flash("El nombre de usuario debe tener al menos 8 caracteres.", "error")
        return redirect(request.referrer or url_for("home"))
    for usuario in gestor.usuarios:
        if usuario.usuario == nombre_usuario:
            flash("El nombre de usuario ya existe. Por favor elige otro.", "error")
            return redirect(request.referrer or url_for("home"))

    # Validaciones de contraseña después
    if len(password) < 8:
        flash("La contraseña debe tener al menos 8 caracteres.", "error")
        return redirect(request.referrer or url_for("home"))
    if not re.search(r"[A-Z]", password):
        flash("La contraseña debe incluir al menos una letra mayúscula.", "error")
        return redirect(request.referrer or url_for("home"))
    if not re.search(r"[0-9]", password):
        flash("La contraseña debe incluir al menos un número.", "error")
        return redirect(request.referrer or url_for("home"))
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        flash("La contraseña debe incluir al menos un símbolo especial.", "error")
        return redirect(request.referrer or url_for("home"))

    # Generar el hash de la contraseña después de validar
    password_hash = generate_password_hash(password)

    usuario_actual = gestor.register_web(nombre_usuario, password_hash)
    if usuario_actual:
        session["usuario"] = {
            "id_usuario": usuario_actual.id_usuario,
            "nombre": usuario_actual.usuario,
            "usuario": usuario_actual.nombre_publico if usuario_actual.nombre_publico else usuario_actual.usuario,
            "nivel": usuario_actual.nivel_usuario,
            "clase_nombre": usuario_actual.clase_nombre,
            "foto_perfil": usuario_actual.foto_perfil,
            "foto_personaje": usuario_actual.foto_personaje
        }

        session.permanent = bool(mantener_sesion)
        return redirect(url_for("setup_profile"))
    else:
        flash("No se pudo registrar", "error")
        return redirect(request.referrer or url_for("home"))

@app.route("/setup_profile", methods=["GET", "POST"])
def setup_profile():
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])

    if request.method == "POST":
        nombre_publico = request.form["nombre_publico"].strip()
        personaje = request.form["personaje"]

        # Validaciones...
        usuario_obj.nombre_publico = nombre_publico
        usuario_obj.foto_personaje = f"/static/images/{personaje}.png"
        gestor.guardar_usuarios()

        session["usuario"]["usuario"] = nombre_publico
        session["usuario"]["foto_personaje"] = usuario_obj.foto_personaje

        return redirect(url_for("dashboard"))

    return render_template("setup_profile.html", **contexto_comun(usuario_obj))

@app.route("/logout")
def logout():
    session.clear()  # limpia toda la sesión, no solo el usuario
    flash("Sesión cerrada correctamente", "warning")  # mensaje para el usuario
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

    # Resetear tareas diarias completadas de días anteriores
    hoy_ddmm = datetime.date.today().strftime("%d-%m-%Y")
    for tarea in gestor_tareas.tareas:
        if tarea.tipo == 2 and int(tarea.id_usuario) == usuario_obj.id_usuario:
            if tarea.completada and tarea.fecha_creacion != hoy_ddmm:
                tarea.completada = False
                tarea.fecha_creacion = hoy_ddmm
                gestor_tareas.actualizar_tarea(tarea)

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


@app.route("/equipos")
def equipos():
    usuario = session.get("usuario")
    if not usuario:
        return redirect(url_for("home"))
    return render_template("equipos.html", usuario=usuario)

@app.route("/ayuda")
def ayuda():
    usuario = session.get("usuario")
    if not usuario:
        return redirect(url_for("home"))
    return render_template("ayuda.html", usuario=usuario)

@app.route("/inventario")
def ver_inventario():
    if "usuario" not in session:
        flash("Debes iniciar sesión para ver tu inventario.", "error")
        return redirect(url_for("login"))

    id_usuario = session["usuario"]["id_usuario"]
    usuario_obj = gestor.get_usuario_por_id(id_usuario)

    gestor_inv = GestorInventario(usuario_obj)
    inventario = gestor_inv.inventario_usuario()
    items = inventario.mostrar_web()
    tiene_pocion = gestor_inv.tiene_item("Poción de Eclosión")

    return render_template(
        "inventario.html",
        items=items,
        tiene_pocion=tiene_pocion,
        **contexto_comun(usuario_obj)   # ahora ya incluye notificaciones
    )

@app.route("/inventario/equipar/<int:id_item>", methods=["POST"])
def equipar_item(id_item):
    if "usuario" not in session:
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for("login"))

    usuario_obj = gestor.get_usuario_por_id(session["usuario"]["id_usuario"])
    resultado = usuario_obj.equipar(id_item)

    if "error" in resultado:
        flash(resultado["error"], "error")
    else:
        flash(resultado["success"], resultado.get("categoria", "success"))

    return redirect(url_for("ver_inventario"))


@app.route("/inventario/desequipar/<slot>", methods=["POST"])
def desequipar_item(slot):
    if "usuario" not in session:
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for("login"))

    usuario_obj = gestor.get_usuario_por_id(session["usuario"]["id_usuario"])
    resultado = usuario_obj.desequipar(slot)

    if "error" in resultado:
        flash(resultado["error"], "error")
    else:
        flash(resultado["success"], resultado.get("categoria", "success"))

    return redirect(url_for("ver_inventario"))


@app.route("/inventario/usar/<int:id_item>", methods=["POST"])
def usar_item(id_item):
    if "usuario" not in session:
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for("login"))

    usuario_obj = gestor.get_usuario_por_id(session["usuario"]["id_usuario"])
    resultado = usuario_obj.usar_item(id_item)

    if "error" in resultado:
        flash(resultado["error"], "error")
    else:
        flash(resultado["success"], "success")

    return redirect(url_for("ver_inventario"))

@app.route("/inventario/eclosionar", methods=["POST"])
def eclosionar_huevo():
    if "usuario" not in session:
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for("login"))

    id_usuario = session["usuario"]["id_usuario"]
    usuario_obj = gestor.get_usuario_por_id(id_usuario)

    gestor_inv = GestorInventario(usuario_obj)
    gestor_mascotas = GestorMascotas(usuario_obj.id_usuario, gestor_inv)

    if not gestor_inv.tiene_item("Huevo Básico"):
        flash("No tienes huevos disponibles.", "error")
        return redirect(url_for("ver_inventario"))

    if not gestor_inv.tiene_item("Poción de Eclosión"):
        flash("Necesitas una poción de eclosión.", "error")
        return redirect(url_for("ver_inventario"))

    gestor_inv.consumir_item("Huevo Básico", 1)
    gestor_inv.consumir_item("Poción de Eclosión", 1)

    es_vip = usuario_obj.rol == "vip"
    success, mensaje = gestor_mascotas.agregar_mascota_aleatoria(es_vip=es_vip)
    flash(mensaje, "success" if success else "error")

    return redirect(url_for("ver_inventario"))


@app.route("/mascotas")
def menu_mascotas():
    if "usuario" not in session:
        flash("Debes iniciar sesión para ver tus mascotas.", "error")
        return redirect(url_for("login"))

    id_usuario = session["usuario"]["id_usuario"]
    usuario_obj = gestor.get_usuario_por_id(id_usuario)

    gestor_inv = GestorInventario(usuario_obj)
    gestor_mascotas = GestorMascotas(usuario_obj.id_usuario, gestor_inv)
    mascotas = gestor_mascotas.listar_mascotas_web()

    # 🔹 Flags de inventario (usar nombres exactos del catálogo)
    tiene_alimento = gestor_inv.tiene_item("Alimento Básico")
    tiene_pocion_eclosion = gestor_inv.tiene_item("Poción de Eclosión")

    return render_template(
        "mascotas.html",
        mascotas=mascotas,
        tiene_alimento=tiene_alimento,
        tiene_pocion_eclosion=tiene_pocion_eclosion,
        **contexto_comun(usuario_obj)
    )

@app.route("/mascotas/alimentar/<int:id_mascota>", methods=["POST"])
def alimentar_mascota(id_mascota):
    if "usuario" not in session:
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for("login"))

    id_usuario = session["usuario"]["id_usuario"]
    usuario_obj = gestor.get_usuario_por_id(id_usuario)

    gestor_inv = GestorInventario(usuario_obj)
    gestor_mascotas = GestorMascotas(usuario_obj.id_usuario, gestor_inv)

    success, mensaje = gestor_mascotas.alimentar_mascota(id_mascota)
    flash(mensaje, "success" if success else "error")

    return redirect(url_for("menu_mascotas"))

@app.route("/tienda")
def mostrar_tienda():
    if "usuario" not in session:
        flash("Debes iniciar sesión para ver la tienda.", "error")
        return redirect(url_for("login"))

    id_usuario = session["usuario"]["id_usuario"]
    usuario_obj = gestor.get_usuario_por_id(id_usuario)

    # Parámetros de paginación
    pagina_catalogo = int(request.args.get("pagina_catalogo", 1))
    pagina_inventario = int(request.args.get("pagina_inventario", 1))
    items_por_pagina = 56

    # Catálogo
    todos_items = tienda.mostrar_items()
    total_paginas_catalogo = (len(todos_items) + items_por_pagina - 1) // items_por_pagina
    inicio_cat = (pagina_catalogo - 1) * items_por_pagina
    fin_cat = inicio_cat + items_por_pagina
    items_paginados = todos_items[inicio_cat:fin_cat]

    # Inventario del usuario
    inventario_completo = usuario_obj.gestor_inventario.inventario_usuario()
    inventario_items = list(inventario_completo.items.items())
    total_paginas_inventario = (len(inventario_items) + items_por_pagina - 1) // items_por_pagina
    inicio_inv = (pagina_inventario - 1) * items_por_pagina
    fin_inv = inicio_inv + items_por_pagina
    inventario_paginados = dict(inventario_items[inicio_inv:fin_inv])

    return render_template(
        "tienda.html",
        items=items_paginados,
        inventario=inventario_paginados,
        tienda=tienda,
        pagina_catalogo=pagina_catalogo,
        total_paginas_catalogo=total_paginas_catalogo,
        pagina_inventario=pagina_inventario,
        total_paginas_inventario=total_paginas_inventario,
        **contexto_comun(usuario_obj)   # igual que en inventario
    )

@app.route("/tienda/comprar/<int:id_item>", methods=["POST"])
def comprar_item(id_item):
    if "usuario" not in session:
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for("login"))

    usuario_obj = gestor.get_usuario_por_id(session["usuario"]["id_usuario"])
    cantidad = int(request.form.get("cantidad", 1))

    # ✅ pasar id_item, no objeto
    resultado = tienda.comprar_item(usuario_obj, gestor, id_item, cantidad)

    if isinstance(resultado, dict):
        if "error" in resultado:
            flash(resultado["error"], "error")
        else:
            flash(resultado["success"], "success")
    else:
        flash(resultado, "info")

    return redirect(url_for("mostrar_tienda"))

@app.route("/tienda/vender/<int:id_item>", methods=["POST"])
def vender_item(id_item):
    if "usuario" not in session:
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for("login"))

    usuario_obj = gestor.get_usuario_por_id(session["usuario"]["id_usuario"])
    cantidad = int(request.form.get("cantidad", 1))

    # ✅ pasar id_item, no objeto
    resultado = tienda.vender_item(usuario_obj, gestor, id_item, cantidad)

    if isinstance(resultado, dict):
        if "error" in resultado:
            flash(resultado["error"], "error")
        else:
            flash(resultado["success"], "success")
    else:
        flash(resultado, "info")

    return redirect(url_for("mostrar_tienda"))

@app.route("/perfil")
def perfil():
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])
    perfil_data = usuario_obj.ver_perfil_web()

    return render_template("perfil.html", perfil=perfil_data)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/editar_perfil", methods=["POST"])
def editar_perfil():
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])

    # Nombre y descripción
    usuario_obj.nombre_publico = request.form.get("nombre_publico", usuario_obj.nombre_publico).strip() or usuario_obj.nombre_publico
    usuario_obj.descripcion = request.form.get("descripcion", usuario_obj.descripcion).strip() or usuario_obj.descripcion

    # Foto de perfil → subida de archivo seguro
    archivo = request.files.get("foto_perfil")
    if archivo and archivo.filename:
        ext = os.path.splitext(archivo.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            flash("Formato de imagen no permitido. Usá JPG, PNG o WebP.", "error")
            return redirect(url_for("dashboard"))

        # Validar el contenido real del archivo (magic bytes)
        archivo.seek(0)
        cabecera = archivo.read(8)
        archivo.seek(0)
        es_imagen = (
            cabecera.startswith(b"\xff\xd8\xff")          # JPEG
            or cabecera.startswith(b"\x89PNG\r\n\x1a\n") # PNG
            or cabecera.startswith(b"RIFF")               # WEBP (RIFF....WEBP)
        )
        if ext == ".webp" and not cabecera.startswith(b"RIFF"):
            flash("El archivo no es un WebP válido.", "error")
            return redirect(url_for("dashboard"))
        if not es_imagen:
            flash("El archivo no parece ser una imagen válida.", "error")
            return redirect(url_for("dashboard"))

        nombre_unico = f"{uuid.uuid4().hex}{ext}"
        ruta_guardado = os.path.join(UPLOAD_FOLDER, nombre_unico)
        archivo.save(ruta_guardado)
        usuario_obj.foto_perfil = url_for("static", filename=f"uploads/{nombre_unico}")

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
    try:
        usuario_obj.editar_credenciales(request.form)
        flash("Credenciales actualizadas exitosamente", "success")
    except ValueError as e:
        flash(str(e), "error")

    return redirect(request.referrer or url_for("dashboard"))

@app.route("/eliminar_usuario", methods=["POST"])
def eliminar_usuario():
    nombre_usuario = request.form["usuario"]
    password = request.form["contraseña"]

    usuario_obj = gestor.eliminar_usuario_web(nombre_usuario)
    if usuario_obj and check_password_hash(usuario_obj.contraseña, password):
        # Crear gestor de tareas e inventario en este contexto
        gestor_tareas = GestorTareas(usuario_obj)
        gestor_inventario = GestorInventario(usuario_obj)

        gestor_tareas.eliminar_tareas_de_usuario(usuario_obj.id_usuario)
        gestor_inventario.eliminar_inventario_de_usuario(usuario_obj.id_usuario)
        gestor.usuarios.remove(usuario_obj)
        gestor.guardar_usuarios()
        session.clear()
        flash("Cuenta eliminada exitosamente. Este proceso es irreversible.", "success")
        return redirect(url_for("home"))
    else:
        flash("Credenciales inválidas. No se pudo eliminar la cuenta.", "error")
        return redirect(request.referrer or url_for("dashboard"))

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

    retroactivo = request.form.get("retroactivo") == "true"
    por_medianoche = request.form.get("por_medianoche") == "true"

    resultado = gestor_tareas.marcar_tarea_web(
        tarea_id, accion,
        retroactivo=retroactivo,
        por_medianoche=por_medianoche
    )

    if "error" in resultado:
        flash(resultado["error"], "error")
    else:
        flash(resultado["mensaje"], "info")

        for r in resultado.get("recompensas", []):
            if r["tipo"] in ("aleatorio", "item"):
                flash(f"{r['nombre']} +{r['resultado']['total']}", "item")
            else:
                flash(f"{r['tipo'].upper()} +{r['resultado']['total']}", r["tipo"])

        for p in resultado.get("penalizaciones", []):
            flash(p.get("mensaje", f"{p['tipo'].upper()} {p['resultado']['total']}"), f"{p['tipo']}-neg")

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

@app.route("/usar_poder/<nombre_poder>", methods=["POST"])
def usar_poder(nombre_poder):
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])

    success, mensajes = usuario_obj.usar_poder(nombre_poder)
    for m in mensajes:
        flash(m, "success" if success else "error")

    gestor.actualizar_usuario(usuario_obj)
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
    # Redirige a la página desde la que vino la petición
    return redirect(request.referrer or url_for("dashboard"))


@app.route("/notificacion/<int:id_notificacion>/eliminar", methods=["POST", "GET"])
def eliminar_notificacion(id_notificacion):
    usuario_dict = session.get("usuario")
    if not usuario_dict:
        return redirect(url_for("home"))

    usuario_obj = gestor.get_usuario_por_id(usuario_dict["id_usuario"])
    gestor_notificaciones = GestorNotificaciones()
    gestor_notificaciones.eliminar_notificacion(usuario_obj.id_usuario, str(id_notificacion))

    flash("Notificación eliminada", "success")
    # Redirige a la página desde la que vino la petición
    return redirect(request.referrer or url_for("dashboard"))

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

    hoy_diaria = datetime.date.today().strftime("%d-%m-%Y")
    hoy_pendiente = datetime.date.today()

    # Procesar diarias vencidas
    for d in diarias_vencidas:
        if str(d.id) in ids_completadas:
            resultado = gestor_tareas.marcar_tarea_web(
                tarea_id=d.id,
                accion="completar",
                retroactivo=True,
                por_medianoche=False
            )
            for r in resultado.get("recompensas", []):
                if r["tipo"] in total_recompensas:
                    total_recompensas[r["tipo"]] += r["resultado"]["total"]
                elif r["tipo"] in ["aleatorio", "item"]:
                    flash(f"{r['nombre']} +{r['resultado']['total']}", "item")
                else:
                    flash(f"{r['tipo'].upper()} +{r['resultado']['total']}", r["tipo"])
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
            for r in resultado.get("recompensas", []):
                if r["tipo"] in total_recompensas:
                    total_recompensas[r["tipo"]] += r["resultado"]["total"]
                elif r["tipo"] in ["aleatorio", "item"]:
                    flash(f"{r['nombre']} +{r['resultado']['total']}", "item")
                else:
                    flash(f"{r['tipo'].upper()} +{r['resultado']['total']}", r["tipo"])

            p.completada = True
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
    session["ultimo_procesado"] = hoy_diaria

    gestor.actualizar_usuario(usuario_obj)
    return ("", 204)

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

def contexto_comun(usuario_obj, pagina_actual=1, total_paginas=1):
    gestor_notificaciones = GestorNotificaciones()
    notificaciones_lista = gestor_notificaciones.obtener_notificaciones(usuario_obj.id_usuario)[:5]

    return {
        "usuario": usuario_obj,
        "vida_maxima": vida_maxima(),
        "mana_maximo": mana_maximo(),
        "xp_requerida": usuario_obj.xp_requerida(),
        "pagina_actual": pagina_actual,
        "total_paginas": total_paginas,
        "notificaciones": notificaciones_lista
    }

@app.before_request
def verificar_perfil_completo():
    # Rutas que no deben ser bloqueadas
    rutas_libres = {"setup_profile", "register", "login", "home", "logout", "static"}

    if "usuario" in session:
        usuario_obj = gestor.get_usuario_por_id(session["usuario"]["id_usuario"])
        if usuario_obj and (not usuario_obj.foto_personaje or not usuario_obj.nombre_publico):
            # Si intenta entrar a otra ruta que no sea setup_profile, lo redirigimos
            if request.endpoint not in rutas_libres:
                flash("Debes completar tu perfil para comenzar a usar Progresia.", "error")
                return redirect(url_for("setup_profile"))

if __name__ == "__main__":
    es_desarrollo = os.environ.get("FLASK_ENV") == "development"
    app.run(debug=es_desarrollo, host="127.0.0.1")

