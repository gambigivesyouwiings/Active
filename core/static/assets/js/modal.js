document.addEventListener('htmx:afterRequest', function (event) {
    let url = event.target.getAttribute('data-url'); // Get URL from button attribute
    if (url && url.includes('confirm-delete-user')) {
        setTimeout(function () {
            let modal = new bootstrap.Modal(document.getElementById('delete-modal'));
            modal.show();
        }, 500); // Delay of 500ms
    }
});