-- db/01_esquema.sql  (SQLite)
-- Repetible: corre sobre una base vacía y también dos veces seguidas (IF NOT EXISTS).
-- Orden: primero las tablas a las que otras apuntan.

CREATE TABLE IF NOT EXISTS departamento (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre  TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS proyecto (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre  TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS persona (
    rut     TEXT PRIMARY KEY,                 -- texto, no número (dígito verificador y ceros)
    nombre  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS empleado (
    rut             TEXT PRIMARY KEY,
    fecha_ingreso   DATE NOT NULL,            -- fecha, no texto
    sueldo_base     INTEGER NOT NULL CHECK (sueldo_base >= 0),
    departamento_id INTEGER,
    -- Empleado ES una persona: si se borra la persona, se borra el empleado.
    FOREIGN KEY (rut) REFERENCES persona(rut) ON DELETE CASCADE,
    -- No se puede borrar un departamento que todavía tiene empleados.
    FOREIGN KEY (departamento_id) REFERENCES departamento(id) ON DELETE RESTRICT
);

-- Tabla intermedia de la relación N:M empleado <-> proyecto.
CREATE TABLE IF NOT EXISTS registro_tiempo (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    empleado_rut  TEXT NOT NULL,
    proyecto_id   INTEGER NOT NULL,
    horas         REAL NOT NULL CHECK (horas > 0 AND horas <= 24),
    fecha         DATE NOT NULL,
    -- Composición ◆: los registros mueren con su empleado.
    FOREIGN KEY (empleado_rut) REFERENCES empleado(rut) ON DELETE CASCADE,
    FOREIGN KEY (proyecto_id)  REFERENCES proyecto(id)  ON DELETE RESTRICT
);
