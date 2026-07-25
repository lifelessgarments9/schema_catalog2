const API = "http://127.0.0.1:8000";

// ─── helpers ───────────────────────────────────────────────────────────────

function authHeaders(json = false) {
    const token = localStorage.getItem("access");
    const h = { Authorization: `Bearer ${token}` };
    if (json) h["Content-Type"] = "application/json";
    return h;
}

// ─── catalog ───────────────────────────────────────────────────────────────

export async function getDevices(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => {
        if (v !== "" && v != null) params.append(k, v);
    });
    const qs = params.toString();
    const url = qs ? `${API}/catalog/devices/?${qs}` : `${API}/catalog/devices/`;
    return fetch(url).then(r => r.json());
}

export async function getDevice(id) {
    return fetch(`${API}/catalog/devices/${id}/`).then(r => r.json());
}

export async function getCategories() {
    return fetch(`${API}/catalog/categories/`).then(r => r.json());
}

export async function addDevice(data) {
    const response = await fetch(`${API}/catalog/`, {
        method: "POST",
        headers: authHeaders(),
        body: data,
    });
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

export async function getRentalRequests() {
    return fetch(`${API}/rental/requests/`, { headers: authHeaders() }).then(r => r.json());
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
        body: JSON.stringify({
            message,
            chat_id: chatId
        })
    });
    return response.json();
}

export async function deleteChat(id) {
    await fetch(`${API}/ai/chats/${id}/`, {
        method: "DELETE",
        headers: authHeaders()
    });
}
