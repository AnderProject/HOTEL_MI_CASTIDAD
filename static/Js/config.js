// config.js
window.appConfig = {
    createReservaUrl: "{% url 'crear_reserva' %}",
    redirectToListarReservas: "{% url 'listar_reservas' %}",
    csrfToken: "{{ csrf_token }}",
};
