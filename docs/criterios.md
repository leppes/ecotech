# Rúbrica UA2: dónde está la evidencia de cada criterio

Los criterios **G** se revisan en el código. Los **I** son orales e individuales:
cada integrante tiene que poder explicarlos con sus palabras, mostrando el archivo.

## 2.1.1 · Del UML al código

| Criterio | Evidencia |
|---|---|
| G.1 Clases del UML con atributos, constructores y métodos | `dominio/`: 5 clases con tipos, cada una con `__init__`, propiedades, `__str__` y `__repr__`. **Faltan métodos de negocio** (ver nota abajo). **Comparar contra el diagrama UML**: si tiene más clases, atributos o métodos, faltan. |
| G.2 Relaciones del diseño en el código | Herencia `class Empleado(Persona)`; asociación `Empleado.departamento_id`; N:M resuelta con `RegistroTiempo`; composición con `empleado_rut` de solo lectura + `ON DELETE CASCADE`. Tabla en el README, «Paso 1». |
| I.3 Explicar la correspondencia UML ↔ clases, atributos y constructores | Tabla «Paso 1» del README, con el diagrama al lado. |
| I.4 Cómo se tradujeron las relaciones a Python | Herencia → `super().__init__(rut, nombre)`. Asociación → llave (`departamento_id`) + FK. Composición → atributo de solo lectura + cascada. |

## 2.1.2 · Principios de POO

| Criterio | Evidencia |
|---|---|
| G.5 Encapsulamiento y herencia | Atributos `_privados` con `@property`; los setters validan. Herencia `Empleado(Persona)`; abstracción: `Menu(ABC)` con `@abstractmethod opciones()`. |
| G.6 Consistencia diseño-código, reutilizando clases | `dominio/validaciones.py` (lo usan el dominio y el menú), `MenuCatalogo` para departamentos y proyectos, `Empleado.__str__` con `super()`. |
| I.7 Justificar el encapsulamiento | Un objeto nunca queda inválido: todo pasa por el setter. `rut` e `id` son de solo lectura porque son la identidad. Probar: `demo.py`, sección «Encapsulamiento». |
| I.8 Argumentar cómo se evitó duplicar código | Reglas escritas una vez en `validaciones.py`; ciclo de menú y manejo de errores una vez en `Menu`; un solo mapper por repositorio; `_SELECT_BASE`. |

## 2.1.3 · Conexión a la base de datos

| Criterio | Evidencia |
|---|---|
| G.9 Conexión con librería oficial | `sqlite3` (biblioteca estándar), en `infraestructura/conexion.py`. |
| G.10 Ejecuta el CRUD verificando su funcionamiento | `python main.py` (menú) y `python demo.py` (demo con ✔/✘ por operación). |
| I.11 Proceso de configuración y parámetros | `.env` (`DB_MOTOR`, `DB_NOMBRE`) leído con `python-dotenv`; `PRAGMA foreign_keys = ON`; `probar_conexion()`. README, «Configuración» y «Paso 3». |
| I.12 Lógica de las operaciones CRUD | Repositorios: consultas con `?`, un mapper `_fila_a_...`, `guardar` devuelve el id asignado, `eliminar` devuelve `True/False`, decisiones de borrado (C08). |

## 2.1.4 · Manejo de errores

| Criterio | Evidencia |
|---|---|
| G.13 try-except en la ejecución y en la conexión | Conexión: `obtener_conexion()` (`OperationalError` → `ErrorDeConexion`). Ejecución: repositorios (`IntegrityError` → errores del dominio), `Menu._ejecutar`, `main.py`. |
| G.14 Valida entradas del usuario sin interrumpir el programa | `interfaz/consola.py` (`pedir` repite hasta recibir un dato válido), `Menu._ejecutar`, Ctrl+C en `main.py`. README, «Validación de las entradas del usuario». |
| I.15 Explicar cada try-except y qué falla captura | Tabla «Manejo de errores (C09)» del README: excepción de origen, dónde se captura y en qué se convierte. |
| I.16 Cómo las validaciones protegen frente al usuario | Dos capas: la interfaz convierte el tipo y el dominio aplica la regla; la base además tiene `CHECK`, `NOT NULL` y FK. Consultas parametrizadas contra inyección. |

## 2.1.5 · Uso crítico de IA

| Criterio | Evidencia |
|---|---|
| G.17 Analiza y prueba el código de la IA | `docs/bitacora_ia.md`: auditoría (parametrización, capturas, librerías) y pruebas hechas. |
| G.18 Modifica, adapta o descarta el código de la IA con justificación | `docs/bitacora_ia.md`: **pendiente, la decisión la escribe el equipo**. |
| I.19 Qué fragmentos se hicieron con IA | `docs/bitacora_ia.md`, lista de fragmentos por archivo. |
| I.20 Criterios técnicos (seguridad, eficiencia, coherencia) para decidir | `docs/bitacora_ia.md`, «Puntos que conviene evaluar». |

## Polimorfismo (sección 3.3 C del informe)

`MenuPrincipal.opciones()` recorre una colección mixta de submenús
(`MenuEmpleados`, `MenuCatalogo`, `MenuRegistros`) y llama a `submenu.mostrar`
sin preguntar de qué clase es cada uno. Y `Menu.mostrar()` llama a
`self.opciones()`, que cada subclase implementa a su manera.
`mostrar_lista()` imprime cualquier objeto del dominio con `str()`, y cada clase
responde con su propio `__str__`; el de `Empleado` reutiliza el de `Persona` con `super()`.

## Nota: métodos de negocio (G.1)

La escala pide «métodos funcionales» y la plantilla del informe (3.2) pide
métodos de cálculo propios del negocio. Las clases del dominio solo tienen
propiedades, `__str__` y `__repr__`. Hay que agregar los métodos que figuran en
el diagrama UML de la Unidad 1 (por ejemplo, cálculo de remuneración o de
antigüedad del empleado, o total de horas), respetando sus nombres.

