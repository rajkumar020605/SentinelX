const API_URL = "https://sentinelx-csdo.onrender.com";

const token = localStorage.getItem("sentinelx_token");

if (!token) {
    window.location.href = "login.html";
}

let allEvents = [];

let currentPage = 1;
let totalPages = 1;
let totalResults = 0;


// =========================
// LOAD SECURITY EVENTS
// =========================

async function loadEvents(page = 1) {

    const tableBody =
        document.getElementById("eventsTableBody");

    try {

        tableBody.innerHTML = `
            <tr>
                <td colspan="8">
                    Loading events...
                </td>
            </tr>
        `;

        const response = await fetch(
            `${API_URL}/security-events/?page=${page}`,
            {
                method: "GET",

                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );


        // =========================
        // TOKEN EXPIRED
        // =========================

        if (response.status === 401) {

            logout();

            return;
        }


        // =========================
        // API ERROR
        // =========================

        if (!response.ok) {

            throw new Error(
                "Failed to load security events"
            );
        }


        // =========================
        // GET RESPONSE
        // =========================

        const data = await response.json();

        console.log(
            "Security events:",
            data
        );


        // =========================
        // STORE PAGINATION DATA
        // =========================

        allEvents =
            data.results || [];

        currentPage =
            data.page || page;

        totalPages =
            data.total_pages || 1;

        totalResults =
            data.total_results || 0;


        // =========================
        // DISPLAY EVENTS
        // =========================

        displayEvents(allEvents);


        // =========================
        // UPDATE PAGINATION
        // =========================

        updatePagination();


    } catch (error) {

        console.error(
            "Security events error:",
            error
        );


        tableBody.innerHTML = `
            <tr>
                <td colspan="8">
                    Unable to load security events.
                </td>
            </tr>
        `;


        document.getElementById(
            "eventCount"
        ).textContent = "Error";
    }
}


// =========================
// DISPLAY EVENTS
// =========================

function displayEvents(events) {

    const tableBody =
        document.getElementById(
            "eventsTableBody"
        );


    // =========================
    // EVENT COUNT
    // =========================

    document.getElementById(
        "eventCount"
    ).textContent =
        `${events.length} events on this page (${totalResults} total)`;


    // =========================
    // NO EVENTS
    // =========================

    if (events.length === 0) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="8">
                    No security events found.
                </td>
            </tr>
        `;

        return;
    }


    // =========================
    // CREATE TABLE ROWS
    // =========================

    tableBody.innerHTML = events.map(
        event => {

            const ioc =
                event.ioc_value
                    ? `${event.ioc_type || ""}: ${event.ioc_value}`
                    : "-";


            const created =
                event.created_at
                    ? new Date(
                        event.created_at
                    ).toLocaleString()
                    : "-";


            const severity =
                event.severity || "low";


            return `
                <tr>

                    <td>
                        ${event.event_id ?? "-"}
                    </td>

                    <td>
                        ${event.event_type ?? "-"}
                    </td>

                    <td>
                        ${event.source_ip ?? "-"}
                    </td>

                    <td>
                        ${event.username ?? "-"}
                    </td>

                    <td>
                        ${ioc}
                    </td>

                    <td>
                        <span class="severity ${severity}">
                            ${severity}
                        </span>
                    </td>

                    <td>
                        ${event.status ?? "-"}
                    </td>

                    <td>
                        ${created}
                    </td>

                </tr>
            `;
        }
    ).join("");
}


// =========================
// SEARCH EVENTS
// =========================

document
    .getElementById("searchInput")
    .addEventListener(
        "input",
        function () {

            const search =
                this.value
                    .toLowerCase()
                    .trim();


            // =========================
            // SHOW ALL EVENTS
            // =========================

            if (!search) {

                displayEvents(
                    allEvents
                );

                return;
            }


            // =========================
            // FILTER EVENTS
            // =========================

            const filtered =
                allEvents.filter(
                    event => {

                        return JSON.stringify(
                            event
                        )
                        .toLowerCase()
                        .includes(search);
                    }
                );


            displayEvents(
                filtered
            );
        }
    );


// =========================
// PAGINATION
// =========================

function updatePagination() {

    let pagination =
        document.getElementById(
            "pagination"
        );


    // =========================
    // CREATE PAGINATION AREA
    // =========================

    if (!pagination) {

        pagination =
            document.createElement(
                "div"
            );

        pagination.id =
            "pagination";

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


        const eventsPanel =
            document.querySelector(
                ".events-panel"
            );

        eventsPanel.appendChild(
            pagination
        );
    }


    // =========================
    // PAGINATION BUTTONS
    // =========================

    pagination.innerHTML = `

        <button
            id="previousBtn"
            onclick="previousPage()"
            ${currentPage <= 1 ? "disabled" : ""}
        >
            ← Previous
        </button>


        <span>
            Page ${currentPage}
            of ${totalPages}
        </span>


        <button
            id="nextBtn"
            onclick="nextPage()"
            ${currentPage >= totalPages ? "disabled" : ""}
        >
            Next →
        </button>

    `;


    // =========================
    // BUTTON STYLE
    // =========================

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


// =========================
// PREVIOUS PAGE
// =========================

function previousPage() {

    if (currentPage > 1) {

        loadEvents(
            currentPage - 1
        );
    }
}


// =========================
// NEXT PAGE
// =========================

function nextPage() {

    if (currentPage < totalPages) {

        loadEvents(
            currentPage + 1
        );
    }
}


// =========================
// LOGOUT
// =========================

function logout() {

    localStorage.removeItem(
        "sentinelx_token"
    );

    window.location.href =
        "login.html";
}


// =========================
// USERNAME
// =========================

const usernameElement =
    document.getElementById(
        "username"
    );


if (usernameElement) {

    usernameElement.textContent =
        "Analyst";
}


// =========================
// INITIAL LOAD
// =========================

loadEvents();
