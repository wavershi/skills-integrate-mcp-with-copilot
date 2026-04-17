document.addEventListener("DOMContentLoaded", () => {
  const registerForm = document.getElementById("register-form");
  const loginForm = document.getElementById("login-form");
  const logoutButton = document.getElementById("logout-button");
  const authContainer = document.getElementById("auth-container");
  const appContainer = document.getElementById("app-container");
  const clubsList = document.getElementById("clubs-list");
  const membershipList = document.getElementById("membership-list");
  const userSummary = document.getElementById("user-summary");
  const messageDiv = document.getElementById("message");

  const TOKEN_KEY = "mh_auth_token";
  let token = localStorage.getItem(TOKEN_KEY) || "";
  let currentUser = null;

  function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");

    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 4500);
  }

  async function apiRequest(path, options = {}) {
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    };

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(path, {
      ...options,
      headers,
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Request failed");
    }

    return data;
  }

  function setAuthenticatedUI(isAuthenticated) {
    authContainer.classList.toggle("hidden", isAuthenticated);
    appContainer.classList.toggle("hidden", !isAuthenticated);
  }

  function renderMemberships(memberships) {
    membershipList.innerHTML = "";
    if (memberships.length === 0) {
      const emptyItem = document.createElement("li");
      emptyItem.textContent = "No memberships yet";
      membershipList.appendChild(emptyItem);
      return;
    }

    memberships.forEach((clubName) => {
      const item = document.createElement("li");
      item.textContent = clubName;
      membershipList.appendChild(item);
    });
  }

  function renderClubs(clubs) {
    clubsList.innerHTML = "";

    Object.entries(clubs).forEach(([name, details]) => {
      const card = document.createElement("div");
      card.className = "activity-card";

      const buttonState = details.membership_state;
      const isJoined = buttonState === "Joined";

      card.innerHTML = `
        <h4>${name}</h4>
        <p>${details.description}</p>
        <button class="join-btn" data-club="${name}" ${isJoined ? "disabled" : ""}>
          ${buttonState}
        </button>
      `;

      clubsList.appendChild(card);
    });

    document.querySelectorAll(".join-btn").forEach((button) => {
      button.addEventListener("click", async () => {
        const clubName = button.getAttribute("data-club");
        try {
          const result = await apiRequest(`/clubs/${encodeURIComponent(clubName)}/join`, {
            method: "POST",
          });
          showMessage(result.message, "success");
          await loadProtectedData();
        } catch (error) {
          showMessage(error.message, "error");
        }
      });
    });
  }

  async function loadProtectedData() {
    const me = await apiRequest("/auth/me", { method: "GET" });
    const clubs = await apiRequest("/clubs", { method: "GET" });
    const memberships = await apiRequest("/memberships", { method: "GET" });

    currentUser = me;
    userSummary.textContent = `Logged in as ${me.email} (${me.role})`;
    renderClubs(clubs);
    renderMemberships(memberships.memberships || []);
  }

  async function restoreSession() {
    if (!token) {
      setAuthenticatedUI(false);
      return;
    }

    try {
      setAuthenticatedUI(true);
      await loadProtectedData();
    } catch (error) {
      token = "";
      currentUser = null;
      localStorage.removeItem(TOKEN_KEY);
      setAuthenticatedUI(false);
      showMessage("Your session expired. Please sign in again.", "info");
    }
  }

  registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = {
      email: document.getElementById("register-email").value.trim(),
      password: document.getElementById("register-password").value,
      role: document.getElementById("register-role").value,
    };

    try {
      const result = await apiRequest("/auth/register", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      showMessage(result.message, "success");
      registerForm.reset();
    } catch (error) {
      showMessage(error.message, "error");
    }
  });

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
      email: document.getElementById("login-email").value.trim(),
      password: document.getElementById("login-password").value,
    };

    try {
      const result = await apiRequest("/auth/login", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      token = result.token;
      localStorage.setItem(TOKEN_KEY, token);
      setAuthenticatedUI(true);
      await loadProtectedData();
      showMessage("Login successful", "success");
      loginForm.reset();
    } catch (error) {
      showMessage(error.message, "error");
    }
  });

  logoutButton.addEventListener("click", async () => {
    try {
      await apiRequest("/auth/logout", { method: "POST" });
    } catch (error) {
      console.error("Logout failed:", error.message);
    } finally {
      token = "";
      currentUser = null;
      localStorage.removeItem(TOKEN_KEY);
      setAuthenticatedUI(false);
      userSummary.textContent = "";
      clubsList.innerHTML = "<p>Please sign in.</p>";
      membershipList.innerHTML = "";
      showMessage("Logged out", "info");
    }
  });

  restoreSession();
});
