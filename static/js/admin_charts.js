document.addEventListener("DOMContentLoaded", async () => {
    const chartDefaults = {
        responsive: true,
        plugins: { legend: { labels: { color: "#cbd5e1" } } },
        scales: {
            x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
            y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
        },
    };

    async function fetchChart(url) {
        const res = await fetch(url);
        return res.json();
    }

    const activity = await fetchChart("/admin/api/charts/user-activity");
    new Chart(document.getElementById("activityChart"), {
        type: "line",
        data: {
            labels: activity.labels,
            datasets: [{
                label: "Behavior Events",
                data: activity.values,
                borderColor: "#60a5fa",
                backgroundColor: "rgba(96,165,250,0.15)",
                fill: true,
                tension: 0.35,
            }],
        },
        options: chartDefaults,
    });

    const trust = await fetchChart("/admin/api/charts/trust-distribution");
    new Chart(document.getElementById("trustChart"), {
        type: "bar",
        data: {
            labels: trust.labels,
            datasets: [{
                label: "Users",
                data: trust.values,
                backgroundColor: ["#22c55e", "#3b82f6", "#f59e0b", "#ef4444"],
            }],
        },
        options: chartDefaults,
    });

    const risk = await fetchChart("/admin/api/charts/risk-distribution");
    new Chart(document.getElementById("riskChart"), {
        type: "doughnut",
        data: {
            labels: risk.labels,
            datasets: [{
                data: risk.values,
                backgroundColor: ["#22c55e", "#3b82f6", "#f59e0b", "#ef4444"],
            }],
        },
        options: { responsive: true, plugins: { legend: { labels: { color: "#cbd5e1" } } } },
    });

    const pred = await fetchChart("/admin/api/charts/predictions");
    new Chart(document.getElementById("predictionChart"), {
        type: "pie",
        data: {
            labels: pred.labels,
            datasets: [{
                data: pred.values,
                backgroundColor: ["#22c55e", "#ef4444"],
            }],
        },
        options: { responsive: true, plugins: { legend: { labels: { color: "#cbd5e1" } } } },
    });
});
