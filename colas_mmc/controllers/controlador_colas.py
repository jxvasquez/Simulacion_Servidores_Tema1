

import math

from flask import Blueprint, render_template, request

import config
from models.escenarios import evaluar_escenarios
from views.graficos import generar_graficos

controlador = Blueprint("colas", __name__)
@controlador.app_template_filter("numero")
def formatear_numero(valor, decimales=2):

    if valor is None:
        return "—"

    if math.isinf(valor):
        return "∞"

    return f"{valor:.{decimales}f}"

@controlador.app_template_filter("porcentaje")
def formatear_porcentaje(valor, decimales=1):

    if valor is None:
        return "—"

    return f"{valor * 100:.{decimales}f} %"


# -----------------------------------------------------------------------------
#  Función auxiliar: leer un número positivo del formulario
# -----------------------------------------------------------------------------
def leer_tasa(nombre_campo, valor_por_defecto, nombre_visible, errores):
   
    # request.args contiene los datos enviados en la dirección web,
    # por ejemplo:  /?lambda=24&mu=10&unidad=hora
    texto = request.args.get(nombre_campo)

    # Si el campo no viene (primera visita), usamos el valor por defecto.
    if texto is None or texto.strip() == "":
        return valor_por_defecto

    # Aceptamos coma o punto como separador decimal (12,5 o 12.5)
    texto = texto.strip().replace(",", ".")

    try:
        numero = float(texto)
    except ValueError:
        errores.append(f"{nombre_visible} debe ser un número. Escribiste «{texto}».")
        return valor_por_defecto

    if numero <= 0 or math.isinf(numero) or math.isnan(numero):
        errores.append(f"{nombre_visible} debe ser mayor que cero.")
        return valor_por_defecto

    return numero


@controlador.route("/")
def inicio():
    

    # --- 1) Leer y validar los datos del formulario --------------------------
    errores = []

    tasa_llegada = leer_tasa("lambda", config.LAMBDA_POR_DEFECTO,
                             "La tasa de llegada (λ)", errores)

    tasa_atencion = leer_tasa("mu", config.MU_POR_DEFECTO,
                              "La tasa de atención (μ)", errores)

    unidad = request.args.get("unidad", config.UNIDAD_POR_DEFECTO)
    if unidad not in ("hora", "minuto"):
        errores.append("La unidad debe ser «hora» o «minuto».")
        unidad = config.UNIDAD_POR_DEFECTO

    # Datos que siempre se envían a la vista (para rellenar el formulario)
    datos_formulario = {
        "lambda": tasa_llegada,
        "mu": tasa_atencion,
        "unidad": unidad,
    }

    # --- 2) Si hay errores, mostramos la página solo con los mensajes --------
    if errores:
        return render_template(
            "index.html",
            formulario=datos_formulario,
            errores=errores,
            resultados=None,
            graficos=None,
            config=config,
        )

    # --- 3) Pedir al MODELO que calcule los escenarios configurados ------------------
    resultados = evaluar_escenarios(tasa_llegada, tasa_atencion, unidad)

    # --- 4) Pedir a la VISTA que dibuje los gráficos -------------------------
    graficos = generar_graficos(resultados)

    # --- 5) Enviar todo a la plantilla HTML ----------------------------------
    return render_template(
        "index.html",
        formulario=datos_formulario,
        errores=[],
        resultados=resultados,
        graficos=graficos,
        config=config,
    )
