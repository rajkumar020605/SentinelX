const API_URL = "http://127.0.0.1:8000";

const token =
    localStorage.getItem("sentinelx_token");

if (!token) {
    window.location.href = "login.html";
}


/* =========================
   LOAD REPORT
========================= */

async function loadReport() {

    try {

        console.log(
            "Loading SentinelX report..."
        );


        const response =
            await fetch(
                `${API_URL}/reports/summary`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        console.log(
            "Report response:",
            response.status
        );


        if (response.status === 401) {

            logout();

            return;
        }


        if (!response.ok) {

            throw new Error(
                "Failed to load report"
            );
        }


        const data =
            await response.json();


        console.log(
            "REPORT DATA:",
            data
        );


        /* =========================
           SUMMARY
        ========================= */

        document.getElementById(
            "totalEvents"
        ).textContent =
            data.total_security_events ?? 0;


        document.getElementById(
            "totalIncidents"
        ).textContent =
            data.total_incidents ?? 0;


        document.getElementById(
            "totalAlerts"
        ).textContent =
            data.total_alerts ?? 0;


        /* =========================
           INCIDENT STATUS
        ========================= */

        const incidentStatus =
            data.incident_status || {};


        document.getElementById(
            "openIncidents"
        ).textContent =
            incidentStatus.open ?? 0;


        document.getElementById(
            "investigatingIncidents"
        ).textContent =
            incidentStatus.investigating ?? 0;


        document.getElementById(
            "resolvedIncidents"
        ).textContent =
            data.incident_status
                ?.resolved_or_closed ?? 0;


        /* =========================
           INCIDENT SEVERITY
        ========================= */

        const incidentSeverity =
            data.incident_severity || {};


        document.getElementById(
            "criticalIncidents"
        ).textContent =
            incidentSeverity.critical ?? 0;


        document.getElementById(
            "highIncidents"
        ).textContent =
            incidentSeverity.high ?? 0;


        document.getElementById(
            "mediumIncidents"
        ).textContent =
            incidentSeverity.medium ?? 0;


        document.getElementById(
            "lowIncidents"
        ).textContent =
            incidentSeverity.low ?? 0;


        /* =========================
           HIGH + CRITICAL
        ========================= */

        const critical =
            Number(
                incidentSeverity.critical ?? 0
            );


        const high =
            Number(
                incidentSeverity.high ?? 0
            );


        document.getElementById(
            "highCritical"
        ).textContent =
            critical + high;


        /* =========================
           ALERT STATUS
        ========================= */

        const alertStatus =
            data.alert_status || {};


        document.getElementById(
            "newAlerts"
        ).textContent =
            alertStatus.new ?? 0;


        document.getElementById(
            "acknowledgedAlerts"
        ).textContent =
            alertStatus.acknowledged ?? 0;


        document.getElementById(
            "resolvedAlerts"
        ).textContent =
            alertStatus.resolved ?? 0;


        console.log(
            "Report loaded successfully."
        );


    } catch (error) {

        console.error(
            "REPORT ERROR:",
            error
        );


        document.getElementById(
            "totalEvents"
        ).textContent =
            "Error";


        document.getElementById(
            "totalIncidents"
        ).textContent =
            "Error";


        document.getElementById(
            "totalAlerts"
        ).textContent =
            "Error";


        document.getElementById(
            "highCritical"
        ).textContent =
            "Error";


        alert(
            "Unable to load security report."
        );
    }
}


/* =========================
   DOWNLOAD CSV
========================= */

async function downloadCSV() {

    try {

        const response =
            await fetch(
                `${API_URL}/reports/csv`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        console.log(
            "CSV response:",
            response.status
        );


        if (response.status === 401) {

            logout();

            return;
        }


        if (!response.ok) {

            throw new Error(
                "CSV report generation failed"
            );
        }


        const blob =
            await response.blob();


        const url =
            window.URL.createObjectURL(
                blob
            );


        const link =
            document.createElement(
                "a"
            );


        link.href = url;

        link.download =
            "sentinelx_security_report.csv";


        document.body.appendChild(
            link
        );


        link.click();


        link.remove();


        window.URL.revokeObjectURL(
            url
        );


        console.log(
            "CSV downloaded successfully."
        );


    } catch (error) {

        console.error(
            "CSV ERROR:",
            error
        );


        alert(
            "Unable to download CSV report."
        );
    }
}


/* =========================
   DOWNLOAD PDF
========================= */

async function downloadPDF() {

    try {

        const response =
            await fetch(
                `${API_URL}/reports/pdf`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        console.log(
            "PDF response:",
            response.status
        );


        if (response.status === 401) {

            logout();

            return;
        }


        if (!response.ok) {

            throw new Error(
                "PDF report generation failed"
            );
        }


        const blob =
            await response.blob();


        const url =
            window.URL.createObjectURL(
                blob
            );


        const link =
            document.createElement(
                "a"
            );


        link.href = url;

        link.download =
            "sentinelx_security_report.pdf";


        document.body.appendChild(
            link
        );


        link.click();


        link.remove();


        window.URL.revokeObjectURL(
            url
        );


        console.log(
            "PDF downloaded successfully."
        );


    } catch (error) {

        console.error(
            "PDF ERROR:",
            error
        );


        alert(
            "Unable to download PDF report."
        );
    }
}


/* =========================
   LOGOUT
========================= */

function logout() {

    localStorage.removeItem(
        "sentinelx_token"
    );


    window.location.href =
        "login.html";
}


/* =========================
   USERNAME
========================= */

const usernameElement =
    document.getElementById(
        "username"
    );


if (usernameElement) {

    usernameElement.textContent =
        "Analyst";
}


/* =========================
   START
========================= */

loadReport();