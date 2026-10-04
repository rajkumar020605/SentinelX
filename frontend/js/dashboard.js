const API_URL = "http://127.0.0.1:8000";

const token = localStorage.getItem("sentinelx_token");

if (!token) {
    window.location.href = "login.html";
}


async function loadDashboard() {

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
            logout();
            return;
        }

        if (!response.ok) {
            throw new Error("Failed to load dashboard");
        }

        const data = await response.json();

        console.log("Dashboard data:", data);

        /* =========================
           MAIN COUNTS
        ========================= */

        document.getElementById("totalEvents").textContent =
            data.total_security_events;

        document.getElementById("totalIncidents").textContent =
            data.total_incidents;

        document.getElementById("totalAlerts").textContent =
            data.total_alerts;


        /* =========================
           INCIDENT STATUS
        ========================= */

        const incidentStatus = data.incident_status || {};

        document.getElementById("statusOpen").textContent =
            incidentStatus.open || 0;

        document.getElementById("statusInvestigating").textContent =
            incidentStatus.investigating || 0;

        document.getElementById("statusResolved").textContent =
            incidentStatus.resolved_or_closed || 0;

        document.getElementById("openIncidents").textContent =
            incidentStatus.open || 0;


        /* =========================
           INCIDENT SEVERITY
        ========================= */

        const severity = data.incident_severity || {};

        document.getElementById("criticalCount").textContent =
            severity.critical || 0;

        document.getElementById("highCount").textContent =
            severity.high || 0;

        document.getElementById("mediumCount").textContent =
            severity.medium || 0;

        document.getElementById("lowCount").textContent =
            severity.low || 0;


        /* =========================
           ALERT STATUS
        ========================= */

        const alertStatus = data.alert_status || {};

        document.getElementById("newAlerts").textContent =
            alertStatus.new || 0;

        document.getElementById("ackAlerts").textContent =
            alertStatus.acknowledged || 0;

        document.getElementById("resolvedAlerts").textContent =
            alertStatus.resolved || 0;


        /* =========================
           USER
        ========================= */

        if (data.generated_for) {
            document.getElementById("username").textContent =
                data.generated_for;
        }


        /* =========================
           LAST UPDATED
        ========================= */

        document.getElementById("lastUpdated").textContent =
            "Last updated: " + new Date().toLocaleTimeString();


    } catch (error) {

        console.error("Dashboard error:", error);

        document.getElementById("lastUpdated").textContent =
            "Unable to load dashboard data";
    }
}


/* =========================
   LOGOUT
========================= */

function logout() {

    localStorage.removeItem("sentinelx_token");

    window.location.href = "login.html";
}


/* =========================
   LOAD DASHBOARD
========================= */

loadDashboard();