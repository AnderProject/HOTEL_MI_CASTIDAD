document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const modal = document.getElementById('customModal');
    const closeModalButton = document.getElementById('close-modal-button');
    const closeButton = document.querySelector('.close-button-custom');

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevenir el comportamiento predeterminado del formulario
        
        const formData = new FormData(form);
        fetch(window.createReservaUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': window.csrfToken,
            }
        })
        .then(response => {
            if (response.ok) {
                // Mostrar el modal cuando la reserva se crea
                modal.style.display = 'block';
            }
        })
        .catch(error => console.error('Error al crear la reserva:', error));
    });

    // Cerrar el modal cuando se hace clic en el botón Aceptar y redirigir a la página de listar reservas
    closeModalButton.onclick = function() {
        window.location.href = window.redirectToListarReservas; // Aquí rediriges a la URL de la lista de reservas
    };

    // Cerrar el modal cuando se hace clic en la "X" y redirigir a la página de listar reservas
    closeButton.onclick = function() {
        window.location.href = window.redirectToListarReservas;
    };

    // Cerrar el modal si el usuario hace clic fuera del modal
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    };
});
