

from flask import Flask

import config
from controllers.controlador_colas import controlador


def crear_aplicacion():
    """
    Crea el objeto Flask indicando dónde están las plantillas HTML
    y los archivos estáticos (CSS y JS). Por defecto Flask los busca
    en "templates/" y "static/", pero nosotros los guardamos dentro
    de "views/" para respetar el patrón MVC.
    """
    aplicacion = Flask(
        __name__,
        template_folder="views/templates",
        static_folder="views/static",
    )

    # Registramos el controlador (el grupo de rutas definido en el Blueprint)
    aplicacion.register_blueprint(controlador)

    return aplicacion

app = crear_aplicacion()

if __name__ == "__main__":

    print()
    print("  Simulador de atención estudiantil M/M/c")
    print(f"  Abre en tu navegador:  http://{config.HOST}:{config.PUERTO}")
    print("  Para detener el servidor presiona  Ctrl + C")
    print()

    app.run(host=config.HOST, port=config.PUERTO, debug=config.MODO_DEBUG)
