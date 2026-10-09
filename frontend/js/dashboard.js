
const API_URL = "https://sentinelx-csdo.onrender.com";

let severityChartInstance = null;
let incidentStatusChartInstance = null;

// =========================
// LOAD DASHBOARD DATA
// =========================

async function loadDashboard() {
    const token = localStorage.getItem("sentinelx_token");

    if (!token) {
        window.location.href = "login.html";
        return;
    }

    const apiStatus = document.getElementById("apiStatus");

    try {
        const response = await fetch(`${API_URL}/dashboard/summary`, {
            method: "GET",
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            localStorage.removeItem("sentinelx_token");
            window.location.href = "login.html";
            return;
        }

        if (!response.ok) {
            throw new Error(`Dashboard API failed: ${response.status}`);
        }

        const data = await response.json();

        console.log("Dashboard data loaded.");

        const dashboard = data.dashboard || {};
        const severity = data.incident_severity || {};
        const status = data.incident_status || {};
        const alerts = data.alert_status || {};

        // =========================
        // MAIN DASHBOARD COUNTS
        // =========================

        setText("totalEvents", dashboard.total_security_events);
        setText("totalIncidents", dashboard.total_incidents);
        setText("totalAlerts", dashboard.total_alerts);
        setText("openIncidents", status.open);

        // =========================
        // INCIDENT STATUS COUNTS
        // =========================

        setText("incidentOpen", status.open);
        setText("incidentInvestigating", status.investigating);
        setText("incidentResolved", status.resolved_or_closed);

        // =========================
        // INCIDENT SEVERITY COUNTS
        // =========================

        setText("criticalIncidents", severity.critical);
        setText("highIncidents", severity.high);
        setText("mediumIncidents", severity.medium);
        setText("lowIncidents", severity.low);

        // =========================
        // ALERT STATUS COUNTS
        // =========================

        setText("newAlerts", alerts.new);
        setText("acknowledgedAlerts", alerts.acknowledged);
        setText("resolvedAlerts", alerts.resolved);

        // =========================
        // RISK OVERVIEW
        // =========================

        setText("criticalSummary", severity.critical);
        setText("highSummary", severity.high);
        setText("openSummary", status.open);
        setText("newAlertSummary", alerts.new);

        // =========================
        // UPDATE CHARTS
        // =========================

        updateDashboardCharts(data);

        // =========================
        // RECENT SECURITY ACTIVITY
        // =========================

        renderRecentActivity(data.recent_events || []);

        // =========================
        // API STATUS
        // =========================

        if (apiStatus) {
            apiStatus.textContent = "🟢 SentinelX API";
            apiStatus.className = "api-online";
        }

        // =========================
        // LAST UPDATED
        // =========================

        const updated = document.getElementById("lastUpdated");

        if (updated) {
            updated.textContent =
                "Last updated: " + new Date().toLocaleString();
        }

    } catch (error) {
        console.error("Dashboard error:", error);

        if (apiStatus) {
            apiStatus.textContent = "🔴 SentinelX API - Offline";
            apiStatus.className = "api-offline";
        }

        const activityBody =
            document.getElementById("recentActivityBody");

        if (activityBody) {
            activityBody.replaceChildren();

            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 4;
            cell.className = "empty-message";
            cell.textContent = "Unable to load recent activity.";

            row.appendChild(cell);
            activityBody.appendChild(row);
        }
    }
}

// =========================
// UPDATE DASHBOARD CHARTS
// =========================

function updateDashboardCharts(data) {
    if (typeof Chart === "undefined") {
        console.warn(
            "Chart.js is unavailable. Check the Chart.js script in dashboard.html."
        );
        return;
    }

    const severity = data.incident_severity || {};
    const status = data.incident_status || {};

    const severityCanvas = document.getElementById("severityChart");
    const statusCanvas = document.getElementById("incidentStatusChart");

    // =========================
    // INCIDENT SEVERITY BAR CHART
    // =========================

    if (severityCanvas) {
        if (severityChartInstance) {
            severityChartInstance.destroy();
        }

        severityChartInstance = new Chart(severityCanvas, {
            type: "bar",

            data: {
                labels: ["Critical", "High", "Medium", "Low"],

                datasets: [{
                    label: "Incidents",
                    data: [
                        Number(severity.critical) || 0,
                        Number(severity.high) || 0,
                        Number(severity.medium) || 0,
                        Number(severity.low) || 0
                    ],
                    backgroundColor: [
                        "#dc2626",
                        "#ea580c",
                        "#ca8a04",
                        "#16a34a"
                    ],
                    borderRadius: 6,
                    maxBarThickness: 65
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: true
                    }
                },

                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }

    // =========================
    // INCIDENT STATUS DOUGHNUT CHART
    // =========================

    if (statusCanvas) {
        if (incidentStatusChartInstance) {
            incidentStatusChartInstance.destroy();
        }

        incidentStatusChartInstance = new Chart(statusCanvas, {
            type: "doughnut",

            data: {
                labels: [
                    "Open",
                    "Investigating",
                    "Resolved / Closed"
                ],

                datasets: [{
                    label: "Incidents",
                    data: [
                        Number(status.open) || 0,
                        Number(status.investigating) || 0,
                        Number(status.resolved_or_closed) || 0
                    ],
                    backgroundColor: [
                        "#dc2626",
                        "#2563eb",
                        "#16a34a"
                    ],
                    borderColor: "#ffffff",
                    borderWidth: 2,
                    hoverOffset: 8
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "62%",

                plugins: {
                    legend: {
                        display: true,
                        position: "bottom"
                    },
                    tooltip: {
                        enabled: true
                    }
                }
            }
        });
    }
}

// =========================
// RENDER RECENT ACTIVITY SAFELY
// =========================

function renderRecentActivity(events) {
    const activityBody =
        document.getElementById("recentActivityBody");

    if (!activityBody) {
        return;
    }

    activityBody.replaceChildren();

    if (!events.length) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 4;
        cell.className = "empty-message";
        cell.textContent = "No recent security events.";

        row.appendChild(cell);
        activityBody.appendChild(row);
        return;
    }

    events.slice(0, 10).forEach(event => {
        const row = document.createElement("tr");

        const values = [
            event.event_type,
            event.source_ip,
            event.severity,
            event.status
        ];

        values.forEach(value => {
            const cell = document.createElement("td");
            cell.textContent =
                value === null || value === undefined || value === ""
                    ? "-"
                    : String(value);

            row.appendChild(cell);
        });

        activityBody.appendChild(row);
    });
}

// =========================
// HELPER FUNCTION
// =========================

function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value ?? 0;
    }
}

// =========================
// LOAD DASHBOARD
// =========================

document.addEventListener("DOMContentLoaded", loadDashboard);