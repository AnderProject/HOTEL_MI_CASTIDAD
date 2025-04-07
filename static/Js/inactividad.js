// inactividad.js
// Temporizador para la inactividad
var idleTime = 0;

// Incrementar el contador de inactividad cada 60 segundos (1 minuto)
var idleInterval = setInterval(timerIncrement, 60000); // 1 minuto = 60000 ms

// Resetea el contador con cualquier evento de actividad del usuario
document.onmousemove = resetTimer;
document.onkeypress = resetTimer;
document.onclick = resetTimer;

function timerIncrement() {
    idleTime += 1;  // Incrementar el contador de minutos
    if (idleTime >= 5) {  // Si el contador alcanza los 5 minutos
        // Redirigir a la URL de cierre de sesión
        window.location.href = logoutUrl;
    }
}

function resetTimer() {
    idleTime = 0;  // Resetea el contador de inactividad
}
