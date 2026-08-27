# 🎓 Gestión de Estudiantes

Aplicación web para **registrar estudiantes** y **consultarlos ordenados por edad,
orden alfabético o grado**. Incluye base de datos (SQLite), CRUD completo y un
resumen por grado/sección.

Los grados van de **6to a 11mo** (6 grados) y cada grado admite varias secciones
(`7mo A`, `7mo B`, …).

## Características

- Alta, edición y borrado de estudiantes (nombre, apellido, edad, grado, sección).
- Listado con **ordenación** por:
  - Orden alfabético (apellido, nombre)
  - Edad (ascendente o descendente)
  - Grado y sección
- Filtros por grado y sección + búsqueda por nombre/apellido.
- Página de **resumen**: total de estudiantes y edad promedio por grado y sección.
- **Login de administrador**: agregar, editar y borrar requiere sesión. Cualquiera
  puede consultar y ordenar el listado; solo el admin modifica datos.
- Base de datos SQLite creada automáticamente al arrancar.

## Acceso de administrador

Credenciales por defecto (¡cámbialas en producción!):

| Usuario | Contraseña |
|---------|------------|
| `admin` | `admin123` |

Para cambiarlas, define variables de entorno antes de arrancar:

```bash
export ADMIN_USUARIO="miusuario"
export ADMIN_PASSWORD="una-clave-larga"
export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
flask --app app run
```

## Stack

- Python 3 · Flask
- SQLite (módulo `sqlite3` de la librería estándar)
- HTML + CSS (plantillas Jinja2, sin frameworks front-end)

## Instalación y uso

```bash
# 1. Clonar
git clone https://github.com/<tu-usuario>/gestion-estudiantes.git
cd gestion-estudiantes

# 2. Entorno virtual (opcional pero recomendado)
python3 -m venv .venv
source .venv/bin/activate

# 3. Dependencias
pip install -r requirements.txt

# 4. (Opcional) cargar datos de ejemplo
python seed.py

# 5. Arrancar
flask --app app run --debug
```

Abre <http://127.0.0.1:5000> en el navegador.

### Reiniciar la base de datos

```bash
flask --app app init-db      # borra y recrea las tablas
```

La base de datos se guarda en `instance/estudiantes.db` (ignorada por git).

## Estructura

```
gestion-estudiantes/
├── app.py            # rutas, login de admin y validación
├── db.py             # conexión y consultas SQLite
├── schema.sql        # esquema de la tabla estudiantes
├── seed.py           # datos de ejemplo
├── requirements.txt
├── templates/        # base, index, form, resumen, login
└── static/style.css
```

## Esquema de datos

| Campo      | Tipo    | Notas                              |
|------------|---------|------------------------------------|
| id         | INTEGER | clave primaria autoincremental     |
| nombre     | TEXT    | obligatorio                        |
| apellido   | TEXT    | obligatorio                        |
| edad       | INTEGER | 1–99                               |
| grado      | TEXT    | `6to`, `7mo`, `8vo`, `9no`, `10mo`, `11mo` |
| seccion    | TEXT    | `A`, `B`, `C`, …                   |
| creado_en  | TEXT    | fecha/hora de alta (automática)    |

## Licencia

MIT
