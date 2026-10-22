# EcoTech Solutions · Sistema de Gestión de Empleados

Programa de consola en Python para registrar empleados, departamentos, proyectos y horas trabajadas.
Los datos se guardan en una base SQLite.

**Equipo:** Miguel Fuentealba (líder), Benjamín Leppe y Gonzalo Bustos · TI3021 · ES2

## Cómo ejecutarlo

1. Crear y activar el entorno virtual:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```
   En Mac o Linux, el segundo comando es `source .venv/bin/activate`.
2. Instalar las dependencias: `pip install -r requirements.txt`
3. Copiar `.env.example` con el nombre `.env` (no hay que cambiarle nada).
4. Ejecutar: `python main.py`

Al abrirse, el programa prueba la conexión, crea las tablas si no existen y muestra el menú.

## Carpetas

| Carpeta o archivo | Qué tiene |
|---|---|
| `dominio/` | Las clases del negocio, sus validaciones y sus excepciones |
| `repositorio/` | La conexión a la base y las consultas SQL |
| `datos/schema.sql` | Las tablas de la base |
| `main.py` | El menú por consola |

## Seguridad

- Todas las consultas usan `?`: si se busca `' OR '1'='1` en el menú, no aparece nadie.
- El archivo `.env` no se sube a GitHub.
- Si la base falla, el usuario ve un mensaje simple y el detalle queda en `ecotech.log`.
