# NUEVO: APARTADO "GRAFICAS" (MATPLOTLIB + BACKEND SPRING BOOT)
backend_cambios_integrantes/
├── pom.xml
├── Dockerfile
├── README.md
├── GRAFICAS_README.md                      (NUEVO) guía del apartado
├── database/schema.sql
├── graficas/                               (NUEVO) servicio Python
│   ├── app.py                              servidor Flask
│   ├── charts.py                           funciones matplotlib
│   ├── samples.py                          datos de ejemplo
│   ├── requirements.txt                    flask, matplotlib, gunicorn
│   ├── setup_venv.sh / setup_venv.bat      crean el ambiente virtual
│   ├── run.sh / run.bat                    inician el servicio
│   ├── Dockerfile
│   └── .gitignore
└── src/main/
    ├── java/com/cesde/proyectointegrador/
    │   ├── config/SecurityConfig.java      (sin cambios)
    │   └── modules/
    │       ├── auth, usuarios, retos, empresas,
    │       │   categorias, registros, health   (sin cambios)
    │       └── graficas/                   (NUEVO)
    │           ├── controller/GraficaController.java
    │           ├── service/GraficaService.java
    │           └── config/GraficasSecurityConfig.java
    └── resources/
        ├── application.properties          (sin cambios)
        └── static/                         (NUEVO)
            ├── graficas.html               página para ver las gráficas
            └── graficas/
                ├── graficas-panel.js       menú desplegable y carga de imágenes
                └── graficas-panel.css      estilos

## Como funciona

```
Frontend / graficas.html  --JWT-->  Spring Boot (/api/graficas/**)  --JSON-->  Python + matplotlib (puerto 5000)
                                    calcula los datos con JPA              <--PNG--  dibuja la grafica
```

- Spring Boot valida el token y el rol, calcula los datos y le pide la imagen a Python.
- Python (carpeta `graficas/`) solo dibuja con matplotlib; no toca la base de datos.
- El estudiante siempre ve **sus propios** retos (el correo sale del token, no de un parametro).

## Archivos nuevos (no se modifico ningun archivo existente)

| Archivo | Que hace |
| :--- | :--- |
| `graficas/` | Servicio Python: `app.py`, `charts.py`, `samples.py`, `requirements.txt`, scripts del ambiente virtual, `Dockerfile` |
| `modules/graficas/service/GraficaService.java` | Arma los datos y llama a Python |
| `modules/graficas/controller/GraficaController.java` | Endpoints PNG con control de rol |
| `modules/graficas/config/GraficasSecurityConfig.java` | Deja publica solo la pagina `graficas.html` (sin tocar `SecurityConfig`) |
| `static/graficas.html` | Vista de las graficas en el backend |
| `static/graficas/graficas-panel.js` y `.css` | Menu desplegable "Graficas" reutilizable en el frontend |

## Como ejecutarlo

1. **Ambiente virtual de Python** (una sola vez):
   - Linux/Mac: `cd graficas && ./setup_venv.sh`
   - Windows: `cd graficas` y luego `setup_venv.bat`
2. **Iniciar el servicio de graficas**: `./run.sh` (o `run.bat`). Queda en `http://localhost:5000`.
   - Prueba sin base de datos: abre `http://localhost:5000/` y veras las 5 graficas con datos de ejemplo.
3. **Iniciar el backend Java** como siempre (`mvn clean spring-boot:run`).
4. **Ver en el backend**: abre `http://localhost:3000/graficas.html` e inicia sesion
   (admin: `admin@sistema.com`, estudiante: `mariana.gomez@tech.co`).

Variables de entorno opcionales: `APP_GRAFICAS_URL` (por defecto `http://localhost:5000`) y,
para proteger el servicio Python, la misma clave en `GRAFICAS_API_KEY` (Python) y `APP_GRAFICAS_KEY` (Java).

## Endpoints

| Rol | Endpoint | Grafica |
| :--- | :--- | :--- |
| ADMIN | `GET /api/graficas/admin/estudiantes` | Estudiantes/devs: activos vs inactivos y retos en proceso/culminados por estudiante |
| ADMIN | `GET /api/graficas/admin/retos-estado` | Retos en total por estado |
| ADMIN | `GET /api/graficas/admin/retos-tomados` | Retos tomados: en proceso vs culminados y detalle por reto |
| ADMIN | `GET /api/graficas/admin/empresas` | Empresas patrocinadoras: retos publicados y retos tomados por estudiantes |
| USUARIO | `GET /api/graficas/estudiante/mis-retos` | Mis retos en proceso y culminados, con puntos (XP) |

## Que cuenta como "tomado", "en proceso" y "culminado"

Se toma de la tabla `registros`, solo de usuarios con rol `USUARIO`:

- **Tomado**: registro de tipo `INSCRIPCION` o `ENTREGA` sobre un reto (los `RECHAZADO` no cuentan). Cada pareja estudiante-reto cuenta una sola vez.
- **Culminado**: algun registro de esa pareja esta `COMPLETADO`.
- **En proceso**: los demas (`PENDIENTE` o `APROBADO`).

Si tu equipo define estos estados de otra forma, solo hay que ajustar `participaciones()` en `GraficaService.java`.

## Integrarlo al frontend

El modulo `static/graficas/graficas-panel.js` no depende de ninguna libreria:

```html
<link rel="stylesheet" href="graficas-panel.css">
<div id="menu-graficas"></div>      <!-- ABAJO DE TODAS LAS PESTANAS DEL MENU -->
<main id="vista-graficas"></main>   <!-- DONDE SE MUESTRAN LAS GRAFICAS -->
<script src="graficas-panel.js"></script>
<script>
  GraficasPanel.montar({
    menu: document.getElementById('menu-graficas'),
    vista: document.getElementById('vista-graficas'),
    apiBase: 'http://localhost:3000',
    rol: usuario.rol,                         // 'ADMIN' o 'USUARIO'
    obtenerToken: () => localStorage.getItem('token')
  });
</script>
```
