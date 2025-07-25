// Fichier JavaScript pour la recherche et les notifications dans la gestion utilisateurs

document.addEventListener('DOMContentLoaded', function() {
    // Filtrage dynamique des utilisateurs
    const searchInput = document.getElementById('user-search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const filter = searchInput.value.toLowerCase();
            document.querySelectorAll('tbody[data-user-list] tr').forEach(function(row) {
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    }

    // Notification toast auto-hide
    const toast = document.getElementById('toast-message');
    if (toast) {
        setTimeout(() => toast.classList.add('opacity-0', 'pointer-events-none'), 3500);
    }
});
