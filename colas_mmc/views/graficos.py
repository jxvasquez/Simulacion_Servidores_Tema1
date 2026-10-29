# =============================================================================
#  views/graficos.py
#  -----------------------------------------------------------------------------
#  Genera los GRÁFICOS COMPARATIVOS con matplotlib.
#
#  ¿Cómo llegan los gráficos a la página web?
#    1. matplotlib dibuja la figura en memoria (no se guarda en disco).
#    2. La convertimos a una imagen PNG.
#    3. La PNG se transforma en texto "base64".
#    4. Ese texto se coloca dentro de una etiqueta <img src="data:...">.
#  Así no hay que crear ni borrar archivos de imagen.
# =============================================================================

import base64
import io

# -----------------------------------------------------------------------------
#  IMPORTANTE: elegir el "backend" Agg ANTES de importar pyplot.
#  Agg dibuja imágenes sin abrir ventanas, que es lo que necesita un
#  servidor web. Si no lo hacemos, matplotlib podría intentar abrir una
#  ventana y fallar.
# -----------------------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D


# -----------------------------------------------------------------------------
#  Paleta de colores (la misma que usa el CSS de la página)
# -----------------------------------------------------------------------------
COLOR_TINTA = "#19304D"        # texto principal
COLOR_TINTA_SUAVE = "#5C718A"  # texto secundario y ejes
COLOR_REJILLA = "#DCE8F6"      # líneas de fondo muy suaves
COLOR_FONDO = "#FFFFFF"

COLOR_CUMPLE = "#2E8B57"       # verde: cumple la meta de espera
COLOR_NO_CUMPLE = "#B23B2E"    # rojo: no cumple la meta
COLOR_INESTABLE = "#8A949C"    # gris: la fila crece sin límite

COLOR_SERIE_1 = "#3E7CB8"      # azul: primera serie de datos
COLOR_SERIE_2 = "#9CBFE8"      # azul suave: segunda serie de datos


# -----------------------------------------------------------------------------
#  Función auxiliar: estilo común para todos los gráficos
# -----------------------------------------------------------------------------
def _preparar_ejes(titulo, etiqueta_y, tamano=(6.4, 4.0)):
    """
    Crea una figura vacía con un estilo limpio y la devuelve.
    Así todos los gráficos se ven iguales y el código no se repite.

    'tamano' es (ancho, alto) en pulgadas. Los gráficos que se muestran
    más pequeños en la página usan una figura más chica, así el texto
    se ve del mismo tamaño en todos.
    """
    figura, ejes = plt.subplots(figsize=tamano, dpi=120)

    figura.patch.set_facecolor(COLOR_FONDO)
    ejes.set_facecolor(COLOR_FONDO)

    # Título a la izquierda, como un encabezado de sección
    ejes.set_title(titulo, loc="left", fontsize=12, fontweight="bold",
                   color=COLOR_TINTA, pad=14)

    ejes.set_ylabel(etiqueta_y, fontsize=9.5, color=COLOR_TINTA_SUAVE)
    ejes.set_xlabel("Ventanillas abiertas", fontsize=9.5, color=COLOR_TINTA_SUAVE)

    # Quitamos los bordes superior y derecho (no aportan información)
    ejes.spines["top"].set_visible(False)
    ejes.spines["right"].set_visible(False)
    ejes.spines["left"].set_color(COLOR_REJILLA)
    ejes.spines["bottom"].set_color(COLOR_TINTA_SUAVE)

    # Rejilla horizontal suave DETRÁS de las barras
    ejes.yaxis.grid(True, color=COLOR_REJILLA, linewidth=1)
    ejes.set_axisbelow(True)

    ejes.tick_params(colors=COLOR_TINTA_SUAVE, labelsize=9, length=0)

    return figura, ejes


# -----------------------------------------------------------------------------
#  Función auxiliar: convertir una figura en texto base64
# -----------------------------------------------------------------------------
def _figura_a_base64(figura):
    """
    Guarda la figura en un "archivo en memoria" (BytesIO), lo codifica
    en base64 y cierra la figura para liberar memoria.
    """
    memoria = io.BytesIO()
    figura.tight_layout()
    figura.savefig(memoria, format="png", facecolor=figura.get_facecolor())
    plt.close(figura)     # ¡muy importante en un servidor para no acumular figuras!

    memoria.seek(0)
    return base64.b64encode(memoria.read()).decode("utf-8")


