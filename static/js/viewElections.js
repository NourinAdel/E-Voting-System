document.addEventListener("DOMContentLoaded", () => {
    const dialog = document.getElementById("modal");
    const logoutBtn = document.getElementById("logoutBtn");
    const yesBtn = document.getElementById("yesBtn");
    const noBtn = document.getElementById("noBtn");

    if (logoutBtn && dialog) {
        logoutBtn.addEventListener("click", async () => {
            dialog.showModal();
        });

        yesBtn.addEventListener("click", async () => {
            try {
                const response = await fetch('/logout', {
                method: 'POST'
            });

            if (response.ok) {
                window.location.href = '/login';
            } 
            else {
                alert('Logout failed. Please try again.');
            }
            } catch (error) {
                console.error('Logout error:', error);
                window.location.href = '/logout';
            }

        });

        noBtn.addEventListener("click", () => {
            dialog.close();
        });
    }
});
