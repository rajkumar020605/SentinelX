const API_URL = "https://sentinelx-csdo.onrender.com";

const token =
    localStorage.getItem("sentinelx_token");

if (!token) {
    window.location.href = "login.html";
}


let allAlerts = [];

let filteredAlerts = [];

let currentPage = 1;

const pageSize = 10;


// ===============================
// LOAD ALERTS
// ===============================

async function loadAlerts() {

    const tableBody =
        document.getElementById(
            "alertsTableBody"
        );

    try {

        tableBody.innerHTML = `
            <tr>
                <td colspan="7">
                    Loading alerts...
                </td>
            </tr>
        `;


        const response =
            await fetch(
                `${API_URL}/alerts/`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        console.log(
            "Alerts response status:",
            response.status
        );


        if (response.status === 401) {

            logout();

            return;
        }


        if (!response.ok) {

            throw new Error(
                "Failed to load alerts"
            );

        }


        const data =
            await response.json();


        console.log(
            "ALERT DATA:",
            data
        );


        // API returns an ARRAY
        allAlerts =
            Array.isArray(data)
                ? data
                : [];


        filteredAlerts =
            [...allAlerts];


        currentPage = 1;


        displayAlerts();

        updatePagination();


    } catch (error) {

        console.error(
            "ALERT ERROR:",
            error
        );


        tableBody.innerHTML = `
            <tr>
                <td colspan="7">
                    Unable to load alerts.
                </td>
            </tr>
        `;


        document.getElementById(
            "alertCount"
        ).textContent =
            "Error";

    }

}


// ===============================
// DISPLAY ALERTS
// ===============================

function displayAlerts() {

    const tableBody =
        document.getElementById(
            "alertsTableBody"
        );


    const total =
        filteredAlerts.length;


    document.getElementById(
        "alertCount"
    ).textContent =
        `${total} alerts`;


    if (total === 0) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="7">
                    No alerts found.
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


    const pageAlerts =
        filteredAlerts.slice(
            start,
            end
        );


    tableBody.innerHTML =
        pageAlerts
            .map(
                alert => {

                    const severity =
                        alert.severity ||
                        "low";


                    const status =
                        alert.status ||
                        "-";


                    const created =
                        alert.created_at
                            ? new Date(
                                alert.created_at
                            ).toLocaleString()
                            : "-";


                    return `

                        <tr>

                            <td>
                                ${alert.id ?? "-"}
                            </td>

                            <td>
                                ${alert.title ?? "-"}
                            </td>

                            <td>
                                ${alert.incident_id ?? "-"}
                            </td>

                            <td>

                                <span
                                    class="severity ${severity}"
                                >
                                    ${severity}
                                </span>

                            </td>

                            <td>

                                <strong>
                                    ${alert.risk_score ?? 0}
                                </strong>

                            </td>

                            <td>
                                ${status}
                            </td>

                            <td>
                                ${created}
                            </td>

                        </tr>

                    `;

                }
            )
            .join("");

}


// ===============================
// SEARCH ALERTS
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

                filteredAlerts =
                    [...allAlerts];

            } else {

                filteredAlerts =
                    allAlerts.filter(
                        alert =>
                            JSON.stringify(
                                alert
                            )
                            .toLowerCase()
                            .includes(search)
                    );

            }


            currentPage = 1;


            displayAlerts();

            updatePagination();

        }
    );


// ===============================
// PAGINATION
// ===============================

function updatePagination() {

    let pagination =
        document.getElementById(
            "alertPagination"
        );


    if (!pagination) {

        pagination =
            document.createElement(
                "div"
            );


        pagination.id =
            "alertPagination";


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
                filteredAlerts.length /
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

        displayAlerts();

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
                filteredAlerts.length /
                pageSize
            )
        );


    if (currentPage < totalPages) {

        currentPage++;

        displayAlerts();

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

loadAlerts();
