

import math

import config
from models.cola_mmc import ColaMMc
from models.simulador import simular_escenario


# -----------------------------------------------------------------------------
#  Conversión de unidades
# -----------------------------------------------------------------------------
def convertir_a_por_minuto(tasa, unidad):
 
    if unidad == "hora":
        return tasa / 60.0

    return tasa


# -----------------------------------------------------------------------------
#  Ventanillas mínimas para que la fila no crezca sin límite
# -----------------------------------------------------------------------------
def ventanillas_minimas_estables(lam, mu):
    """
    Se necesita  c > λ / μ  para que ρ < 1.
    Ejemplo: λ/μ = 2.5  ->  se necesitan al menos 3 ventanillas.
    """
    carga = lam / mu
    return math.floor(carga) + 1


# -----------------------------------------------------------------------------
#  Función principal: evalúa todos los escenarios
# -----------------------------------------------------------------------------
def evaluar_escenarios(tasa_llegada, tasa_atencion, unidad):
    """
    Recibe los datos tal como los escribió el usuario y devuelve un
    diccionario con todo lo necesario para mostrar la página.
    """

    # --- 1) Pasamos las tasas a "por minuto"
    lam = convertir_a_por_minuto(tasa_llegada, unidad)
    mu = convertir_a_por_minuto(tasa_atencion, unidad)

    # --- 2) Evaluamos cada escenario de la lista de configuración
    lista_escenarios = []

    for c in config.VENTANILLAS_A_COMPARAR:

        # 2a) Resultados teóricos (fórmulas exactas)
        cola = ColaMMc(lam, mu, c)
        resultado = cola.resumen()


        if resultado["estable"]:
            resultado["simulacion"] = simular_escenario(
                lam,
                mu,
                c,
                replicas=config.REPLICAS,
                n_estudiantes=config.ESTUDIANTES_POR_REPLICA,
                n_calentamiento=config.ESTUDIANTES_CALENTAMIENTO,
                semilla=config.SEMILLA,
            )
        else:
            resultado["simulacion"] = None

        # 2c) ¿Cumple la meta de espera?
        resultado["cumple_meta"] = (
            resultado["estable"] and resultado["wq"] <= config.META_WQ_MINUTOS
        )

        # 2d) Se marca más adelante si es la configuración recomendada
        resultado["recomendado"] = False

        lista_escenarios.append(resultado)


    candidatos = [e for e in lista_escenarios if e["cumple_meta"]]
    recomendado = min(candidatos, key=lambda e: e["ventanillas"], default=None)
    if recomendado is not None:
        recomendado["recomendado"] = True

    # --- 4) Devolvemos todo junto
    return {
        "lam_min": lam,
        "mu_min": mu,
        "carga": lam / mu,
        "minimo_estable": ventanillas_minimas_estables(lam, mu),
        "escenarios": lista_escenarios,
        "recomendado": recomendado,
        "cumplen": [e["ventanillas"] for e in lista_escenarios if e["cumple_meta"]],
        "meta": config.META_WQ_MINUTOS,
    }
