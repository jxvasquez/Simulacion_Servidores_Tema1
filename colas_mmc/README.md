# Simulador de atención estudiantil — Modelo de colas M/M/c

Proyecto académico que permite comparar diferentes cantidades de **ventanillas de atención presencial** en una dependencia universitaria. Utiliza el modelo estocástico de colas **M/M/c**, implementado en **Python y Flask**, y presenta los resultados desde una interfaz web.

El sistema considera una **cola compartida**, estudiantes atendidos por **orden de llegada** y una persona a cargo de cada ventanilla. Compara los resultados **teóricos y simulados** y recomienda la menor cantidad de ventanillas que cumpla la meta de espera establecida.

> **Importante:** los datos iniciales son supuestos académicos. La meta de espera de dos minutos fue definida para este ejercicio y no corresponde a una norma universitaria ni a una medición real.

## 1. Requisitos (solo Linux)

- Ubuntu u otra distribución de Linux con terminal.
- Python **3.10 o superior**.
- Conexión a Internet para instalar las dependencias por primera vez.
- Navegador web (Firefox, Chrome, etc.).

En **Ubuntu**, si faltan las herramientas necesarias, instálalas con:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip unzip git
```

Puedes verificar Python con:

```bash
python3 --version
```

## 2. Descargar o conseguir el proyecto

### Opción A. Desde GitHub

Si el proyecto está publicado en un repositorio, reemplaza `URL_DEL_REPOSITORIO` por su enlace real y ejecuta:

```bash
cd ~/Documentos
git clone URL_DEL_REPOSITORIO colas_mmc
cd colas_mmc
```

**Nota:** `URL_DEL_REPOSITORIO` es un marcador; no es una dirección de descarga. Necesitas el enlace real del proyecto.

### Opción B. Desde el archivo ZIP

Si ya descargaste `colas_mmc_azul_actualizado.zip` en la carpeta `Descargas` de Ubuntu, ejecuta:

```bash
cd ~/Descargas
unzip colas_mmc_azul_actualizado.zip -d colas_mmc_azul_actualizado
cd colas_mmc_azul_actualizado/colas_mmc
```

Si descomprimiste el ZIP desde el explorador de archivos, abre una terminal **dentro de la carpeta `colas_mmc`**, donde se encuentran `app.py`, `config.py` y `requirements.txt`.

## 3. Crear el entorno virtual

Desde la carpeta del proyecto, ejecuta:

```bash
python3 -m venv venv
source venv/bin/activate
```

Si se activó correctamente, verás `(venv)` al comienzo de la terminal. El entorno virtual separa las bibliotecas de este proyecto de las del resto de tu computadora.

## 4. Instalar las dependencias

Con el entorno virtual activado, ejecuta:

```bash
python -m pip install -r requirements.txt
```

Las dependencias principales son **Flask** (servidor web local) y **Matplotlib** (gráficos). Las bibliotecas `math`, `random` y `statistics` vienen con Python.

## 5. Ejecutar el simulador

Desde la carpeta `colas_mmc`, ejecuta:

```bash
python app.py
```

Abre la siguiente dirección en tu navegador:

**http://127.0.0.1:5000**

El servidor corre **localmente** en tu computadora. Para detenerlo, vuelve a la terminal y presiona **Ctrl + C**.

## 6. Cómo volver a abrir el programa otro día

Si guardaste el proyecto en `~/Documentos/colas_mmc_azul_actualizado/colas_mmc`, solo necesitas:

```bash
cd ~/Documentos/colas_mmc_azul_actualizado/colas_mmc
source venv/bin/activate
python app.py
```

No necesitas volver a instalar las dependencias cada vez.

## 7. Cómo utilizar la interfaz

1. Abre la aplicación en el navegador.
2. Introduce la **tasa de llegada (λ)**: estudiantes que llegan por hora o minuto.
3. Introduce la **tasa de atención (μ)**: estudiantes que **una ventanilla** puede atender por hora o minuto.
4. Elige la unidad de tiempo y ejecuta la comparación.
5. Consulta las tablas y las gráficas de los escenarios configurados.
6. Revisa los indicadores: **Wq** (espera promedio), **Lq** (estudiantes promedio en cola) y **ρ** (utilización de las ventanillas).
7. Compara los valores **teóricos** y **simulados**. Pueden diferir ligeramente porque la simulación utiliza números aleatorios.

La recomendación identifica la **menor cantidad de ventanillas que cumple la meta de espera**. No calcula salarios ni demuestra un ahorro económico exacto.

## 8. Configuración centralizada (`config.py`)

Para cambiar los parámetros sin modificar las fórmulas del programa, abre `config.py`:

```python
VENTANILLAS_A_COMPARAR = [3, 4, 5]
META_WQ_MINUTOS = 2.0
LAMBDA_POR_DEFECTO = 24.0
MU_POR_DEFECTO = 10.0
UNIDAD_POR_DEFECTO = "hora"

