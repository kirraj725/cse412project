// API endpoints – match urls.py
const API_LOGIN   = "/api/login/";
const API_ACCOUNT = "/api/account/";
const API_REWARDS = "/api/rewards/";
const API_STORES  = "/api/stores/";
const API_REGISTER = "/api/register/";

let currentUser = null;

// Tabs
const tabButtons = document.querySelectorAll(".tab-button");
const tabs = document.querySelectorAll(".tab");

const logoutButton = document.getElementById("logout-button");
const authButtons = document.getElementById("auth-buttons");

tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        const target = btn.getAttribute("data-tab");
        tabs.forEach(t => t.classList.remove("active"));
        document.getElementById(target).classList.add("active");
    });
});

function enableTabsAfterLogin() {
    authButtons.style.display = "none";

    document.querySelectorAll("nav .tab-button").forEach(btn => {
        const tab = btn.getAttribute("data-tab");
        if (tab !== "login-tab" && tab !== "register-tab") {
            btn.disabled = false;
            btn.style.display = "inline";
        }
    });
}

function disableTabsAfterLogout() {
    authButtons.style.display = "inline"; // show login/register buttons
    logoutButton.style.display = "none"; // hide logout

    document.querySelectorAll("nav .tab-button").forEach(btn => {
        const tab = btn.getAttribute("data-tab");
        
        if (tab === "login-tab" || tab === "register-tab") {
            btn.disabled = false;
            btn.style.display = "inline";
        } else {
            btn.disabled = true;
            btn.style.display = "none";
        }
    });
}

function resetForms() {
    // Clear login form
    document.getElementById("email").value = "";
    document.getElementById("password").value = "";
    loginMessage.textContent = "";

    // Clear register form
    document.getElementById("reg-name").value = "";
    document.getElementById("reg-email").value = "";
    document.getElementById("reg-phone").value = "";
    document.getElementById("reg-password").value = "";
    registerMessage.textContent = "";
}


// Login
const loginForm = document.getElementById("login-form");
const loginMessage = document.getElementById("login-message");

loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    loginMessage.textContent = "";
    loginMessage.style.color = "red";

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const res = await fetch(API_LOGIN, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email, password })
        });

        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            loginMessage.textContent = data.detail || data.message || "Login failed.";
            return;
        }

        const data = await res.json();
        currentUser = data.user || data;

        loginMessage.style.color = "green";
        loginMessage.textContent = "Login successful.";

        enableTabsAfterLogin();
        await loadAccount();
        await loadRewards();
        await loadStores();

        tabs.forEach(t => t.classList.remove("active"));
        document.getElementById("account-tab").classList.add("active");
    } catch (err) {
        console.error(err);
        loginMessage.textContent = "Network or server error.";
    }
});

// Handles logout
logoutButton.addEventListener("click", async () => {
    try {
        await fetch("/api/logout/", { method: "POST" });
    } catch (err) {
        console.error("Logout failed:", err);
    }

    // Reset UI
    resetForms();
    disableTabsAfterLogout();
    currentUser = null;

    tabs.forEach(t => t.classList.remove("active"));
    document.getElementById("login-tab").classList.add("active");
});


// Account tab
async function loadAccount() {
    try {
        const res = await fetch(API_ACCOUNT);
        if (!res.ok) return;

        const data = await res.json();
        const div = document.getElementById("account-info");
        div.innerHTML = `
            <p><strong>Name:</strong> ${data.name}</p>
            <p><strong>Email:</strong> ${data.email}</p>
            <p><strong>Phone:</strong> ${data.phone}</p>
            <p><strong>Total Points:</strong> ${data.total_points}</p>
        `;
    } catch (err) {
        console.error(err);
    }
}

// Rewards tab
async function loadRewards() {
    try {
        const res = await fetch(API_REWARDS);
        if (!res.ok) return;

        const data = await res.json();

        document.getElementById("total-points").textContent = data.total_points ?? 0;

        const ledgerBody = document.querySelector("#ledger-table tbody");
        ledgerBody.innerHTML = "";
        (data.ledger || []).forEach(entry => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${entry.change_amount}</td>
                <td>${entry.reason}</td>
                <td>${entry.date}</td>
                <td>${entry.expiration_date || ""}</td>
            `;
            ledgerBody.appendChild(tr);
        });

        const rewardsBody = document.querySelector("#rewards-table tbody");
        rewardsBody.innerHTML = "";
        (data.rewards || []).forEach(reward => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${reward.vendor_name}</td>
                <td>${Number(reward.balance).toFixed(2)}</td>
                <td>${reward.expiration}</td>
            `;
            rewardsBody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
    }
}

// Stores tab
async function loadStores() {
    try {
        const res = await fetch(API_STORES);
        if (!res.ok) return;

        const data = await res.json();

        const tbody = document.querySelector("#stores-table tbody");
        tbody.innerHTML = "";
        (data || []).forEach(item => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${item.vendor_name}</td>
                <td>${item.category || ""}</td>
                <td>${Number(item.total_spent).toFixed(2)}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
    }
}

// Register
const registerForm = document.getElementById("register-form");
const registerMessage = document.getElementById("register-message");

registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    registerMessage.textContent = "";
    registerMessage.style.color = "red";

    const name = document.getElementById("reg-name").value;
    const email = document.getElementById("reg-email").value;
    const phone = document.getElementById("reg-phone").value;
    const password = document.getElementById("reg-password").value;

    try {
        const res = await fetch(API_REGISTER, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ name, email, phone, password })
        });

        const data = await res.json();

        if (!res.ok) {
            registerMessage.textContent = data.error || "Registration failed.";
            return;
        }

        registerMessage.style.color = "green";
        registerMessage.textContent = "Account created! You can now log in.";

        setTimeout(() => {
            tabs.forEach(t => t.classList.remove("active"));
            document.getElementById("login-tab").classList.add("active");
        }, 1500);

    } catch (err) {
        console.error(err);
        registerMessage.textContent = "Network or server error.";
    }
});

