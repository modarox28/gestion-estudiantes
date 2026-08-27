-- Esquema de la base de datos de gestión de estudiantes
DROP TABLE IF EXISTS estudiantes;

CREATE TABLE estudiantes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT    NOT NULL,
    apellido    TEXT    NOT NULL,
    edad        INTEGER NOT NULL CHECK (edad > 0 AND edad < 100),
    grado       TEXT    NOT NULL,   -- 6to, 7mo, 8vo, 9no, 10mo, 11mo
    seccion     TEXT    NOT NULL,   -- A, B, C, ...
    creado_en   TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_estudiantes_grado   ON estudiantes (grado, seccion);
CREATE INDEX idx_estudiantes_apellido ON estudiantes (apellido, nombre);
CREATE INDEX idx_estudiantes_edad    ON estudiantes (edad);
