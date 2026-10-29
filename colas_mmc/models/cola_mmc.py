

import math
class ColaMMc:
    """
    Representa UNA configuración del sistema: una tasa de llegada,
    una tasa de atención y un número fijo de ventanillas.

    Todas las tasas deben estar en la MISMA unidad de tiempo.
    En esta aplicación siempre usamos "estudiantes por MINUTO",
    así los tiempos (Wq, W) salen directamente en minutos.
    """

    # -------------------------------------------------------------------------
    #  Constructor: guarda los datos de entrada
    # -------------------------------------------------------------------------
    def __init__(self, tasa_llegada, tasa_atencion, ventanillas):

        # λ: cuántos estudiantes llegan, en promedio, por minuto
        self.lam = tasa_llegada

        # μ: cuántos estudiantes atiende UNA ventanilla, en promedio, por minuto
        self.mu = tasa_atencion

        # c: número de ventanillas abiertas
        self.c = ventanillas

        # "a" es la carga ofrecida (también llamada intensidad de tráfico).
        # Indica cuántas ventanillas estarían ocupadas en promedio.
        #   a = λ / μ
        self.a = self.lam / self.mu

    # -------------------------------------------------------------------------
    #  ρ (rho): utilización de las ventanillas
    # -------------------------------------------------------------------------
    def utilizacion(self):
        """
        ρ = λ / (c · μ)

        Es la fracción del tiempo que cada ventanilla pasa ocupada.
        Ejemplo: ρ = 0.80 significa que cada ventanilla trabaja el 80 %
        del tiempo y está libre el 20 %.
        """
        return self.lam / (self.c * self.mu)

    # -------------------------------------------------------------------------
    #  ¿El sistema es estable?
    # -------------------------------------------------------------------------
    def es_estable(self):
        """
        Si llegan más estudiantes de los que se pueden atender (ρ >= 1),
        la fila crece sin límite y las fórmulas dejan de tener sentido.
        Por eso SIEMPRE revisamos esto antes de calcular lo demás.
        """
        return self.utilizacion() < 1

    # -------------------------------------------------------------------------
    #  P0: probabilidad de que el sistema esté vacío
    # -------------------------------------------------------------------------
    def probabilidad_vacio(self):
        """
        P0 = 1 / [  Σ (n = 0 hasta c-1) de  a^n / n!   +   a^c / ( c! · (1 - ρ) )  ]

        Es la probabilidad de que NO haya ningún estudiante en el sistema
        (nadie en la fila y todas las ventanillas libres).
        """

        # Si el sistema es inestable, a la larga nunca queda vacío.
        if not self.es_estable():
            return 0.0

        rho = self.utilizacion()

        # --- Primera parte de la suma: estados con menos estudiantes que
        #     ventanillas (n = 0, 1, ..., c-1). Nadie espera en fila.
        suma = 0.0
        for n in range(self.c):
            suma = suma + (self.a ** n) / math.factorial(n)

        # --- Segunda parte: todos los estados con c o más estudiantes
        #     (todas las ventanillas ocupadas). Es una serie geométrica
        #     que ya viene sumada en esta expresión.
        ultimo_termino = (self.a ** self.c) / (math.factorial(self.c) * (1 - rho))

        # --- P0 es el inverso de la suma total
        return 1.0 / (suma + ultimo_termino)

    # -------------------------------------------------------------------------
    #  Probabilidad de que un estudiante tenga que esperar (Erlang C)
    # -------------------------------------------------------------------------
    def probabilidad_esperar(self):
        """
        Pw = [ a^c / ( c! · (1 - ρ) ) ] · P0

        Probabilidad de que, al llegar, el estudiante encuentre TODAS
        las ventanillas ocupadas y tenga que hacer fila.
        """
        if not self.es_estable():
            return 1.0

        rho = self.utilizacion()
        p0 = self.probabilidad_vacio()

        return (self.a ** self.c) / (math.factorial(self.c) * (1 - rho)) * p0

    # -------------------------------------------------------------------------
    #  Lq: cantidad promedio de estudiantes esperando en la fila
    # -------------------------------------------------------------------------
    def estudiantes_en_fila(self):
        """
        Lq = P0 · a^c · ρ / ( c! · (1 - ρ)² )

        No cuenta a quienes ya están siendo atendidos en una ventanilla,
        solo a quienes esperan su turno.
        """
        if not self.es_estable():
            return math.inf     # "infinito": la fila crece sin control

        rho = self.utilizacion()
        p0 = self.probabilidad_vacio()

        numerador = p0 * (self.a ** self.c) * rho
        denominador = math.factorial(self.c) * (1 - rho) ** 2

        return numerador / denominador

    # -------------------------------------------------------------------------
    #  Wq: tiempo promedio de espera en la fila
    # -------------------------------------------------------------------------
    def tiempo_en_fila(self):
        """
        Wq = Lq / λ      (Ley de Little)

        Como λ está en estudiantes por minuto, Wq queda en MINUTOS.
        """
        if not self.es_estable():
            return math.inf

        return self.estudiantes_en_fila() / self.lam

    # -------------------------------------------------------------------------
    #  W: tiempo promedio total dentro del sistema (fila + atención)
    # -------------------------------------------------------------------------
    def tiempo_en_sistema(self):
        """
        W = Wq + 1/μ

        1/μ es el tiempo promedio que dura la atención en la ventanilla.
        """
        if not self.es_estable():
            return math.inf

        return self.tiempo_en_fila() + 1.0 / self.mu

    # -------------------------------------------------------------------------
    #  L: cantidad promedio de estudiantes en todo el sistema
    # -------------------------------------------------------------------------
    def estudiantes_en_sistema(self):
        """
        L = λ · W      (otra vez la Ley de Little)
        """
        if not self.es_estable():
            return math.inf

        return self.lam * self.tiempo_en_sistema()

    # -------------------------------------------------------------------------
    #  Resumen: todos los indicadores en un diccionario
    # -------------------------------------------------------------------------
    def resumen(self):
        """
        Devuelve un diccionario con todos los resultados.
        Un diccionario es cómodo para enviarlo luego a la vista (HTML).
        """
        return {
            "ventanillas": self.c,
            "estable": self.es_estable(),
            "rho": self.utilizacion(),
            "p0": self.probabilidad_vacio(),
            "pw": self.probabilidad_esperar(),
            "lq": self.estudiantes_en_fila(),
            "wq": self.tiempo_en_fila(),
            "l": self.estudiantes_en_sistema(),
            "w": self.tiempo_en_sistema(),
        }
