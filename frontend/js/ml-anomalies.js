const API_URL = "https://sentinelx-csdo.onrender.com";

const token =
    localStorage.getItem("sentinelx_token");

if (!token) {
    window.location.href = "login.html";
}


let allAnomalies = [];

let filteredAnomalies = [];

let currentPage = 1;

const pageSize = 10;


// ===============================
// LOAD ML ANOMALIES
// ===============================

async function loadAnomalies() {

    const tableBody =
        document.getElementById(
            "anomaliesTableBody"
        );

    try {

        tableBody.innerHTML = `
            <tr>
                <td colspan="8">
                    Running ML anomaly scan...
                </td>
            </tr>
        `;


        const response =
            await fetch(
                `${API_URL}/anomaly/scan`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        console.log(
            "ML response status:",
            response.status
        );


        if (response.status === 401) {

            logout();

            return;
        }


        if (!response.ok) {

            throw new Error(
                "Failed to run ML anomaly scan"
            );

        }


        const data =
            await response.json();


        console.log(
            "ML ANOMALY DATA:",
            data
        );


        // ===============================
        // SUMMARY
        // ===============================

        document.getElementById(
            "modelName"
        ).textContent =
            data.model || "-";


        document.getElementById(
            "totalEvents"
        ).textContent =
            data.total_events_analyzed ?? 0;


        document.getElementById(
            "totalAnomalies"
        ).textContent =
            data.anomalies_detected ?? 0;


        document.getElementById(
            "totalIncidents"
        ).textContent =
            data.incidents_created ?? 0;


        // ===============================
        // ANOMALIES
        // ===============================

        allAnomalies =
            Array.isArray(data.anomalies)
                ? data.anomalies
                : [];


        filteredAnomalies =
            [...allAnomalies];


        currentPage = 1;


        displayAnomalies();

        updatePagination();


    } catch (error) {

        console.error(
            "ML anomaly error:",
            error
        );


        tableBody.innerHTML = `
            <tr>
                <td colspan="8">
                    Unable to load ML anomalies.
                </td>
            </tr>
        `;


        document.getElementById(
            "anomalyCount"
        ).textContent =
            "Error";

    }

}


// ===============================
// DISPLAY ANOMALIES
// ===============================

function displayAnomalies() {

    const tableBody =
        document.getElementById(
            "anomaliesTableBody"
        );


    const total =
        filteredAnomalies.length;


    document.getElementById(
        "anomalyCount"
    ).textContent =
        `${total} anomalies`;


    if (total === 0) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="8">
                    No anomalies found.
                </td>
            </tr>
        `;

        return;
    }


    const start =
        (currentPage - 1) *
        pageSize;


    const end =
        start + pageSize;


    const pageAnomalies =
        filteredAnomalies.slice(
            start,
            end
        );


    tableBody.innerHTML =
        pageAnomalies
            .map(
                anomaly => {

                    const severity =
                        anomaly.severity ||
                        "low";


                    const anomalyLevel =
                        anomaly.anomaly_level ||
                        "medium";


                    const sourceIP =
                        anomaly.source_ip ||
                        "-";


                    const ioc =
                        anomaly.ioc_value
                            ? `${anomaly.ioc_type || ""}: ${anomaly.ioc_value}`
                            : "-";


                    return `

                        <tr>

                            <td>
                                ${anomaly.event_id ?? "-"}
                            </td>

                            <td>
                                ${anomaly.event_type ?? "-"}
                            </td>

                            <td>
                                ${sourceIP}
                            </td>

                            <td>
                                ${ioc}
                            </td>

                            <td>

                                <span
                                    class="severity ${severity}"
                                >
                                    ${severity}
                                </span>

                            </td>

                            <td>

                                <span
                                    class="severity ${anomalyLevel}"
                                >
                                    ${anomalyLevel}
                                </span>

                            </td>

                            <td>

                                <strong>
                                    ${anomaly.risk_score ?? 0}
                                </strong>

                            </td>

                            <td>
                                ${anomaly.incident_id ?? "-"}
                            </td>

                        </tr>

                    `;

                }
            )
            .join("");

}


// ===============================
// SEARCH
// ===============================

document
    .getElementById("searchInput")
    .addEventListener(
        "input",
        function () {

            const search =
                this.value
                    .toLowerCase()
                    .trim();


            if (!search) {

                filteredAnomalies =
                    [...allAnomalies];

            } else {

                filteredAnomalies =
                    allAnomalies.filter(
                        anomaly =>
                            JSON.stringify(
                                anomaly
                            )
                            .toLowerCase()
                            .includes(search)
                    );

            }


            currentPage = 1;


            displayAnomalies();

            updatePagination();

        }
    );


// ===============================
// PAGINATION
// ===============================

function updatePagination() {

    let pagination =
        document.getElementById(
            "anomalyPagination"
        );


    if (!pagination) {

        pagination =
            document.createElement(
                "div"
            );


        pagination.id =
            "anomalyPagination";


        pagination.style.display =
            "flex";


        pagination.style.justifyContent =
            "center";


        pagination.style.alignItems =
            "center";


        pagination.style.gap =
            "15px";


        pagination.style.marginTop =
            "20px";


        document
            .querySelector(".events-panel")
            .appendChild(
                pagination
            );

    }


    const totalPages =
        Math.max(
            1,
            Math.ceil(
                filteredAnomalies.length /
                pageSize
            )
        );


    if (currentPage > totalPages) {

        currentPage =
            totalPages;

    }


    pagination.innerHTML = `

        <button
            onclick="previousPage()"
            ${currentPage <= 1 ? "disabled" : ""}
        >
            ← Previous
        </button>


        <span>

            Page
            ${currentPage}
            of
            ${totalPages}

        </span>


        <button
            onclick="nextPage()"
            ${currentPage >= totalPages ? "disabled" : ""}
        >
            Next →

        </button>

    `;


    const buttons =
        pagination.querySelectorAll(
            "button"
        );


    buttons.forEach(
        button => {

            button.style.padding =
                "10px 18px";


            button.style.border =
                "none";


            button.style.borderRadius =
                "7px";


            button.style.background =
                "#2563eb";


            button.style.color =
                "white";


            button.style.cursor =
                "pointer";


            if (button.disabled) {

                button.style.background =
                    "#94a3b8";


                button.style.cursor =
                    "not-allowed";

            }

        }
    );

}


// ===============================
// PREVIOUS PAGE
// ===============================

function previousPage() {

    if (currentPage > 1) {

        currentPage--;

        displayAnomalies();

        updatePagination();

    }

}


// ===============================
// NEXT PAGE
// ===============================

function nextPage() {

    const totalPages =
        Math.max(
            1,
            Math.ceil(
                filteredAnomalies.length /
                pageSize
            )
        );


    if (currentPage < totalPages) {

        currentPage++;

        displayAnomalies();

        updatePagination();

    }

}


// ===============================
// LOGOUT
// ===============================

function logout() {

    localStorage.removeItem(
        "sentinelx_token"
    );


    window.location.href =
        "login.html";

}


// ===============================
// USERNAME
// ===============================

const usernameElement =
    document.getElementById(
        "username"
    );


if (usernameElement) {

    usernameElement.textContent =
        "Analyst";

}


// ===============================
// INITIAL LOAD
// ===============================

loadAnomalies();
