"""Utilidades de acceso a la base de datos SQLite."""
import sqlite3
from pathlib import Path

from flask import current_app, g

# Grados disponibles (6 grados: de 6to a 11mo) y orden lógico para ordenar.
GRADOS = ["6to", "7mo", "8vo", "9no", "10mo", "11mo"]
GRADO_ORDEN = {g: i for i, g in enumerate(GRADOS)}


def get_db():
    """Devuelve una conexión SQLite reutilizable por petición."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Crea las tablas a partir de schema.sql."""
    db = get_db()
    schema = Path(current_app.root_path) / "schema.sql"
    db.executescript(schema.read_text(encoding="utf-8"))
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)


# ---------------------------------------------------------------------------
# Consultas
# ---------------------------------------------------------------------------

# Mapa de criterios de ordenación -> cláusula ORDER BY segura (whitelist).
ORDENES = {
    "alfabetico": "apellido COLLATE NOCASE, nombre COLLATE NOCASE",
    "edad": "edad ASC, apellido COLLATE NOCASE",
    "edad_desc": "edad DESC, apellido COLLATE NOCASE",
    "grado": "orden_grado ASC, seccion COLLATE NOCASE, apellido COLLATE NOCASE",
}

# Expresión CASE para traducir el texto del grado a un número ordenable.
_ORDEN_GRADO_SQL = "CASE grado " + " ".join(
    f"WHEN '{g}' THEN {i}" for i, g in enumerate(GRADOS)
) + " ELSE 99 END"


def listar_estudiantes(orden="alfabetico", grado=None, seccion=None, buscar=None):
    if orden not in ORDENES:
        orden = "alfabetico"

    sql = f"SELECT *, {_ORDEN_GRADO_SQL} AS orden_grado FROM estudiantes WHERE 1=1"
    params = []

    if grado:
        sql += " AND grado = ?"
        params.append(grado)
    if seccion:
        sql += " AND seccion = ?"
        params.append(seccion)
    if buscar:
        sql += " AND (nombre LIKE ? OR apellido LIKE ?)"
        like = f"%{buscar}%"
        params.extend([like, like])

    sql += f" ORDER BY {ORDENES[orden]}"
    return get_db().execute(sql, params).fetchall()


def obtener_estudiante(est_id):
    return get_db().execute(
        "SELECT * FROM estudiantes WHERE id = ?", (est_id,)
    ).fetchone()


def crear_estudiante(nombre, apellido, edad, grado, seccion):
    db = get_db()
    db.execute(
        "INSERT INTO estudiantes (nombre, apellido, edad, grado, seccion) "
        "VALUES (?, ?, ?, ?, ?)",
        (nombre, apellido, edad, grado, seccion),
    )
    db.commit()


def actualizar_estudiante(est_id, nombre, apellido, edad, grado, seccion):
    db = get_db()
    db.execute(
        "UPDATE estudiantes SET nombre = ?, apellido = ?, edad = ?, "
        "grado = ?, seccion = ? WHERE id = ?",
        (nombre, apellido, edad, grado, seccion, est_id),
    )
    db.commit()


def borrar_estudiante(est_id):
    db = get_db()
    db.execute("DELETE FROM estudiantes WHERE id = ?", (est_id,))
    db.commit()


def secciones_existentes():
    filas = get_db().execute(
        "SELECT DISTINCT seccion FROM estudiantes ORDER BY seccion"
    ).fetchall()
    return [f["seccion"] for f in filas]


def resumen_por_grado():
    """Cuenta de estudiantes y edad promedio por grado y sección."""
    return get_db().execute(
        f"""
        SELECT grado, seccion, COUNT(*) AS total,
               ROUND(AVG(edad), 1) AS edad_promedio
        FROM estudiantes
        GROUP BY grado, seccion
        ORDER BY {_ORDEN_GRADO_SQL}, seccion
        """
    ).fetchall()
