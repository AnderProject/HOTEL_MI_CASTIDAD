function startCountdown(endTime, elementId) {
    const countDownDate = new Date(endTime).getTime();

    const countdownInterval = setInterval(function() {
        const now = new Date().getTime();
        const distance = countDownDate - now;

        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        if (distance < 0) {
            clearInterval(countdownInterval);
            document.getElementById(elementId).innerHTML = "Finalizado";
        } else {
            document.getElementById(elementId).innerHTML = hours + "h " + minutes + "m " + seconds + "s ";
        }
    }, 1000);
}

// Esta función inicializa los contadores para todas las reservas
function initCountdowns(reservas) {
    reservas.forEach(function(reserva) {
        const endTime = reserva.endTime;
        const elementId = "contador-" + reserva.id;
        startCountdown(endTime, elementId);
    });
}

