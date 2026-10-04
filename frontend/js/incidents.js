const API_URL = "http://127.0.0.1:8000";

const token =
    localStorage.getItem("sentinelx_token");

if (!token) {
    window.location.href = "login.html";
}

let allIncidents = [];
let filteredIncidents = [];

let currentPage = 1;
const pageSize = 10;


/* =========================
   LOAD INCIDENTS
========================= */

async function loadIncidents() {

    const tableBody =
        document.getElementById(
            "incidentsTableBody"
        );

    try {

        tableBody.innerHTML = `
            <tr>
                <td colspan="9">
                    Loading incidents...
                </td>
            </tr>
        `;


        const response =
            await fetch(
                `${API_URL}/incidents/`,
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


        if (!response.ok) {

            throw new Error(
                "Failed to load incidents"
            );
        }


        const data =
            await response.json();


        console.log(
            "INCIDENT DATA:",
            data
        );


        allIncidents =
            Array.isArray(data)
                ? data
                : [];


        filteredIncidents =
            [...allIncidents];


        currentPage = 1;


        displayIncidents();

        updatePagination();


    } catch (error) {

        console.error(
            "INCIDENT ERROR:",
            error
        );


        tableBody.innerHTML = `
            <tr>
                <td colspan="9">
                    Unable to load incidents.
                </td>
            </tr>
        `;


        document.getElementById(
            "incidentCount"
        ).textContent =
            "Error";
    }
}


/* =========================
   DISPLAY INCIDENTS
========================= */

function displayIncidents() {

    const tableBody =
        document.getElementById(
            "incidentsTableBody"
        );


    const total =
        filteredIncidents.length;


    document.getElementById(
        "incidentCount"
    ).textContent =
        `${total} incidents`;


    if (total === 0) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="9">
                    No incidents found.
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


    const pageIncidents =
        filteredIncidents.slice(
            start,
            end
        );


    tableBody.innerHTML =
        pageIncidents
            .map(
                incident => {

                    const severity =
                        incident.severity ||
                        "low";


                    const status =
                        incident.status ||
                        "-";


                    const created =
                        incident.created_at
                            ? new Date(
                                incident.created_at
                            ).toLocaleString()
                            : "-";


                    return `
                        <tr>

                            <!-- INCIDENT ID -->

                            <td>

                                <button
                                    type="button"
                                    onclick="openIncident(${incident.id})"
                                    class="incident-id-button"
                                >
                                    #${incident.id ?? "-"}
                                </button>

                            </td>


                            <!-- TITLE -->

                            <td>
                                ${incident.title ?? "-"}
                            </td>


                            <!-- DETECTION RULE -->

                            <td>
                                ${incident.detection_rule ?? "-"}
                            </td>


                            <!-- SOURCE IP -->

                            <td>
                                ${incident.source_ip ?? "-"}
                            </td>


                            <!-- USERNAME -->

                            <td>
                                ${incident.username ?? "-"}
                            </td>


                            <!-- SEVERITY -->

                            <td>

                                <span
                                    class="severity ${severity}"
                                >
                                    ${severity}
                                </span>

                            </td>


                            <!-- RISK SCORE -->

                            <td>

                                <strong>
                                    ${incident.risk_score ?? 0}
                                </strong>

                            </td>


                            <!-- STATUS -->

                            <td>
                                ${status}
                            </td>


                            <!-- CREATED -->

                            <td>
                                ${created}
                            </td>

                        </tr>
                    `;
                }
            )
            .join("");
}


/* =========================
   OPEN INCIDENT DETAILS
========================= */

function openIncident(
    incidentId
) {

    console.log(
        "Opening incident:",
        incidentId
    );


    if (!incidentId) {

        alert(
            "Invalid incident ID."
        );

        return;
    }


    window.location.href =
        `incident-details.html?id=${encodeURIComponent(incidentId)}`;
}


/* =========================
   SEARCH INCIDENTS
========================= */

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

                filteredIncidents =
                    [...allIncidents];

            } else {

                filteredIncidents =
                    allIncidents.filter(
                        incident =>
                            JSON.stringify(
                                incident
                            )
                            .toLowerCase()
                            .includes(search)
                    );
            }


            currentPage = 1;


            displayIncidents();

            updatePagination();

        }
    );


/* =========================
   PAGINATION
========================= */

function updatePagination() {

    let pagination =
        document.getElementById(
            "incidentPagination"
        );


    if (!pagination) {

        pagination =
            document.createElement(
                "div"
            );


        pagination.id =
            "incidentPagination";


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
            .querySelector(
                ".events-panel"
            )
            .appendChild(
                pagination
            );
    }


    const totalPages =
        Math.max(
            1,
            Math.ceil(
                filteredIncidents.length /
                pageSize
            )
        );


    if (
        currentPage >
        totalPages
    ) {

        currentPage =
            totalPages;
    }


    pagination.innerHTML = `

        <button
            onclick="previousPage()"
            ${currentPage <= 1
                ? "disabled"
                : ""}
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
            ${currentPage >= totalPages
                ? "disabled"
                : ""}
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


/* =========================
   PREVIOUS PAGE
========================= */

function previousPage() {

    if (currentPage > 1) {

        currentPage--;

        displayIncidents();

        updatePagination();
    }
}


/* =========================
   NEXT PAGE
========================= */

function nextPage() {

    const totalPages =
        Math.max(
            1,
            Math.ceil(
                filteredIncidents.length /
                pageSize
            )
        );


    if (
        currentPage <
        totalPages
    ) {

        currentPage++;

        displayIncidents();

        updatePagination();
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

loadIncidents();