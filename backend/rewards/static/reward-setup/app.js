// API endpoints – match urls.py
const API_LOGIN   = "/api/login/";
const API_ACCOUNT = "/api/account/";
const API_REWARDS = "/api/rewards/";
const API_STORES  = "/api/stores/";
const API_VENDORS  = "/api/vendors/";
const API_REGISTER = "/api/register/";
const API_EXCHANGE = "/api/exchange/";

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

function showModal(message) {
    return new Promise(resolve => {
        const overlay = document.getElementById("modal-overlay");
        const text = document.getElementById("modal-text");
        const btnConfirm = document.getElementById("modal-confirm");
        const btnCancel = document.getElementById("modal-cancel");

        text.textContent = message;
        overlay.style.display = "flex";

        const cleanup = (result) => {
            overlay.style.display = "none";
            btnConfirm.onclick = null;
            btnCancel.onclick = null;
            resolve(result);
        };

        btnConfirm.onclick = () => cleanup(true);
        btnCancel.onclick = () => cleanup(false);
    });
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
        await loadVendorsForExchange();

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
                <td class="expiration-col ${entry.expiration_date === '-' ? 'center-dash' : ''}">
                    ${entry.expiration_date}
                </td>
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

        updateExchangeOptions();

    } catch (err) {
        console.error(err);
    }
}

function updateExchangeOptions() {
    const totalPoints = Number(document.getElementById("total-points").textContent);
    const amountSelect = document.getElementById("exchange-amount");

    const costs = {
        5: 40000,
        10: 75000,
        15: 110000,
        25: 180000,
        50: 350000
    };

    [...amountSelect.options].forEach(opt => {
        const cost = costs[opt.value];
        if (totalPoints < cost) {
            opt.disabled = true;
            opt.textContent = `$${opt.value} Credit — Need ${cost} pts`;
        } else {
            opt.disabled = false;
            opt.textContent = `$${opt.value} Credit`;
        }
    });
}

async function loadVendorsForExchange() {
    const res = await fetch(API_VENDORS);
    if (!res.ok) return;

    const data = await res.json();
    const dropdown = document.getElementById("exchange-vendor");

    dropdown.innerHTML = `<option value="" disabled selected>Select…</option>`;

    data.forEach(v => {
        const opt = document.createElement("option");
        opt.value = v.vendor_id;
        opt.textContent = v.name;
        dropdown.appendChild(opt);
    });
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
                <td>${Number(item.amount).toFixed(2)}</td>
                <td>${item.date || ""}</td>
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

const exchangeForm = document.getElementById("exchange-form");
const exchangeMessage = document.getElementById("exchange-message");

exchangeForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const vendor_id = document.getElementById("exchange-vendor").value;
    const credit_amount_raw = document.getElementById("exchange-amount").value;
    
    if (!vendor_id) {
        exchangeMessage.style.color = "red";
        exchangeMessage.textContent = "Please choose a vendor.";
        return;
    }
    
    if (!credit_amount_raw) {
        exchangeMessage.style.color = "red";
        exchangeMessage.textContent = "Please choose a credit amount.";
        return;
    }
    
    const credit_amount = parseInt(credit_amount_raw);    

    const confirmed = await showModal(`Are you sure you want to redeem $${credit_amount} store credit?`);
    if (!confirmed) return;    

    const res = await fetch("/api/exchange/", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ vendor_id, credit_amount })
    });

    const data = await res.json();

    if (!res.ok) {
        exchangeMessage.style.color = "red";
        exchangeMessage.textContent = data.error;
        return;
    }

    exchangeMessage.style.color = "green";
    exchangeMessage.textContent = data.message;

    // Refresh UI
    await loadRewards();
    await loadAccount();
});
