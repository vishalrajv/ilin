/* ILIN Authentication utilities */

const API_BASE = "";

function getToken() {
    return localStorage.getItem("ilin_token");
}

function setToken(token) {
    localStorage.setItem("ilin_token", token);
}

function clearToken() {
    localStorage.removeItem("ilin_token");
}

function getUser() {
    const data = localStorage.getItem("ilin_user");
    return data ? JSON.parse(data) : null;
}

function setUser(user) {
    localStorage.setItem("ilin_user", JSON.stringify(user));
}

function clearUser() {
    localStorage.removeItem("ilin_user");
}

function isLoggedIn() {
    return !!getToken();
}

function isAdmin() {
    const user = getUser();
    return user && user.role === "admin";
}

async function apiCall(url, options = {}) {
    const token = getToken();
    const headers = {
        "Content-Type": "application/json",
        ...options.headers,
    };
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) {
        clearToken();
        clearUser();
        window.location.href = "/";
        return null;
    }
    return response;
}

async function login(username, password) {
    const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Login failed");
    }
    const data = await response.json();
    setToken(data.access_token);
    setUser({ username: data.username, role: data.role });
    return data;
}

async function logout() {
    await apiCall("/api/auth/logout", { method: "POST" });
    clearToken();
    clearUser();
    window.location.href = "/";
}

// Redirect on page load
function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = "/";
    }
}

function redirectIfLoggedIn() {
    if (isLoggedIn()) {
        window.location.href = isAdmin() ? "/admin" : "/chat";
    }
}
