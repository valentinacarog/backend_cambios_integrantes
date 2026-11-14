# NUEVO: DATOS DE EJEMPLO PARA PROBAR EL SERVICIO SIN BASE DE DATOS (RUTA /demo/<nombre>.png)
MUESTRAS = {
    "admin-estudiantes": {
        "activos": 8, "inactivos": 2, "totalEstudiantes": 10,
        "estudiantes": [
            {"nombre": "Mariana Gómez", "enProceso": 2, "culminados": 3},
            {"nombre": "Felipe Restrepo", "enProceso": 1, "culminados": 1},
            {"nombre": "Camila Ortiz", "enProceso": 0, "culminados": 2},
            {"nombre": "Andrés Londoño", "enProceso": 1, "culminados": 0},
        ],
    },
    "admin-retos-estado": {
        "total": 12,
        "estados": {"ABIERTO": 5, "EN_PROGRESO": 3, "CERRADO": 1, "FINALIZADO": 3},
    },
    "admin-retos-tomados": {
        "tomados": 9, "enProceso": 5, "culminados": 4,
        "retos": [
            {"titulo": "Optimización de Consumo Energético en Servidores", "enProceso": 2, "culminados": 1},
            {"titulo": "Sistema de Trazabilidad de Residuos Reciclables", "enProceso": 2, "culminados": 2},
            {"titulo": "Microcréditos con Evaluación de Riesgo Alternativo", "enProceso": 1, "culminados": 1},
        ],
    },
    "admin-empresas": {
        "empresas": [
            {"nombre": "Innovación Digital S.A.S.", "retosPorEstado": {"ABIERTO": 2, "EN_PROGRESO": 1, "FINALIZADO": 1}, "enProceso": 3, "culminados": 1},
            {"nombre": "Ecosistemas Verdes Corp", "retosPorEstado": {"ABIERTO": 1, "EN_PROGRESO": 2}, "enProceso": 2, "culminados": 2},
            {"nombre": "Finanzas Ágiles Global", "retosPorEstado": {"ABIERTO": 2, "CERRADO": 1}, "enProceso": 0, "culminados": 1},
        ],
    },
    "estudiante-mis-retos": {
        "nombre": "Mariana Gómez", "enProceso": 2, "culminados": 1, "puntosGanados": 850,
        "retos": [
            {"titulo": "Sistema de Trazabilidad de Residuos Reciclables", "puntos": 850, "culminado": True},
            {"titulo": "Optimización de Consumo Energético en Servidores", "puntos": 1500, "culminado": False},
            {"titulo": "Microcréditos con Evaluación de Riesgo Alternativo", "puntos": 1200, "culminado": False},
        ],
    },
}