# =============================================================================
#  GRÁFICO 1: Tiempo de espera Wq vs. la meta de 2 minutos
# =============================================================================
def grafico_tiempo_espera(escenarios, meta):
    """
    Barras con el Wq teórico de cada escenario.
      - Verde  = cumple la meta (Wq <= 2 min)
      - Rojo   = no cumple
      - Gris   = sistema inestable (la fila nunca deja de crecer)
    Además se dibuja el Wq SIMULADO como un punto con su intervalo de
    confianza, y una línea punteada con la meta.
    """
    figura, ejes = _preparar_ejes("Tiempo promedio de espera en fila (Wq)",
                                  "Minutos")

    etiquetas = [str(e["ventanillas"]) for e in escenarios]
    posiciones = list(range(len(escenarios)))

    # --- Altura máxima del eje: el mayor Wq finito, o la meta si es mayor.
    valores_finitos = [e["wq"] for e in escenarios if e["estable"]]
    techo = max(valores_finitos + [meta]) * 1.30

    for i, escenario in enumerate(escenarios):

        # (a) Caso inestable: barra gris rayada hasta el techo
        if not escenario["estable"]:
            ejes.bar(i, techo * 0.92, width=0.56, color=COLOR_FONDO,
                     edgecolor=COLOR_INESTABLE, hatch="///", linewidth=1.2)
            ejes.text(i, techo * 0.94, "Inestable\n(ρ ≥ 1)", ha="center",
                      va="bottom", fontsize=9, color=COLOR_TINTA_SUAVE)
            continue

        # (b) Caso estable: color según cumpla o no la meta
        color = COLOR_CUMPLE if escenario["cumple_meta"] else COLOR_NO_CUMPLE
        ejes.bar(i, escenario["wq"], width=0.56, color=color)

        # (c) Punto del valor simulado con su intervalo de confianza
        sim = escenario["simulacion"]
        altura_texto = escenario["wq"]

        if sim is not None:
            # El texto irá por encima del punto más alto (barra o intervalo)
            altura_texto = max(altura_texto, sim["wq_max"])
            ejes.errorbar(i, sim["wq"], yerr=sim["wq_margen"], fmt="D",
                          markersize=6, color=COLOR_TINTA, markerfacecolor=COLOR_FONDO,
                          markeredgewidth=1.6, capsize=4, linewidth=1.4, zorder=5)

        # (d) Valor escrito encima, centrado, con un símbolo de estado
        simbolo = "✓" if escenario["cumple_meta"] else "✗"
        ejes.text(i, altura_texto + techo * 0.02, f"{escenario['wq']:.2f} min {simbolo}",
                  ha="center", va="bottom", fontsize=9.5, color=COLOR_TINTA,
                  fontweight="bold")

    # --- Línea de la meta
    ejes.axhline(meta, color=COLOR_TINTA, linestyle=(0, (5, 4)), linewidth=1.3)
    # La etiqueta va FUERA del área de barras (a la derecha) para que nunca
    # se encime con los valores escritos sobre las barras.
    ejes.text(len(escenarios) - 0.38, meta, f"Meta\n{meta:g} min", ha="left",
              va="center", fontsize=9, color=COLOR_TINTA, fontweight="bold")

    ejes.set_xticks(posiciones)
    ejes.set_xticklabels(etiquetas)
    ejes.set_ylim(0, techo * 1.12)
    ejes.set_xlim(-0.6, len(escenarios) - 0.4)

    # --- Leyenda (para que el color nunca sea la única pista)
    leyenda = [
        Patch(color=COLOR_CUMPLE, label="Cumple la meta"),
        Patch(color=COLOR_NO_CUMPLE, label="No cumple"),
        Line2D([0], [0], marker="D", color=COLOR_TINTA, markerfacecolor=COLOR_FONDO,
               linestyle="none", label="Simulado (IC 95 %)"),
    ]
    ejes.legend(handles=leyenda, loc="upper right", fontsize=8.5, frameon=False)

    return _figura_a_base64(figura)


