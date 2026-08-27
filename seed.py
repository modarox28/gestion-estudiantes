"""Carga datos de ejemplo en la base de datos.

Uso:
    python seed.py
"""
import random

from app import app
import db

NOMBRES = [
    "Ana", "Luis", "María", "Carlos", "Sofía", "Diego", "Valentina", "José",
    "Camila", "Andrés", "Lucía", "Miguel", "Isabella", "Javier", "Gabriela",
    "Daniel", "Paula", "Sebastián", "Antonella", "Fernando",
]
APELLIDOS = [
    "González", "Rodríguez", "Pérez", "Martínez", "López", "Sánchez", "Ramírez",
    "Torres", "Flores", "Rivera", "Gómez", "Díaz", "Vargas", "Castro", "Romero",
]
SECCIONES = ["A", "B"]
# Edad típica aproximada por grado.
EDAD_BASE = {"6to": 11, "7mo": 12, "8vo": 13, "9no": 14, "10mo": 15, "11mo": 16}


def main():
    with app.app_context():
        db.init_db()
        con = db.get_db()
        total = 0
        for grado in db.GRADOS:
            for seccion in SECCIONES:
                for _ in range(random.randint(6, 10)):
                    nombre = random.choice(NOMBRES)
                    apellido = f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
                    edad = EDAD_BASE[grado] + random.choice([-1, 0, 0, 1])
                    con.execute(
                        "INSERT INTO estudiantes (nombre, apellido, edad, grado, seccion)"
                        " VALUES (?, ?, ?, ?, ?)",
                        (nombre, apellido, edad, grado, seccion),
                    )
                    total += 1
        con.commit()
        print(f"{total} estudiantes de ejemplo insertados.")


if __name__ == "__main__":
    main()
