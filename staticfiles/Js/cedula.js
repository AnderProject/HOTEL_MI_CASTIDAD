document.getElementById("cedula_cliente").addEventListener("input", function() {
    const cedula = this.value;
    if (cedula.length === 10) { // Asegúrate de que la cédula tenga 10 dígitos
        fetch(`/buscar_cliente/?cedula=${cedula}`)
            .then(response => response.json())
            .then(data => {
                if (data.existe) {
                    // Autocompletar los campos y bloquearlos
                    document.getElementById("nombre_cliente").value = data.nombre;
                    document.getElementById("apellido_cliente").value = data.apellido;
                    document.getElementById("nombre_cliente").setAttribute("readonly", true);
                    document.getElementById("apellido_cliente").setAttribute("readonly", true);
                } else {
                    // Limpiar los campos y desbloquearlos si el cliente no existe
                    document.getElementById("nombre_cliente").value = '';
                    document.getElementById("apellido_cliente").value = '';
                    document.getElementById("nombre_cliente").removeAttribute("readonly");
                    document.getElementById("apellido_cliente").removeAttribute("readonly");
                }
            })
            .catch(error => console.error('Error:', error));
    } else {
        // Si no hay una cédula completa, limpia y desbloquea los campos
        document.getElementById("nombre_cliente").value = '';
        document.getElementById("apellido_cliente").value = '';
        document.getElementById("nombre_cliente").removeAttribute("readonly");
        document.getElementById("apellido_cliente").removeAttribute("readonly");
    }
});