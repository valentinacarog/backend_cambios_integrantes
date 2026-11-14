# NUEVO: FUNCIONES QUE DIBUJAN CADA GRAFICA CON MATPLOTLIB (RECIBEN JSON Y DEVUELVEN BYTES PNG)
import io

# NUEVO: SE USA LA API ORIENTADA A OBJETOS (FIGURE) Y NO PYPLOT PARA QUE SEA SEGURA CON VARIAS PETICIONES A LA VEZ
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator

# NUEVO: PALETA IGUAL A LOS COLORES DE LAS CATEGORIAS DEL ESQUEMA SQL
C_PROCESO = "#f59e0b"
C_CULMINADO = "#10b981"
C_TOMADO = "#6366f1"
C_ROSA = "#ec4899"
C_GRIS = "#94a3b8"
C_TEXTO = "#1e293b"

# NUEVO: COLORES POR ESTADO DE RETO
COLORES_ESTADO_RETO = {
    "ABIERTO": C_TOMADO,
    "EN_PROGRESO": C_PROCESO,
    "CERRADO": C_GRIS,
    "FINALIZADO": C_CULMINADO,
}
ETIQUETAS_ESTADO_RETO = {
    "ABIERTO": "Abierto",
    "EN_PROGRESO": "En progreso",
    "CERRADO": "Cerrado",
    "FINALIZADO": "Finalizado",
}


def _nueva_figura(ancho=10, alto=5):
    # NUEVO: CREA UNA FIGURA CON FONDO BLANCO Y TEXTO OSCURO
    fig = Figure(figsize=(ancho, alto), dpi=110, facecolor="white")
    FigureCanvasAgg(fig)
    return fig


def _estilo_ejes(ax):
    # NUEVO: QUITA BORDES SOBRANTES Y AGREGA CUADRICULA SUAVE
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.spines["left"].set_color("#cbd5e1")
    ax.spines["bottom"].set_color("#cbd5e1")
    ax.tick_params(colors=C_TEXTO, labelsize=9)
    ax.set_axisbelow(True)


def _sin_datos(ax, mensaje="Sin datos para mostrar"):
    # NUEVO: MENSAJE CUANDO NO HAY INFORMACION
    ax.axis("off")
    ax.text(0.5, 0.5, mensaje, ha="center", va="center", fontsize=12, color=C_GRIS, transform=ax.transAxes)


def _a_png(fig):
    # NUEVO: CONVIERTE LA FIGURA EN BYTES PNG
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
    return buf.getvalue()


def _acortar(texto, largo=28):
    # NUEVO: RECORTA TITULOS LARGOS PARA QUE QUEPAN EN EL EJE
    texto = str(texto or "")
    return texto if len(texto) <= largo else texto[: largo - 1] + "…"


def _dona(ax, etiquetas, valores, colores, centro_texto, centro_sub):
    # NUEVO: GRAFICA DE DONA CON UN TOTAL EN EL CENTRO
    total = sum(valores)
    if total == 0:
        _sin_datos(ax)
        return
    ax.pie(
        valores,
        colors=colores,
        startangle=90,
        counterclock=False,
        wedgeprops=dict(width=0.38, edgecolor="white", linewidth=2),
    )
    ax.text(0, 0.06, str(centro_texto), ha="center", va="center", fontsize=22, fontweight="bold", color=C_TEXTO)
    ax.text(0, -0.16, centro_sub, ha="center", va="center", fontsize=9, color=C_GRIS)
    ax.legend(
        [f"{e}: {v}" for e, v in zip(etiquetas, valores)],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.02),
        ncol=2,
        frameon=False,
        fontsize=9,
    )
    ax.set_aspect("equal")


