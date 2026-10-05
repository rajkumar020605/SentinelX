const API_URL = "https://sentinelx-csdo.onrender.com";

const token =
    localStorage.getItem("sentinelx_token");

if (!token) {
    window.location.href = "login.html";
}

let allMappings = [];
let filteredMappings = [];

async function loadMitre() {

    const tableBody =
        document.getElementById("mitreTableBody");

    try {

        tableBody.innerHTML = `
            <tr>
                <td colspan="5">
                    Loading MITRE ATT&CK mappings...
                </td>
            </tr>
        `;

        const response =
            await fetch(
                `${API_URL}/mitre/techniques`,
                {
                    method: "GET",
                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );

        console.log(
            "MITRE response status:",
            response.status
        );

        if (response.status === 401) {
            logout();
            return;
        }

        if (!response.ok) {
            throw new Error(
                "Failed to load MITRE mappings"
            );
        }

        const data =
            await response.json();

        console.log(
            "MITRE DATA:",
            data
        );


        /*
         * Backend response:
         *
         * {
         *   total_mappings: 2,
         *   mappings: {
         *      BRUTE_FORCE_LOGIN: {...},
         *      SUSPICIOUS_LOGIN: {...}
         *   }
         * }
         */


        const mappings =
            data.mappings || {};


        allMappings =
            Object.entries(mappings).map(
                ([rule, mapping]) => {

                    return {
                        rule: rule,
                        ...mapping
                    };

                }
            );


        filteredMappings =
            [...allMappings];


        displayMitre();


    } catch (error) {

        console.error(
            "MITRE ERROR:",
            error
        );

        tableBody.innerHTML = `
            <tr>
                <td colspan="5">
                    Unable to load MITRE ATT&CK mappings.
                </td>
            </tr>
        `;

        document.getElementById(
            "mitreCount"
        ).textContent = "Error";
    }
}


function displayMitre() {

    const tableBody =
        document.getElementById(
            "mitreTableBody"
        );

    const total =
        filteredMappings.length;


    document.getElementById(
        "mitreCount"
    ).textContent =
        `${total} technique mappings`;


    if (total === 0) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="5">
                    No MITRE mappings found.
                </td>
            </tr>
        `;

        return;
    }


    tableBody.innerHTML =
        filteredMappings
            .map(
                mapping => {

                    const additionalTactics =
                        Array.isArray(
                            mapping.additional_tactics
                        )
                            ? mapping.additional_tactics.join(
                                ", "
                            )
                            : "";


                    const tactic =
                        additionalTactics
                            ? `${mapping.tactic || "-"}, ${additionalTactics}`
                            : mapping.tactic || "-";


                    return `
                        <tr>

                            <td>
                                <strong>
                                    ${mapping.rule || "-"}
                                </strong>
                            </td>

                            <td>
                                <strong>
                                    ${mapping.technique_id || "-"}
                                </strong>
                            </td>

                            <td>
                                ${mapping.technique_name || "-"}
                            </td>

                            <td>
                                ${tactic}
                            </td>

                            <td>
                                ${mapping.description || "-"}
                            </td>

                        </tr>
                    `;

                }
            )
            .join("");
}


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

                filteredMappings =
                    [...allMappings];

            } else {

                filteredMappings =
                    allMappings.filter(
                        mapping =>
                            JSON.stringify(
                                mapping
                            )
                            .toLowerCase()
                            .includes(search)
                    );
            }


            displayMitre();

        }
    );


function logout() {

    localStorage.removeItem(
        "sentinelx_token"
    );

    window.location.href =
        "login.html";
}


const usernameElement =
    document.getElementById(
        "username"
    );


if (usernameElement) {

    usernameElement.textContent =
        "Analyst";
}


loadMitre();
