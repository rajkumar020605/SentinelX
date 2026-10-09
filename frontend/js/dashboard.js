
const API_URL = "https://sentinelx-csdo.onrender.com";

let severityChartInstance = null;
let incidentStatusChartInstance = null;
let securityEventsTrendChart = null;

// =====================================
// LOAD DASHBOARD
// =====================================

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

        const dashboard = data.dashboard || {};
        const severity = data.incident_severity || {};
        const status = data.incident_status || {};
        const alerts = data.alert_status || {};

        // Main dashboard counts
        setText("totalEvents", dashboard.total_security_events);
        setText("totalIncidents", dashboard.total_incidents);
        setText("totalAlerts", dashboard.total_alerts);
        setText("openIncidents", status.open);

        // Incident status
        setText("incidentOpen", status.open);
        setText("incidentInvestigating", status.investigating);
        setText("incidentResolved", status.resolved_or_closed);

        // Incident severity
        setText("criticalIncidents", severity.critical);
        setText("highIncidents", severity.high);
        setText("mediumIncidents", severity.medium);
        setText("lowIncidents", severity.low);

        // Alert status
        setText("newAlerts", alerts.new);
        setText("acknowledgedAlerts", alerts.acknowledged);
        setText("resolvedAlerts", alerts.resolved);

        // Risk overview
        setText("criticalSummary", severity.critical);
        setText("highSummary", severity.high);
        setText("openSummary", status.open);
        setText("newAlertSummary", alerts.new);

        // Update existing charts
        updateDashboardCharts(data);

        // Recent activity
        renderRecentActivity(data.recent_events || []);

        // Historical events trend
        await loadHistoricalSecurityEventsTrend(token);

        // API status
        if (apiStatus) {
            apiStatus.textContent = "SentinelX API - Online";
            apiStatus.className = "api-online";
        }

        // Last updated
        const updated = document.getElementById("lastUpdated");

        if (updated) {
            updated.textContent =
                "Last updated: " + new Date().toLocaleString();
        }

    } catch (error) {
        console.error("Dashboard error:", error);

        if (apiStatus) {
            apiStatus.textContent = "SentinelX API - Error";
            apiStatus.className = "api-offline";
        }
    }
}

// =====================================
// INCIDENT SEVERITY AND STATUS CHARTS
// =====================================

function updateDashboardCharts(data) {
    if (typeof Chart === "undefined") {
        console.error("Chart.js is not loaded.");
        return;
    }

    const severity = data.incident_severity || {};
    const status = data.incident_status || {};

    const severityCanvas = document.getElementById("severityChart");
    const statusCanvas = document.getElementById("incidentStatusChart");

    // Severity bar chart
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
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { precision: 0 }
                    }
                }
            }
        });
    }

    // Incident status doughnut chart
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
                    }
                }
            }
        });
    }
}

// =====================================
// HISTORICAL SECURITY EVENTS
// =====================================

async function loadHistoricalSecurityEventsTrend(token) {
    const canvas = document.getElementById("securityEventsTrendChart");

    if (!canvas) {
        console.warn(
            "Trend chart canvas is missing from dashboard.html."
        );
        return;
    }

    if (typeof Chart === "undefined") {
        console.error("Chart.js is not loaded.");
        return;
    }

    try {
        const allEvents = [];
        const pageSize = 100;
        let page = 1;
        const maxPages = 1000;

        while (page <= maxPages) {
            const url = new URL(`${API_URL}/security-events/`);
            url.searchParams.set("page", String(page));
            url.searchParams.set("page_size", String(pageSize));

            const response = await fetch(url, {
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
                throw new Error(
                    `Security events API failed: ${response.status}`
                );
            }

            const result = await response.json();

            // Support a direct array or common paginated formats.
            const events = Array.isArray(result)
                ? result
                : Array.isArray(result.items)
                    ? result.items
                    : Array.isArray(result.events)
                        ? result.events
                        : Array.isArray(result.results)
                            ? result.results
                            : null;

            if (!events) {
                throw new Error(
                    "Unexpected security-events response format."
                );
            }

            allEvents.push(...events);

            if (events.length < pageSize) {
                break;
            }

            page++;
        }

        if (page > maxPages) {
            console.warn("Stopped pagination at the safety limit.");
        }

        renderSecurityEventsTrend(allEvents);

        console.log(
            `Trend chart processed ${allEvents.length} security events.`
        );

    } catch (error) {
        console.error("Security events trend error:", error);
    }
}

// =====================================
// RENDER LAST 30 DAYS TREND CHART
// =====================================

function renderSecurityEventsTrend(events) {
    const canvas = document.getElementById("securityEventsTrendChart");

    if (!canvas || typeof Chart === "undefined") {
        return;
    }

    const dailyCounts = {};

    // Count events by their creation date.
    events.forEach(event => {
        const rawDate =
            event.created_at ||
            event.timestamp ||
            event.event_time ||
            event.createdAt;

        if (!rawDate) {
            return;
        }

        const date = new Date(rawDate);

        if (Number.isNaN(date.getTime())) {
            return;
        }

        // Use the local calendar date.
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        const dateKey = `${year}-${month}-${day}`;

        dailyCounts[dateKey] = (dailyCounts[dateKey] || 0) + 1;
    });

    // Prepare the last 30 calendar days, including zero-event days.
    const labels = [];
    const values = [];
    const today = new Date();

    for (let offset = 29; offset >= 0; offset--) {
        const date = new Date(
            today.getFullYear(),
            today.getMonth(),
            today.getDate() - offset
        );

        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        const dateKey = `${year}-${month}-${day}`;

        labels.push(
            date.toLocaleDateString(undefined, {
                month: "short",
                day: "numeric"
            })
        );

        values.push(dailyCounts[dateKey] || 0);
    }

    if (securityEventsTrendChart) {
        securityEventsTrendChart.destroy();
    }

    securityEventsTrendChart = new Chart(canvas, {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: "Security Events",
                data: values,
                borderColor: "#2563eb",
                backgroundColor: "rgba(37, 99, 235, 0.15)",
                fill: true,
                tension: 0.3,
                pointRadius: 3,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: "index"
            },
            plugins: {
                legend: {
                    display: true,
                    position: "top"
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
                    },
                    title: {
                        display: true,
                        text: "Number of Events"
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: "Date"
                    },
                    ticks: {
                        maxTicksLimit: 10
                    }
                }
            }
        }
    });
}

// =====================================
// RECENT SECURITY ACTIVITY TABLE
// =====================================

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

// =====================================
// HELPER
// =====================================

function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value ?? 0;
    }
}

// =====================================
// START DASHBOARD
// =====================================

// Automatically load dashboard when the page opens
document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
});

// Refresh dashboard data every 30 seconds
const DASHBOARD_REFRESH_INTERVAL = 30000;

let dashboardRefreshTimer = null;

function startDashboardAutoRefresh() {
    if (dashboardRefreshTimer) {
        clearInterval(dashboardRefreshTimer);
    }

    dashboardRefreshTimer = setInterval(() => {
        if (!document.hidden) {
            loadDashboard();
        }
    }, DASHBOARD_REFRESH_INTERVAL);
}

// Start automatic refresh
startDashboardAutoRefresh();

// Stop timer when the page is being unloaded
window.addEventListener("beforeunload", () => {
    if (dashboardRefreshTimer) {
        clearInterval(dashboardRefreshTimer);
    }
});