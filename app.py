"""Aplicación web de gestión de estudiantes (Flask + SQLite)."""
import hmac
import os
from functools import wraps

from flask import (
    Flask, flash, redirect, render_template, request, session, url_for
)

import db
from db import GRADOS


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-cambia-esto"),
        DATABASE=os.environ.get(
            "DATABASE", os.path.join(app.instance_path, "estudiantes.db")
        ),
        # Credenciales del administrador (cámbialas con variables de entorno).
        ADMIN_USUARIO=os.environ.get("ADMIN_USUARIO", "admin"),
        ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD", "admin123"),
    )
    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    # ---- Autenticación de administrador ------------------------------------
    def es_admin():
        return session.get("admin") is True

    def login_required(vista):
        @wraps(vista)
        def envoltura(*args, **kwargs):
            if not es_admin():
                flash("Inicia sesión como administrador para hacer eso.", "error")
                return redirect(url_for("login", next=request.path))
            return vista(*args, **kwargs)
        return envoltura

    @app.context_processor
    def inyectar_admin():
        return {"es_admin": es_admin()}

    # Crea la BD automáticamente si no existe.
    with app.app_context():
        if not os.path.exists(app.config["DATABASE"]):
            db.init_db()

    @app.cli.command("init-db")
    def init_db_command():
        """Reinicia la base de datos (borra todos los datos)."""
        db.init_db()
        print("Base de datos inicializada.")

    # -------------------------------------------------------------------
    # Rutas
    # -------------------------------------------------------------------
    @app.route("/")
    def index():
        orden = request.args.get("orden", "alfabetico")
        grado = request.args.get("grado") or None
        seccion = request.args.get("seccion") or None
        buscar = request.args.get("buscar", "").strip() or None

        estudiantes = db.listar_estudiantes(orden, grado, seccion, buscar)
        return render_template(
            "index.html",
            estudiantes=estudiantes,
            orden=orden,
            grado=grado or "",
            seccion=seccion or "",
            buscar=buscar or "",
            grados=GRADOS,
            secciones=db.secciones_existentes(),
        )

    @app.route("/resumen")
    def resumen():
        return render_template("resumen.html", filas=db.resumen_por_grado())

    @app.route("/login", methods=["GET", "POST"])
    def login():
        destino = request.args.get("next") or url_for("index")
        if es_admin():
            return redirect(destino)
        if request.method == "POST":
            usuario = request.form.get("usuario", "")
            password = request.form.get("password", "")
            ok_u = hmac.compare_digest(usuario, app.config["ADMIN_USUARIO"])
            ok_p = hmac.compare_digest(password, app.config["ADMIN_PASSWORD"])
            if ok_u and ok_p:
                session["admin"] = True
                flash("Sesión iniciada como administrador.", "ok")
                return redirect(destino)
            flash("Usuario o contraseña incorrectos.", "error")
        return render_template("login.html")

    @app.route("/logout", methods=["POST"])
    def logout():
        session.pop("admin", None)
        flash("Sesión cerrada.", "ok")
        return redirect(url_for("index"))

    @app.route("/nuevo", methods=["GET", "POST"])
    @login_required
    def nuevo():
        if request.method == "POST":
            datos, error = _leer_formulario(request.form)
            if error:
                flash(error, "error")
            else:
                db.crear_estudiante(**datos)
                flash("Estudiante agregado correctamente.", "ok")
                return redirect(url_for("index"))
        return render_template(
            "form.html", accion="Nuevo estudiante", estudiante=None, grados=GRADOS
        )

    @app.route("/editar/<int:est_id>", methods=["GET", "POST"])
    @login_required
    def editar(est_id):
        estudiante = db.obtener_estudiante(est_id)
        if estudiante is None:
            flash("Ese estudiante no existe.", "error")
            return redirect(url_for("index"))

        if request.method == "POST":
            datos, error = _leer_formulario(request.form)
            if error:
                flash(error, "error")
            else:
                db.actualizar_estudiante(est_id, **datos)
                flash("Cambios guardados.", "ok")
                return redirect(url_for("index"))
        return render_template(
            "form.html", accion="Editar estudiante",
            estudiante=estudiante, grados=GRADOS
        )

    @app.route("/borrar/<int:est_id>", methods=["POST"])
    @login_required
    def borrar(est_id):
        db.borrar_estudiante(est_id)
        flash("Estudiante eliminado.", "ok")
        return redirect(url_for("index"))

    return app


def _leer_formulario(form):
    """Valida y normaliza los datos del formulario. Devuelve (datos, error)."""
    nombre = form.get("nombre", "").strip()
    apellido = form.get("apellido", "").strip()
    edad_raw = form.get("edad", "").strip()
    grado = form.get("grado", "").strip()
    seccion = form.get("seccion", "").strip().upper()

    if not nombre or not apellido:
        return None, "El nombre y el apellido son obligatorios."
    try:
        edad = int(edad_raw)
    except ValueError:
        return None, "La edad debe ser un número entero."
    if not (1 <= edad <= 99):
        return None, "La edad debe estar entre 1 y 99."
    if grado not in GRADOS:
        return None, "Selecciona un grado válido."
    if not seccion or len(seccion) > 3:
        return None, "La sección es obligatoria (ej: A, B, C)."

    return {
        "nombre": nombre,
        "apellido": apellido,
        "edad": edad,
        "grado": grado,
        "seccion": seccion,
    }, None


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
