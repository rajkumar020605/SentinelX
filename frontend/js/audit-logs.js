const API_URL = "https://sentinelx-csdo.onrender.com";

async function loadAuditLogs() {

    const token = localStorage.getItem("sentinelx_token");

    const message = document.getElementById("message");
    const tableBody = document.getElementById("auditTableBody");

    if (!token) {
        message.textContent = "Please login as admin.";
        return;
    }

    try {

        const response = await fetch(`${API_URL}/audit-logs/`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        console.log("Audit Logs Status:", response.status);

        if (response.status === 401) {
            message.textContent = "Session expired. Please login again.";
            return;
        }

        if (response.status === 403) {
            message.textContent = "Access denied. Admin account required.";
            return;
        }

        if (!response.ok) {
            throw new Error("Failed to load audit logs");
        }

        const logs = await response.json();

        tableBody.innerHTML = "";

        if (logs.length === 0) {
            message.textContent = "No audit logs found.";
            return;
        }

        message.textContent = `${logs.length} audit logs found.`;

        logs.forEach(log => {

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${log.id}</td>
                <td>${log.user_id ?? "-"}</td>
                <td>${log.action ?? "-"}</td>
                <td>${log.resource ?? "-"}</td>
                <td>${log.details ?? "-"}</td>
                <td>${log.ip_address ?? "-"}</td>
                <td>${formatDate(log.created_at)}</td>
            `;

            tableBody.appendChild(row);
        });

    } catch (error) {

        console.error("Audit Logs Error:", error);

        message.textContent =
            "Unable to load audit logs. Check the browser console.";
    }
}

function formatDate(dateString) {

    if (!dateString) {
        return "-";
    }

    return new Date(dateString).toLocaleString();
}

document.addEventListener("DOMContentLoaded", loadAuditLogs);
