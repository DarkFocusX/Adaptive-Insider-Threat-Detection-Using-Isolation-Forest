document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("bankingForm");
    const modalEl = document.getElementById("confirmModal");

    if (form && modalEl) {
        const modal = new bootstrap.Modal(modalEl);
        const confirmBtn = document.getElementById("confirmModalBtn");
        const titleEl = document.getElementById("confirmModalTitle");
        const bodyEl = document.getElementById("confirmModalBody");
        let confirmed = false;

        form.addEventListener("submit", (e) => {
            if (confirmed) return;
            e.preventDefault();
            titleEl.textContent = form.dataset.confirmTitle || "Confirm Action";
            bodyEl.textContent = form.dataset.confirmBody || "Are you sure you want to continue?";
            modal.show();
        });

        confirmBtn.addEventListener("click", () => {
            confirmed = true;
            modal.hide();
            form.submit();
        });
    }

    const accountInput = document.getElementById("receiverAccount");
    const nameInput = document.getElementById("receiverName");

    if (accountInput && nameInput) {
        accountInput.addEventListener("blur", async () => {
            const account = accountInput.value.trim();
            if (account.length < 8) return;
            try {
                const res = await fetch(`/api/lookup-account/${account}`);
                const data = await res.json();
                if (data.success) {
                    nameInput.value = data.name;
                }
            } catch (err) {
                console.error("Account lookup failed", err);
            }
        });
    }
});
