
const formulario = document.getElementById("formulario");
const campoLambda = document.getElementById("lambda");
const campoMu = document.getElementById("mu");
const pista = document.getElementById("pista-estabilidad");
const errorCliente = document.getElementById("error-cliente");
const botonCalcular = document.getElementById("boton-calcular");
const zonaResultados = document.querySelector(".zona-resultados");
const radiosUnidad = document.querySelectorAll('input[name="unidad"]');
const textosUnidad = document.querySelectorAll("[data-unidad-texto]");
const botonesEjemplo = document.querySelectorAll(".ejemplo");

// Ventanillas que compara la aplicación. Las leemos del atributo
// data-ventanillas="3,4,5" del formulario (viene de config.py).
const VENTANILLAS = formulario.dataset.ventanillas.split(",").map(Number);



function leerNumero(campo) {

    const texto = campo.value.trim().replace(",", ".");

    if (texto === "") {
        return NaN;
    }

    return Number(texto);
}


function unidadActual() {

    const marcado = document.querySelector('input[name="unidad"]:checked');
    return marcado ? marcado.value : "hora";
}


function formatear(numero) {

    return String(Number(numero.toFixed(4)));
}

function actualizarPista() {

    const lambda = leerNumero(campoLambda);
    const mu = leerNumero(campoMu);

    // Si falta algún dato válido, no mostramos nada
    if (!(lambda > 0) || !(mu > 0)) {
        pista.textContent = "";
        pista.classList.remove("pista-alerta");
        return;
    }

    // Carga del sistema: cuántas ventanillas estarían ocupadas en promedio
    const carga = lambda / mu;

    // Mínimo de ventanillas para que ρ = carga / c sea menor que 1
    const minimo = Math.floor(carga) + 1;

    // ¿Cuáles de los escenarios comparados serían inestables?
    const inestables = VENTANILLAS.filter(function (c) {
        return carga / c >= 1;
    });

    if (inestables.length === 0) {
        pista.classList.remove("pista-alerta");
        pista.innerHTML =
            "Carga λ/μ = <strong>" + formatear(carga) + "</strong>. " +
            "Los " + VENTANILLAS.length + " escenarios son estables.";
    } else {
        pista.classList.add("pista-alerta");
        pista.innerHTML =
            "Carga λ/μ = <strong>" + formatear(carga) + "</strong>. " +
            "Se necesitan al menos " + minimo + " ventanillas; con " +
            inestables.join(" y ") + " la fila crecería sin límite.";
    }
}

// Se ejecuta cada vez que el usuario escribe algo
campoLambda.addEventListener("input", actualizarPista);
campoMu.addEventListener("input", actualizarPista);



let unidadAnterior = unidadActual();

radiosUnidad.forEach(function (radio) {

    radio.addEventListener("change", function () {

        const nuevaUnidad = unidadActual();
        const factor = (unidadAnterior === "hora" && nuevaUnidad === "minuto") ? 1 / 60 : 60;

        // Convertimos solo si hay un número válido escrito
        [campoLambda, campoMu].forEach(function (campo) {
            const valor = leerNumero(campo);
            if (valor > 0) {
                campo.value = formatear(valor * factor);
            }
        });

        // Actualizamos el texto "estudiantes / hora" junto a cada caja
        textosUnidad.forEach(function (texto) {
            texto.textContent = "estudiantes / " + nuevaUnidad;
        });

        unidadAnterior = nuevaUnidad;
        actualizarPista();
    });
});



botonesEjemplo.forEach(function (boton) {

    boton.addEventListener("click", function () {

        // Marcamos la unidad del ejemplo
        const unidad = boton.dataset.unidad;
        document.querySelector('input[name="unidad"][value="' + unidad + '"]').checked = true;
        unidadAnterior = unidad;

        textosUnidad.forEach(function (texto) {
            texto.textContent = "estudiantes / " + unidad;
        });

        // Escribimos los valores y calculamos de inmediato
        campoLambda.value = boton.dataset.lambda;
        campoMu.value = boton.dataset.mu;

        actualizarPista();
        formulario.requestSubmit();
    });
});



formulario.addEventListener("submit", function (evento) {

    const errores = [];

    // Limpiamos marcas de error anteriores
    campoLambda.removeAttribute("aria-invalid");
    campoMu.removeAttribute("aria-invalid");

    if (!(leerNumero(campoLambda) > 0)) {
        errores.push("Escribe una tasa de llegada λ mayor que cero.");
        campoLambda.setAttribute("aria-invalid", "true");
    }

    if (!(leerNumero(campoMu) > 0)) {
        errores.push("Escribe una tasa de atención μ mayor que cero.");
        campoMu.setAttribute("aria-invalid", "true");
    }

    // Si hay errores, detenemos el envío y los mostramos
    if (errores.length > 0) {
        evento.preventDefault();
        errorCliente.textContent = errores.join(" ");
        errorCliente.hidden = false;
        return;
    }

    errorCliente.hidden = true;

    // Normalizamos la coma decimal a punto antes de enviar
    campoLambda.value = String(leerNumero(campoLambda));
    campoMu.value = String(leerNumero(campoMu));

    // La simulación tarda un momento: avisamos al usuario
    botonCalcular.disabled = true;
    botonCalcular.textContent = "Calculando…";

    if (zonaResultados) {
        zonaResultados.setAttribute("aria-busy", "true");
    }
});


window.addEventListener("pageshow", function () {

    botonCalcular.disabled = false;
    botonCalcular.textContent = "Calcular escenarios";

    if (zonaResultados) {
        zonaResultados.removeAttribute("aria-busy");
    }
});


// Mostramos la pista apenas carga la página
actualizarPista();
