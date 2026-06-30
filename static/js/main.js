document.addEventListener("DOMContentLoaded", () => {
    if (typeof AOS !== "undefined") {
        AOS.init({ duration: 700, once: true });
    }

    document.querySelectorAll("form").forEach((form) => {
        form.addEventListener("submit", () => {
            const btn = form.querySelector('button[type="submit"]');
            if (!btn) return;
            const spinner = btn.querySelector(".spinner-border");
            const text = btn.querySelector(".btn-text");
            if (spinner && text) {
                spinner.classList.remove("d-none");
                text.classList.add("d-none");
                btn.disabled = true;
            }
        });
    });

    setTimeout(() => {
        document.querySelectorAll(".toast").forEach((toast) => {
            toast.classList.remove("show");
        });
    }, 4000);
});