def _barras_apiladas_h(ax, nombres, series, colores, etiquetas):
    # NUEVO: BARRAS HORIZONTALES APILADAS (UNA FILA POR NOMBRE, UNA SERIE POR COLOR)
    if not nombres or all(sum(s) == 0 for s in series):
        _sin_datos(ax)
        return
    pos = list(range(len(nombres)))
    izquierda = [0] * len(nombres)
    for valores, color, etiqueta in zip(series, colores, etiquetas):
        ax.barh(pos, valores, left=izquierda, color=color, label=etiqueta, height=0.62)
        for i, v in enumerate(valores):
            if v > 0:
                ax.text(izquierda[i] + v / 2, i, str(v), ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        izquierda = [a + b for a, b in zip(izquierda, valores)]
    ax.set_yticks(pos)
    ax.set_yticklabels([_acortar(n) for n in nombres])
    ax.invert_yaxis()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.xaxis.grid(True, color="#e2e8f0")
    _estilo_ejes(ax)
    # NUEVO: LEYENDA DEBAJO DEL EJE PARA QUE NO TAPE LAS BARRAS
    ax.legend(frameon=False, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=len(series))


# ====================================================================
# NUEVO: GRAFICAS DEL PANEL DE ADMINISTRACION
# ====================================================================

def admin_estudiantes(d):
    # NUEVO: ESTUDIANTES/DEV -> DONA ACTIVOS VS INACTIVOS + RETOS EN PROCESO Y CULMINADOS POR ESTUDIANTE
    fig = _nueva_figura(11, 5.2)
    ax1, ax2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.7]})
    activos, inactivos = d.get("activos", 0), d.get("inactivos", 0)
    _dona(ax1, ["Activos", "Inactivos"], [activos, inactivos], [C_CULMINADO, C_GRIS],
          d.get("totalEstudiantes", activos + inactivos), "estudiantes / devs")
    ests = d.get("estudiantes", [])
    _barras_apiladas_h(
        ax2,
        [e.get("nombre", "") for e in ests],
        [[e.get("enProceso", 0) for e in ests], [e.get("culminados", 0) for e in ests]],
        [C_PROCESO, C_CULMINADO],
        ["En proceso", "Culminados"],
    )
    ax2.set_title("Retos por estudiante", fontsize=11, color=C_TEXTO, loc="left")
    fig.suptitle("Estudiantes / Devs", fontsize=14, fontweight="bold", color=C_TEXTO, x=0.02, ha="left")
    fig.tight_layout()
    return _a_png(fig)


def admin_retos_estado(d):
    # NUEVO: RETOS EN TOTAL -> CUANTOS HAY EN CADA ESTADO
    fig = _nueva_figura(9, 5)
    ax = fig.subplots()
    estados = d.get("estados", {})
    claves = list(ETIQUETAS_ESTADO_RETO.keys())
    valores = [estados.get(k, 0) for k in claves]
    if sum(valores) == 0:
        _sin_datos(ax)
    else:
        barras = ax.bar([ETIQUETAS_ESTADO_RETO[k] for k in claves], valores,
                        color=[COLORES_ESTADO_RETO[k] for k in claves], width=0.55)
        for b, v in zip(barras, valores):
            ax.text(b.get_x() + b.get_width() / 2, v + max(valores) * 0.02, str(v), ha="center", fontsize=11,
                    fontweight="bold", color=C_TEXTO)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.grid(True, color="#e2e8f0")
        ax.set_ylim(0, max(valores) * 1.18)
        _estilo_ejes(ax)
    ax.set_title(f"Retos en total: {d.get('total', sum(valores))}", fontsize=14, fontweight="bold",
                 color=C_TEXTO, loc="left")
    fig.tight_layout()
    return _a_png(fig)


def admin_retos_tomados(d):
    # NUEVO: RETOS TOMADOS -> DONA EN PROCESO VS CULMINADOS + DETALLE POR RETO
    fig = _nueva_figura(11, 5.2)
    ax1, ax2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.7]})
    en_proceso, culminados = d.get("enProceso", 0), d.get("culminados", 0)
    _dona(ax1, ["En proceso", "Culminados"], [en_proceso, culminados], [C_PROCESO, C_CULMINADO],
          d.get("tomados", en_proceso + culminados), "retos tomados")
    retos = d.get("retos", [])
    _barras_apiladas_h(
        ax2,
        [r.get("titulo", "") for r in retos],
        [[r.get("enProceso", 0) for r in retos], [r.get("culminados", 0) for r in retos]],
        [C_PROCESO, C_CULMINADO],
        ["En proceso", "Culminados"],
    )
    ax2.set_title("Retos más tomados", fontsize=11, color=C_TEXTO, loc="left")
    fig.suptitle("Retos tomados, en proceso y culminados", fontsize=14, fontweight="bold", color=C_TEXTO,
                 x=0.02, ha="left")
    fig.tight_layout()
    return _a_png(fig)


