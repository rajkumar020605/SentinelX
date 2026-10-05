const API_URL = "https://sentinelx-csdo.onrender.com";

const token =
    localStorage.getItem("sentinelx_token");

if (!token) {
    window.location.href = "login.html";
}


/* =========================
   GET INCIDENT ID
========================= */

const params =
    new URLSearchParams(
        window.location.search
    );

const incidentId =
    params.get("id");


if (!incidentId) {

    alert("Incident ID is missing.");

    window.location.href =
        "incidents.html";
}


/* =========================
   LOAD INCIDENT
========================= */

async function loadIncident() {

    try {

        const response =
            await fetch(
                `${API_URL}/incidents/${incidentId}`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        console.log(
            "Incident response:",
            response.status
        );


        if (response.status === 401) {

            logout();

            return;
        }


        if (response.status === 404) {

            alert(
                "Incident not found."
            );

            goBack();

            return;
        }


        if (!response.ok) {

            throw new Error(
                "Failed to load incident"
            );
        }


        const incident =
            await response.json();


        console.log(
            "INCIDENT:",
            incident
        );


        /* =========================
           BASIC INFORMATION
        ========================= */

        document.getElementById(
            "incidentId"
        ).textContent =
            incident.id ?? "-";


        document.getElementById(
            "incidentTitle"
        ).textContent =
            incident.title ?? "-";


        document.getElementById(
            "detectionRule"
        ).textContent =
            incident.detection_rule ?? "-";


        document.getElementById(
            "incidentType"
        ).textContent =
            incident.incident_type ?? "-";


        document.getElementById(
            "sourceIP"
        ).textContent =
            incident.source_ip ?? "-";


        document.getElementById(
            "incidentUsername"
        ).textContent =
            incident.username ?? "-";


        /* =========================
           SEVERITY
        ========================= */

        const severity =
            incident.severity || "low";


        document.getElementById(
            "incidentSeverity"
        ).innerHTML = `
            <span class="severity ${severity}">
                ${severity}
            </span>
        `;


        /* =========================
           RISK SCORE
        ========================= */

        document.getElementById(
            "riskScore"
        ).textContent =
            incident.risk_score ?? 0;


        /* =========================
           STATUS
        ========================= */

        document.getElementById(
            "incidentStatus"
        ).textContent =
            incident.status ?? "-";


        /* =========================
           ASSIGNED TO
        ========================= */

        document.getElementById(
            "assignedTo"
        ).textContent =
            incident.assigned_to ?? "-";


        /* =========================
           DATES
        ========================= */

        document.getElementById(
            "createdAt"
        ).textContent =
            formatDate(
                incident.created_at
            );


        document.getElementById(
            "updatedAt"
        ).textContent =
            formatDate(
                incident.updated_at
            );


        /* =========================
           DESCRIPTION
        ========================= */

        document.getElementById(
            "incidentDescription"
        ).textContent =
            incident.description ||
            "No description available.";


        /* =========================
           IOC
        ========================= */

        document.getElementById(
            "iocType"
        ).textContent =
            incident.ioc_type || "-";


        document.getElementById(
            "iocValue"
        ).textContent =
            incident.ioc_value || "-";


        /* =========================
           INVESTIGATION NOTES
        ========================= */

        document.getElementById(
            "investigationNotes"
        ).textContent =
            incident.investigation_notes ||
            "No investigation notes available.";


        /* =========================
           MITRE ATT&CK
        ========================= */

        if (incident.detection_rule) {

            await loadMitre(
                incident.detection_rule
            );
        }


        /* =========================
           RELATED SECURITY EVENT
        ========================= */

        if (incident.event_id) {

            await loadRelatedEvent(
                incident.event_id
            );

        } else {

            showNoRelatedEvent(
                "No related security event."
            );
        }

    } catch (error) {

        console.error(
            "INCIDENT ERROR:",
            error
        );

        alert(
            "Unable to load incident details."
        );
    }
}


/* =========================
   LOAD MITRE
========================= */

async function loadMitre(
    detectionRule
) {

    try {

        const response =
            await fetch(
                `${API_URL}/mitre/rule/${encodeURIComponent(detectionRule)}`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        if (!response.ok) {

            document.getElementById(
                "mitreTechniqueId"
            ).textContent =
                "Not mapped";


            document.getElementById(
                "mitreTechniqueName"
            ).textContent =
                "No MITRE mapping";


            document.getElementById(
                "mitreTactic"
            ).textContent =
                "-";

            return;
        }


        const mapping =
            await response.json();


        console.log(
            "MITRE MAPPING:",
            mapping
        );


        document.getElementById(
            "mitreTechniqueId"
        ).textContent =
            mapping.technique_id ?? "-";


        document.getElementById(
            "mitreTechniqueName"
        ).textContent =
            mapping.technique_name ?? "-";


        document.getElementById(
            "mitreTactic"
        ).textContent =
            mapping.tactic ?? "-";


    } catch (error) {

        console.error(
            "MITRE ERROR:",
            error
        );

        document.getElementById(
            "mitreTechniqueId"
        ).textContent =
            "Not mapped";


        document.getElementById(
            "mitreTechniqueName"
        ).textContent =
            "No MITRE mapping";


        document.getElementById(
            "mitreTactic"
        ).textContent =
            "-";
    }
}


/* =========================
   LOAD SINGLE RELATED EVENT
========================= */

async function loadRelatedEvent(
    eventId
) {

    const tableBody =
        document.getElementById(
            "relatedEventsBody"
        );


    try {

        tableBody.innerHTML = `
            <tr>
                <td colspan="6">
                    Loading security event #${eventId}...
                </td>
            </tr>
        `;


        /*
         * Directly request the event.
         *
         * Example:
         * /security-events/1
         */

        const response =
            await fetch(
                `${API_URL}/security-events/${eventId}`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        console.log(
            "Related event response:",
            response.status
        );


        if (response.status === 401) {

            logout();

            return;
        }


        if (response.status === 404) {

            showNoRelatedEvent(
                `Security event #${eventId} was not found.`
            );

            return;
        }


        if (!response.ok) {

            throw new Error(
                "Failed to load related security event"
            );
        }


        const event =
            await response.json();


        console.log(
            "RELATED SECURITY EVENT:",
            event
        );


        /* =========================
           EVENT SEVERITY
        ========================= */

        const eventSeverity =
            event.severity || "low";


        /* =========================
           DISPLAY EVENT
        ========================= */

        tableBody.innerHTML = `
            <tr>

                <td>
                    ${event.id ?? event.event_id ?? "-"}
                </td>

                <td>
                    ${event.event_type ?? "-"}
                </td>

                <td>
                    ${event.source_ip ?? "-"}
                </td>

                <td>

                    <span
                        class="severity ${eventSeverity}"
                    >
                        ${eventSeverity}
                    </span>

                </td>

                <td>
                    ${event.status ?? "-"}
                </td>

                <td>
                    ${formatDate(
                        event.created_at
                    )}
                </td>

            </tr>
        `;


    } catch (error) {

        console.error(
            "RELATED EVENT ERROR:",
            error
        );


        showNoRelatedEvent(
            "Unable to load related event."
        );
    }
}


/* =========================
   NO RELATED EVENT
========================= */

function showNoRelatedEvent(
    message
) {

    const tableBody =
        document.getElementById(
            "relatedEventsBody"
        );


    tableBody.innerHTML = `
        <tr>
            <td colspan="6">
                ${message}
            </td>
        </tr>
    `;
}


/* =========================
   FORMAT DATE
========================= */

function formatDate(
    value
) {

    if (!value) {
        return "-";
    }


    return new Date(
        value
    ).toLocaleString();
}


/* =========================
   BACK
========================= */

function goBack() {

    window.location.href =
        "incidents.html";
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

loadIncident();
