document.addEventListener('DOMContentLoaded', function () {
    var closeBtn = document.getElementById('close-btn');
    if (closeBtn) {
        closeBtn.addEventListener('click', async function () {
            try { await pywebview.api.close_app(); } catch (e) { window.location.href = '/'; }
        });
    }
});

document.addEventListener('contextmenu', function (e) { e.preventDefault(); });
