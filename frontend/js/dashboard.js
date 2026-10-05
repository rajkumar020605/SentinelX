const API_URL = "https://sentinelx-csdo.onrender.com";

async function loadDashboard() {

    const token = localStorage.getItem("sentinelx_token");

    if (!token) {
        window.location.href = "login.html";
        return;
    }

    try {

        const response = await fetch(
            `${API_URL}/dashboard/summary`,
            {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (response.status === 401) {
            localStorage.removeItem("sentinelx_token");
            window.location.href = "login.html";
            return;
        }

        if (!response.ok) {
            throw new Error("Failed to load dashboard");
        }

        const data = await response.json();

        console.log("Dashboard data:", data);

        // =========================
        // MAIN DASHBOARD COUNTS
        // =========================

        setText(
            "totalEvents",
            data.dashboard.total_security_events
        );

        setText(
            "totalIncidents",
            data.dashboard.total_incidents
        );

        setText(
            "totalAlerts",
            data.dashboard.total_alerts
        );


        // =========================
        // OPEN INCIDENTS
        // =========================

        setText(
            "openIncidents",
            data.incident_status.open || 0
        );


        // =========================
        // INCIDENT STATUS
        // =========================

        setText(
            "incidentOpen",
            data.incident_status.open || 0
        );

        setText(
            "incidentInvestigating",
            data.incident_status.investigating || 0
        );

        setText(
            "incidentResolved",
            data.incident_status.resolved_or_closed || 0
        );


        // =========================
        // INCIDENT SEVERITY
        // =========================

        setText(
            "criticalIncidents",
            data.incident_severity.critical || 0
        );

        setText(
            "highIncidents",
            data.incident_severity.high || 0
        );

        setText(
            "mediumIncidents",
            data.incident_severity.medium || 0
        );

        setText(
            "lowIncidents",
            data.incident_severity.low || 0
        );


        // =========================
        // ALERT STATUS
        // =========================

        setText(
            "newAlerts",
            data.alert_status.new || 0
        );

        setText(
            "acknowledgedAlerts",
            data.alert_status.acknowledged || 0
        );

        setText(
            "resolvedAlerts",
            data.alert_status.resolved || 0
        );

setText(
    "criticalSummary",
    data.incident_severity.critical || 0
);

setText(
    "highSummary",
    data.incident_severity.high || 0
);

setText(
    "openSummary",
    data.incident_status.open || 0
);

setText(
    "newAlertSummary",
    data.alert_status.new || 0
);


// Recent security activity

const activityBody =
    document.getElementById("recentActivityBody");

if (activityBody) {

    activityBody.innerHTML = "";

    const events = data.recent_events || [];

    events.slice(0, 10).forEach(event => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${event.event_type || "-"}</td>
            <td>${event.source_ip || "-"}</td>
            <td>${event.severity || "-"}</td>
            <td>${event.status || "-"}</td>
        `;

        activityBody.appendChild(row);
    });
}

        // =========================
        // API STATUS
        // =========================

        setText(
            "apiStatus",
            "SentinelX API"
        );

        const updated = document.getElementById(
            "lastUpdated"
        );

        if (updated) {
            updated.textContent =
                "Last updated: " +
                new Date().toLocaleTimeString();
        }

    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );

        const status =
            document.getElementById("apiStatus");

        if (status) {
            status.textContent =
                "SentinelX API - Offline";
        }
    }
}


// =========================
// HELPER
// =========================

function setText(id, value) {

    const element =
        document.getElementById(id);

    if (element) {
        element.textContent =
            value ?? 0;
    }
}


// =========================
// LOAD DASHBOARD
// =========================

document.addEventListener(
    "DOMContentLoaded",
    loadDashboard
);
