// main.js - Client API Interactor

const API_BASE = "/api";

function setToken(token) {
    localStorage.setItem("token", token);
}

function getToken() {
    return localStorage.getItem("token");
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "/";
}

// Intercept form submissions for login and register
document.addEventListener("DOMContentLoaded", () => {
    checkAuthState();

    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("login-email").value;
            const pass = document.getElementById("login-pass").value;

            try {
                const formData = new URLSearchParams();
                formData.append("username", email);
                formData.append("password", pass);

                const res = await fetch(`${API_BASE}/auth/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: formData
                });

                if (res.ok) {
                    const data = await res.json();
                    setToken(data.access_token);
                    redirectBasedOnRole();
                } else {
                    alert("Login failed. Check credentials.");
                }
            } catch (err) {
                console.error(err);
                alert("Network error.");
            }
        });
    }

    const regForm = document.getElementById("register-form");
    if (regForm) {
        regForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                name: document.getElementById("reg-name").value,
                email: document.getElementById("reg-email").value,
                university_id: document.getElementById("reg-unid").value,
                password: document.getElementById("reg-pass").value,
                is_professor: document.getElementById("reg-isprof").checked
            };

            try {
                const res = await fetch(`${API_BASE}/auth/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                if (res.ok) {
                    alert("Registration successful! Please login.");
                    toggleAuthView(new Event('click'));
                } else {
                    const data = await res.json();
                    let errMsg = 'Registration failed';
                    if (data.detail) {
                        if (typeof data.detail === 'string') {
                            errMsg = data.detail;
                        } else if (Array.isArray(data.detail)) {
                            errMsg = data.detail.map(e => e.msg).join(", ");
                        } else {
                            errMsg = JSON.stringify(data.detail);
                        }
                    }
                    alert(`Error: ${errMsg}`);
                }
            } catch (err) {
                console.error(err);
                alert("Network error.");
            }
        });
    }
});

function toggleAuthView(e) {
    if (e) e.preventDefault();
    const loginView = document.getElementById('login-view');
    const regView = document.getElementById('register-view');
    if (loginView.style.display === 'none') {
        loginView.style.display = 'block';
        regView.style.display = 'none';
    } else {
        loginView.style.display = 'none';
        regView.style.display = 'block';
    }
}

async function redirectBasedOnRole() {
    const token = getToken();
    if (!token) return;

    try {
        const res = await fetch(`${API_BASE}/auth/me`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (res.ok) {
            const user = await res.json();
            if (user.role === "professor") {
                window.location.href = "/professor/dashboard";
            } else {
                window.location.href = "/student/dashboard";
            }
        }
    } catch (err) {
        console.error(err);
    }
}

function checkAuthState() {
    const navActions = document.getElementById('nav-actions');
    const token = getToken();

    if (token) {
        if (navActions) {
            navActions.innerHTML = `
                <a href="#" class="btn btn-primary" onclick="logout()" style="text-decoration: none; color: white;">Logout</a>
            `;
        }
        // Auto redirect if on homepage
        if (window.location.pathname === "/") {
            redirectBasedOnRole();
        }
    } else {
        if (navActions) {
            navActions.innerHTML = `
                <a href="/" style="color: var(--text-secondary);">Login</a>
            `;
        }
    }
}

// Utilities for sending authenticated requests
async function authFetch(url, options = {}) {
    const token = getToken();
    if (!token) {
        window.location.href = "/";
        return null;
    }

    const headers = { ...options.headers };
    headers["Authorization"] = `Bearer ${token}`;
    if (!headers["Content-Type"]) {
        headers["Content-Type"] = "application/json";
    }

    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) {
        logout();
        return null;
    }
    return response;
}

window.togglePasswordVisibility = function(inputId, toggleId) {
    const input = document.getElementById(inputId);
    const toggle = document.getElementById(toggleId);
    if (!input || !toggle) return;

    if (input.type === 'password') {
        input.type = 'text';
        toggle.innerHTML = `
            <svg class="eye-closed" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"></path>
                <line x1="1" y1="1" x2="23" y2="23"></line>
            </svg>
        `;
    } else {
        input.type = 'password';
        toggle.innerHTML = `
            <svg class="eye-open" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                <circle cx="12" cy="12" r="3"></circle>
            </svg>
        `;
    }
};
