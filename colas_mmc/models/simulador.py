

import math
import random
import statistics


# -----------------------------------------------------------------------------
#  1) UNA réplica de la simulación
# -----------------------------------------------------------------------------
def simular_una_replica(lam, mu, c, n_estudiantes, n_calentamiento, generador):
    
  

    # Reloj de la simulación: momento en que llega el estudiante actual.
    reloj = 0.0

    ventanilla_libre_en = [0.0] * c

    # Aquí guardaremos cuánto esperó cada estudiante (después del calentamiento).
    esperas = []

    # Suma del tiempo de atención (para calcular la utilización observada).
    tiempo_total_atendiendo = 0.0

    # Momento en que llega el primer estudiante que sí medimos.
    inicio_medicion = None

    # Momento en que la última ventanilla termina de atender.
    fin_ultima_atencion = 0.0

    # ------------------------------------------------------------------
    #  Recorremos a los estudiantes uno por uno, en orden de llegada.
    # ------------------------------------------------------------------
    for i in range(n_estudiantes):

        # (a) ¿Cuánto tarda en llegar el siguiente estudiante?
        #     expovariate(λ) genera un número aleatorio exponencial
        #     con promedio 1/λ. Eso es exactamente la "M" de llegadas.
        reloj = reloj + generador.expovariate(lam)
        hora_llegada = reloj

        # (b) Buscamos la ventanilla que se desocupa primero.
        #     Como hay una sola fila, el estudiante va a esa ventanilla.
        indice_ventanilla = ventanilla_libre_en.index(min(ventanilla_libre_en))

        # (c) El estudiante empieza a ser atendido cuando:
        #     - él ya llegó, Y
        #     - la ventanilla ya está libre.
        #     Por eso tomamos el MAYOR de los dos instantes.
        inicio_atencion = max(hora_llegada, ventanilla_libre_en[indice_ventanilla])

        # (d) Tiempo de espera en la fila
        espera = inicio_atencion - hora_llegada

        # (e) Duración aleatoria de la atención (la "M" del servicio)
        duracion_atencion = generador.expovariate(mu)

        # (f) La ventanilla quedará ocupada hasta este instante
        fin_atencion = inicio_atencion + duracion_atencion
        ventanilla_libre_en[indice_ventanilla] = fin_atencion

        # (g) Solo medimos después del periodo de calentamiento
        if i >= n_calentamiento:

            if inicio_medicion is None:
                inicio_medicion = hora_llegada

            esperas.append(espera)
            tiempo_total_atendiendo = tiempo_total_atendiendo + duracion_atencion
            fin_ultima_atencion = max(fin_ultima_atencion, fin_atencion)

    # ------------------------------------------------------------------
    #  Cálculo de indicadores de esta réplica
    # ------------------------------------------------------------------

    # Espera promedio en fila: promedio simple de todas las esperas medidas.
    wq_simulado = statistics.mean(esperas)

    # Tasa de llegada que realmente ocurrió en la simulación.
    duracion_llegadas = reloj - inicio_medicion
    lam_observada = (len(esperas) - 1) / duracion_llegadas

    # Ley de Little aplicada a la fila: Lq = λ · Wq
    lq_simulado = lam_observada * wq_simulado

    # Utilización: tiempo total trabajado / tiempo total disponible
    # (c ventanillas abiertas durante todo el periodo medido).
    tiempo_disponible = c * (fin_ultima_atencion - inicio_medicion)
    rho_simulado = tiempo_total_atendiendo / tiempo_disponible

    return {
        "wq": wq_simulado,
        "lq": lq_simulado,
        "rho": rho_simulado,
    }


# -----------------------------------------------------------------------------
#  2) VARIAS réplicas + intervalo de confianza
# -----------------------------------------------------------------------------
def simular_escenario(lam, mu, c, replicas, n_estudiantes, n_calentamiento, semilla):
    """
    Repite la simulación varias veces y resume los resultados.

    ¿Por qué repetir? Porque cada réplica da un número un poco distinto
    (es aleatorio). Promediando muchas réplicas obtenemos un valor más
    confiable y además podemos decir "con 95 % de confianza, el valor
    real está entre A y B".
    """

    # Reiniciamos el generador con la MISMA semilla para cada escenario.
    # Así, al comparar 3, 4 y 5 ventanillas, llegan los mismos estudiantes
    # y cada trámite dura lo mismo. Solo cambia la cantidad de ventanillas.
    generador = random.Random(semilla)

    # Guardamos los resultados de cada réplica en listas separadas.
    lista_wq = []
    lista_lq = []
    lista_rho = []

    for _ in range(replicas):

        resultado = simular_una_replica(
            lam, mu, c, n_estudiantes, n_calentamiento, generador
        )

        lista_wq.append(resultado["wq"])
        lista_lq.append(resultado["lq"])
        lista_rho.append(resultado["rho"])

    # ------------------------------------------------------------------
    #  Intervalo de confianza del 95 % para Wq
    # ------------------------------------------------------------------
    #  Fórmula:  promedio ± z · (desviación estándar / √n)
    #  Con suficientes repeticiones usamos z ≈ 1.96 (distribución normal).
    #  statistics.NormalDist().inv_cdf(0.975) calcula ese 1.96 por nosotros.
    z = statistics.NormalDist().inv_cdf(0.975)

    promedio_wq = statistics.mean(lista_wq)
    desviacion_wq = statistics.stdev(lista_wq)
    margen_error = z * desviacion_wq / math.sqrt(replicas)

    return {
        "wq": promedio_wq,
        "wq_min": promedio_wq - margen_error,
        "wq_max": promedio_wq + margen_error,
        "wq_margen": margen_error,
        "lq": statistics.mean(lista_lq),
        "rho": statistics.mean(lista_rho),
        "replicas": replicas,
        "estudiantes": replicas * (n_estudiantes - n_calentamiento),
    }
