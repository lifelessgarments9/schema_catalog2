const API = "http://127.0.0.1:8000";

// ─── helpers ───────────────────────────────────────────────────────────────

function authHeaders(json = false) {
    const token = localStorage.getItem("access");
    const h = { Authorization: `Bearer ${token}` };
    if (json) h["Content-Type"] = "application/json";
    return h;
}

// ─── catalog ───────────────────────────────────────────────────────────────

export async function getDevices(filters = {},page = 1,pageSize = 8) {
    const params = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
        if (
            value !== "" &&
            value !== null &&
            value !== undefined
        ) {
            params.append(key, value);
        }
    });

    params.append("page", page);
    params.append("page_size", pageSize);

    const response = await fetch(
        `${API}/catalog/devices/?${params.toString()}`
    );

    if (!response.ok) {
        const data = await response.json().catch(() => ({}));

        const error = new Error(
            data.detail || "Не удалось загрузить каталог"
        );

        error.status = response.status;

        throw error;
    }

    return await response.json();
}

export async function getDevice(id) {
    return fetch(`${API}/catalog/devices/${id}/`).then(r => r.json());
}

export async function getCategories() {
    return fetch(`${API}/catalog/categories/`).then(r => r.json());
}

export async function addDevice(data) {
    const response = await fetch(`${API}/catalog/devices/`, {
        method: "POST",
        headers: authHeaders(),
        body: data,
    });
    return response.json();
}

export async function getCatalogStats() {
    const response = await fetch(`${API}/catalog/stats/`, {headers: authHeaders()});
    return response.json();
}

// ─── auth ──────────────────────────────────────────────────────────────────

export async function register(data) {
    const response = await fetch(`${API}/accounts/register/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    return response.json();
}

export async function login(data) {
    const response = await fetch(`${API}/accounts/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    return response.json();
}

// ─── cart ──────────────────────────────────────────────────────────────────

export async function getCart() {
    return fetch(`${API}/rental/cart/`, { headers: authHeaders() }).then(r => r.json());
}

export async function addDeviceToCart(deviceId) {
    const response = await fetch(`${API}/rental/cart/`, {
        method: "POST",
        headers: authHeaders(true),
        body: JSON.stringify({ device: deviceId }),
    });
    return response.json();
}

export async function removeDeviceFromCart(deviceId) {
    const response = await fetch(`${API}/rental/cart/`, {
        method: "DELETE",
        headers: authHeaders(true),
        body: JSON.stringify({ device: deviceId }),
    });
    return response.json();
}

// ─── rental requests ───────────────────────────────────────────────────────

export async function getRentalRequests(page = 1, pageSize = 10) {
    const response = await fetch(`${API}/rental/requests/?page=${page}&page_size=${pageSize}`, {
        headers: authHeaders()
    });

    const data = await response.json();

    if (!response.ok) {
        const error = new Error(data.detail || "Ошибка загрузки заявок");
        error.status = response.status;
        throw error;
    }

    return data;
}

export async function getRentalRequest(id) {
    return fetch(
        `${API}/rental/requests/${id}/`,
        {
            headers: authHeaders(),
        }
    ).then(r => r.json());
}

export async function createRentalRequest(data) {
    const response = await fetch(`${API}/rental/requests/`, {
        method: "POST",
        headers: authHeaders(true),
        body: JSON.stringify(data),
    });
    return response.json();
}

export async function approveRentalRequest(id) {
    const response = await fetch(`${API}/rental/requests/${id}/`, {
        method: "PATCH",
        headers: authHeaders(true),
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || data.detail || "Ошибка");
    }
    return data;
}

export async function deleteRentalRequest(id) {
    const response = await fetch(`${API}/rental/requests/${id}/`, {
        method: "DELETE",
        headers: authHeaders(),
    });
    if (response.status === 204) return null;
    return response.json();
}

export async function returnRentalRequest(id) {
    const response = await fetch(`${API}/rental/requests/${id}/`, {
        method: "PUT",
        headers: authHeaders(true),
    });

    const data = await response.json();

    if (!response.ok)
        throw new Error(data.error || "Ошибка");

    return data;
}

export async function getRentalRequestPdf(id) {
    const response = await fetch(
        `${API}/rental/requests/${id}/pdf/`,
        {
            headers: authHeaders()
        }
    );

    if (!response.ok) {
        let data;
        try {
            data = await response.json();
        } catch {
            data = {};
        }

        const error = new Error(data.detail || data.error || "Не удалось получить PDF");
        error.status = response.status;
        throw error;
    }
    return await response.blob();
}


//ai
export async function getChats() {
    const token = localStorage.getItem("access");
    if (!token) return [];
    try {
        const response = await fetch(`${API}/ai/chats/`, {
            headers: authHeaders()
        });
        const data = await response.json();
        return Array.isArray(data) ? data : [];
    } catch {
        return [];
    }
}

export async function getChat(id) {
    return fetch(`${API}/ai/chats/${id}/`, {
        headers: authHeaders()
    }).then(r => r.json());
}

export async function askAI(message, chatId = null) {
    const body = { message };
    if (chatId) body.chat_id = chatId;
    const response = await fetch(`${API}/ai/chat/`, {
        method: "POST",
        headers: authHeaders(true),
        body: JSON.stringify(body)
    });

    const data = await response.json();
    if (!response.ok) {
        const error = new Error(data.detail || "Request failed");
        error.status = response.status;
        throw error;
    }
    return data;
}

export async function deleteChat(id) {
    await fetch(`${API}/ai/chats/${id}/`, {
        method: "DELETE",
        headers: authHeaders()
    });
}