REPLICAS = 40
ESTUDIANTES_POR_REPLICA = 20000
ESTUDIANTES_CALENTAMIENTO = 2000
SEMILLA = 20261025
```

| Parámetro | Función |
|---|---|
| `VENTANILLAS_A_COMPARAR` | Cantidades de ventanillas que se evaluarán. |
| `META_WQ_MINUTOS` | Espera promedio máxima aceptada, en minutos. |
| `LAMBDA_POR_DEFECTO` | Llegadas promedio por unidad de tiempo. |
| `MU_POR_DEFECTO` | Atenciones promedio por ventanilla y unidad de tiempo. |
| `UNIDAD_POR_DEFECTO` | `"hora"` o `"minuto"`; ambas tasas deben usar la misma unidad. |
| `REPLICAS` | Número de veces que se repite el experimento por escenario. |
| `ESTUDIANTES_POR_REPLICA` | Estudiantes ficticios simulados en cada repetición. |
| `ESTUDIANTES_CALENTAMIENTO` | Primeros estudiantes excluidos de los promedios para reducir el efecto del inicio vacío. |
| `SEMILLA` | Valor que hace reproducibles las secuencias aleatorias. |

**Ejemplo:** si el docente pide comparar 2, 4 y 6 ventanillas, cambia únicamente:

```python
VENTANILLAS_A_COMPARAR = [2, 4, 6]
```

Guarda el archivo, reinicia la aplicación y vuelve a ejecutar la simulación.

## 9. Organización del código (MVC)

```text
colas_mmc/
├── app.py                         Inicia la aplicación Flask
├── config.py                      Parámetros centralizados
├── requirements.txt               Dependencias
├── README.md                      Esta guía
├── models/
│   ├── cola_mmc.py                Cálculos teóricos del modelo M/M/c
│   ├── simulador.py               Cálculos a partir de estudiantes simulados
│   └── escenarios.py              Compara escenarios y elige una recomendación
├── controllers/
│   └── controlador_colas.py       Recibe, valida y envía los datos
├── views/
│   ├── graficos.py                Genera las gráficas
│   ├── templates/
│   │   ├── base.html              Estructura de la página
│   │   └── index.html             Formulario, indicadores y tablas
│   └── static/
│       ├── css/estilos.css        Diseño en tonos azules
│       └── js/app.js              Comportamiento de la interfaz
└── pruebas/
    └── test_modelo.py             Pruebas automáticas
```

**Flujo del sistema:** el usuario ingresa los datos → el **controlador** los recibe → el **modelo** calcula y simula → la **vista** presenta los resultados.

## 10. ¿Dónde se calculan los indicadores?

| Archivo | Qué hace |
|---|---|
| `models/cola_mmc.py` | Aplica las **fórmulas teóricas** de M/M/c: utilización, probabilidades, Lq, Wq y otros indicadores. |
| `models/simulador.py` | Genera llegadas y tiempos de atención aleatorios; calcula los **resultados simulados**. |
| `models/escenarios.py` | Reúne resultados teóricos y simulados, compara las ventanillas y selecciona la recomendada. |
| `views/graficos.py` | Convierte resultados en gráficas. |
| `views/templates/index.html` | Presenta la tabla comparativa y el resto de la interfaz. |

El código utiliza una **cola compartida** con atención por orden de llegada. En el modelo M/M/c, una “ventanilla” es un puesto físico atendido por una persona; **no es un servidor informático**.

## 11. Ejecutar las pruebas del modelo

Con el entorno virtual activado y desde la carpeta del proyecto:

```bash
python -m unittest discover -s pruebas -v
```

Las pruebas ayudan a detectar errores en cálculos, escenarios y recomendaciones.

## 12. Problemas frecuentes en Ubuntu

**`venv/bin/activate: No such file or directory`**

Asegúrate de estar en la carpeta que contiene `app.py` y crea el entorno:

```bash
python3 -m venv venv
source venv/bin/activate
```

**`No module named 'flask'`**

Activa el entorno e instala las dependencias:

```bash
source venv/bin/activate
python -m pip install -r requirements.txt
```

**`ensurepip is not available`**

```bash
sudo apt install python3-venv
python3 -m venv venv
```

**`NameError: name 'math' is not defined`**

Comprueba que el archivo `models/cola_mmc.py` tenga `import math` al inicio, fuera de las clases y las funciones.

**El puerto 5000 ya está ocupado**

Detén otra ejecución del programa con **Ctrl + C** o modifica `PUERTO` en `config.py` y utiliza la nueva dirección indicada en la terminal.

## 13. Consideraciones del proyecto

- Los datos iniciales de **24 llegadas/hora** y **10 atenciones/hora por ventanilla** son supuestos académicos.
- Se comparan **3, 4 y 5 ventanillas** con una meta de espera de **2 minutos**.
- Cada repetición simula **20 000 estudiantes ficticios**, pero los **2 000 primeros** no se incluyen en las mediciones finales.
- Las **40 repeticiones** permiten obtener promedios menos dependientes de una sola secuencia aleatoria.
- Los resultados pueden variar si cambias la semilla o el número de repeticiones.
- No se recomienda utilizar los resultados para modificar el personal de una universidad real sin recopilar y comprobar antes los datos de atención.