def admin_empresas(d):
    # NUEVO: EMPRESAS PATROCINADORAS -> RETOS PUBLICADOS POR ESTADO + PARTICIPACION DE ESTUDIANTES
    fig = _nueva_figura(12, 5.4)
    ax1, ax2 = fig.subplots(1, 2)
    emps = d.get("empresas", [])
    nombres = [e.get("nombre", "") for e in emps]
    claves = list(ETIQUETAS_ESTADO_RETO.keys())
    series = [[(e.get("retosPorEstado") or {}).get(k, 0) for e in emps] for k in claves]
    _barras_apiladas_h(ax1, nombres, series, [COLORES_ESTADO_RETO[k] for k in claves],
                       [ETIQUETAS_ESTADO_RETO[k] for k in claves])
    ax1.set_title("Retos publicados", fontsize=11, color=C_TEXTO, loc="left")
    _barras_apiladas_h(
        ax2,
        nombres,
        [[e.get("enProceso", 0) for e in emps], [e.get("culminados", 0) for e in emps]],
        [C_PROCESO, C_CULMINADO],
        ["En proceso", "Culminados"],
    )
    ax2.set_title("Retos tomados por estudiantes", fontsize=11, color=C_TEXTO, loc="left")
    fig.suptitle("Empresas patrocinadoras", fontsize=14, fontweight="bold", color=C_TEXTO, x=0.02, ha="left")
    fig.tight_layout()
    return _a_png(fig)


# ====================================================================
# NUEVO: GRAFICA DEL AREA DE ESTUDIANTES / DEVS (SOLO SUS PROPIOS RETOS)
# ====================================================================

def estudiante_mis_retos(d):
    # NUEVO: DONA EN PROCESO VS CULMINADOS + PUNTOS (XP) DE CADA RETO QUE TOMO EL ESTUDIANTE
    fig = _nueva_figura(11, 5.2)
    ax1, ax2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.7]})
    en_proceso, culminados = d.get("enProceso", 0), d.get("culminados", 0)
    _dona(ax1, ["En proceso", "Culminados"], [en_proceso, culminados], [C_PROCESO, C_CULMINADO],
          en_proceso + culminados, "retos tomados")
    retos = d.get("retos", [])
    if not retos:
        _sin_datos(ax2, "Aún no has tomado retos")
    else:
        pos = list(range(len(retos)))
        colores = [C_CULMINADO if r.get("culminado") else C_PROCESO for r in retos]
        valores = [r.get("puntos", 0) for r in retos]
        ax2.barh(pos, valores, color=colores, height=0.6)
        for i, v in enumerate(valores):
            ax2.text(v, i, f"  {v} XP", va="center", fontsize=9, color=C_TEXTO)
        ax2.set_yticks(pos)
        ax2.set_yticklabels([_acortar(r.get("titulo", ""), 34) for r in retos])
        ax2.invert_yaxis()
        ax2.set_xlim(0, max(valores) * 1.25 if max(valores) else 1)
        ax2.xaxis.grid(True, color="#e2e8f0")
        _estilo_ejes(ax2)
        # NUEVO: LEYENDA MANUAL DE COLORES
        ax2.legend(handles=[Patch(color=C_PROCESO, label="En proceso"), Patch(color=C_CULMINADO, label="Culminado")],
                   frameon=False, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2)
    ax2.set_title(f"Puntos ganados: {d.get('puntosGanados', 0)} XP", fontsize=11, color=C_TEXTO, loc="left")
    fig.suptitle("Mis retos", fontsize=14, fontweight="bold", color=C_TEXTO, x=0.02, ha="left")
    fig.tight_layout()
    return _a_png(fig)


# NUEVO: TABLA QUE CONECTA EL NOMBRE DE LA RUTA CON LA FUNCION QUE DIBUJA
GRAFICAS = {
    "admin-estudiantes": admin_estudiantes,
    "admin-retos-estado": admin_retos_estado,
    "admin-retos-tomados": admin_retos_tomados,
    "admin-empresas": admin_empresas,
    "estudiante-mis-retos": estudiante_mis_retos,
}
