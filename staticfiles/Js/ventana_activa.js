function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden');
    });
    document.getElementById(sectionId).classList.remove('hidden');
    // Almacenar la sección seleccionada en localStorage
    localStorage.setItem('activeTab', sectionId);
}

// Recuperar la pestaña activa de localStorage al cargar la página
document.addEventListener("DOMContentLoaded", function() {
    const activeTab = localStorage.getItem('activeTab') || 'pendientes';  // Por defecto, se muestra 'pendientes'
    document.getElementById('btn-' + activeTab).click();  // Simula un clic en la pestaña correspondiente
});