# =============================================================================
#  GRÁFICO 2: Estudiantes promedio en la fila (Lq)
# =============================================================================
def grafico_estudiantes_fila(escenarios):
    """
    Una barra por escenario con la cantidad promedio de estudiantes
    esperando. Es una sola serie, así que usa un solo color.
    """
    figura, ejes = _preparar_ejes("Estudiantes promedio en fila (Lq)",
                                  "Estudiantes", tamano=(4.6, 3.6))

    valores_finitos = [e["lq"] for e in escenarios if e["estable"]]
    techo = max(valores_finitos + [0.5]) * 1.30

    for i, escenario in enumerate(escenarios):

        if not escenario["estable"]:
            ejes.bar(i, techo * 0.92, width=0.56, color=COLOR_FONDO,
                     edgecolor=COLOR_INESTABLE, hatch="///", linewidth=1.2)
            ejes.text(i, techo * 0.94, "Crece sin\nlímite", ha="center",
                      va="bottom", fontsize=9, color=COLOR_TINTA_SUAVE)
            continue

        ejes.bar(i, escenario["lq"], width=0.56, color=COLOR_SERIE_1)
        ejes.text(i, escenario["lq"], f"{escenario['lq']:.2f}", ha="center",
                  va="bottom", fontsize=9.5, color=COLOR_TINTA, fontweight="bold")

    ejes.set_xticks(range(len(escenarios)))
    ejes.set_xticklabels([str(e["ventanillas"]) for e in escenarios])
    ejes.set_ylim(0, techo * 1.12)

    return _figura_a_base64(figura)


# =============================================================================
#  GRÁFICO 3: Utilización (ρ) y probabilidad de sistema vacío (P0)
# =============================================================================
def grafico_utilizacion_vacio(escenarios):
    """
    Barras agrupadas: para cada escenario, una barra azul con ρ y una
    barra azul claro con P0. Ambas son proporciones, por eso comparten el
    mismo eje de 0 % a 100 %.
    """
    figura, ejes = _preparar_ejes("Utilización (ρ) y sistema vacío (P0)",
                                  "Porcentaje", tamano=(4.6, 3.6))

    ancho = 0.34          # ancho de cada barra
    separacion = 0.02     # pequeño espacio entre las dos barras del grupo

    for i, escenario in enumerate(escenarios):

        # ρ se limita a 100 % para el dibujo (si es inestable puede pasar de 1)
        rho_dibujo = min(escenario["rho"], 1.0) * 100
        p0_dibujo = escenario["p0"] * 100

        x_rho = i - ancho / 2 - separacion / 2
        x_p0 = i + ancho / 2 + separacion / 2

        ejes.bar(x_rho, rho_dibujo, width=ancho, color=COLOR_SERIE_1)
        ejes.bar(x_p0, p0_dibujo, width=ancho, color=COLOR_SERIE_2)

        # Etiquetas con el valor exacto
        texto_rho = f"{escenario['rho'] * 100:.1f} %"
        ejes.text(x_rho, rho_dibujo + 1.5, texto_rho, ha="center", va="bottom",
                  fontsize=8.5, color=COLOR_TINTA)
        ejes.text(x_p0, p0_dibujo + 1.5, f"{p0_dibujo:.1f} %", ha="center",
                  va="bottom", fontsize=8.5, color=COLOR_TINTA)

    ejes.set_xticks(range(len(escenarios)))
    ejes.set_xticklabels([str(e["ventanillas"]) for e in escenarios])
    # Dejamos espacio libre arriba (hasta 132 %) para que la leyenda
    # no tape las etiquetas de las barras.
    ejes.set_ylim(0, 132)
    ejes.set_yticks([0, 25, 50, 75, 100])
    ejes.set_yticklabels(["0 %", "25 %", "50 %", "75 %", "100 %"])

    leyenda = [
        Patch(color=COLOR_SERIE_1, label="Utilización ρ"),
        Patch(color=COLOR_SERIE_2, label="Sistema vacío P0"),
    ]
    ejes.legend(handles=leyenda, loc="upper center", fontsize=8.5,
                frameon=False, ncol=2)

    return _figura_a_base64(figura)


# =============================================================================
#  Función que crea TODOS los gráficos de una vez
# =============================================================================
def generar_graficos(resultados):
    """
    Recibe el diccionario de resultados del modelo y devuelve otro
    diccionario con las tres imágenes en base64, listas para el HTML.
    """
    escenarios = resultados["escenarios"]

    return {
        "espera": grafico_tiempo_espera(escenarios, resultados["meta"]),
        "fila": grafico_estudiantes_fila(escenarios),
        "utilizacion": grafico_utilizacion_vacio(escenarios),
    }
