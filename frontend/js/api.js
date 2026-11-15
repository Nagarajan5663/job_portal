/* ==========================================================
   Job Portal — API helper (shared across all pages)
   ========================================================== */

// Change this if your backend runs on a different host/port
const API_BASE_URL = "http://127.0.0.1:8001";

const Auth = {
  getToken: () => localStorage.getItem("jp_token"),
  getRole: () => localStorage.getItem("jp_role"),
  getUserId: () => localStorage.getItem("jp_user_id"),
  getName: () => localStorage.getItem("jp_name"),
  isLoggedIn: () => !!localStorage.getItem("jp_token"),

  saveSession(data) {
    localStorage.setItem("jp_token", data.access_token);
    localStorage.setItem("jp_role", data.role);
    localStorage.setItem("jp_user_id", data.user_id);
    localStorage.setItem("jp_name", data.name);
  },

  logout() {
    localStorage.clear();
    window.location.href = "/login.html";
  },

  /** Redirect to login if not authenticated, or to the correct dashboard if role mismatched. */
  requireRole(requiredRole) {
    if (!this.isLoggedIn()) {
      window.location.href = "/login.html";
      return;
    }
    if (requiredRole && this.getRole() !== requiredRole) {
      alert("You do not have access to that page.");
      window.location.href = "/index.html";
    }
  },
};

/**
 * Generic fetch wrapper that attaches the JWT and parses JSON,
 * throwing a readable Error on non-2xx responses.
 */
async function apiRequest(path, { method = "GET", body = null, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth && Auth.getToken()) {
    headers["Authorization"] = `Bearer ${Auth.getToken()}`;
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (networkErr) {
    throw new Error("Cannot reach the server. Is the backend running on " + API_BASE_URL + "?");
  }

  if (response.status === 204) return null;

  let data;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    if (response.status === 401) {
      // Token invalid/expired -> force re-login
      localStorage.clear();
      window.location.href = "/login.html";
      return;
    }
    const detail = data?.detail;
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg).join(", ")
      : detail || `Request failed (${response.status})`;
    throw new Error(message);
  }

  return data;
}

const api = {
  // Auth
  register: (payload) => apiRequest("/api/auth/register", { method: "POST", body: payload, auth: false }),
  login: (payload) => apiRequest("/api/auth/login", { method: "POST", body: payload, auth: false }),

  // Public/job seeker job browsing
  listJobs: (params = {}) => {
    const qs = new URLSearchParams(Object.fromEntries(Object.entries(params).filter(([, v]) => v)));
    return apiRequest(`/api/jobs?${qs.toString()}`);
  },
  getJob: (id) => apiRequest(`/api/jobs/${id}`),

  // Job seeker
  getMyProfile: () => apiRequest("/api/jobseeker/profile"),
  updateMyProfile: (payload) => apiRequest("/api/jobseeker/profile", { method: "PUT", body: payload }),
  applyToJob: (jobId, payload) => apiRequest(`/api/jobseeker/apply/${jobId}`, { method: "POST", body: payload }),
  myApplications: () => apiRequest("/api/jobseeker/applications"),
  withdrawApplication: (id) => apiRequest(`/api/jobseeker/applications/${id}`, { method: "DELETE" }),

  // Recruiter
  getMyCompany: () => apiRequest("/api/recruiter/company"),
  updateMyCompany: (payload) => apiRequest("/api/recruiter/company", { method: "PUT", body: payload }),
  createJob: (payload) => apiRequest("/api/recruiter/jobs", { method: "POST", body: payload }),
  myPostedJobs: () => apiRequest("/api/recruiter/jobs"),
  updateJob: (id, payload) => apiRequest(`/api/recruiter/jobs/${id}`, { method: "PUT", body: payload }),
  deleteJob: (id) => apiRequest(`/api/recruiter/jobs/${id}`, { method: "DELETE" }),
  viewApplicants: (jobId) => apiRequest(`/api/recruiter/jobs/${jobId}/applicants`),
  setApplicationStatus: (appId, status) =>
    apiRequest(`/api/recruiter/applications/${appId}/status`, { method: "PUT", body: { status } }),

  // Admin
  dashboardStats: () => apiRequest("/api/admin/dashboard"),
  listUsers: (role = "") => apiRequest(`/api/admin/users${role ? `?role=${role}` : ""}`),
  toggleUserActive: (id) => apiRequest(`/api/admin/users/${id}/toggle-active`, { method: "PUT" }),
  deleteUser: (id) => apiRequest(`/api/admin/users/${id}`, { method: "DELETE" }),
  adminListJobs: () => apiRequest("/api/admin/jobs"),
  adminDeleteJob: (id) => apiRequest(`/api/admin/jobs/${id}`, { method: "DELETE" }),
  adminListApplications: () => apiRequest("/api/admin/applications"),
};

/** Small helper to render an error message inside a banner element. */
function showBanner(elId, message, type = "error") {
  const el = document.getElementById(elId);
  if (!el) return;
  el.textContent = message;
  el.style.display = message ? "block" : "none";
  el.className = type === "error" ? "error-banner" : "success-banner";
  if (message) el.style.display = "block";
}

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function formatDate(iso) {
  if (!iso) return "-";
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}
