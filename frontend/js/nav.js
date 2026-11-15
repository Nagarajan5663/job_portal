/* ==========================================================
   Renders the top navbar based on logged-in role.
   Include after api.js. Requires <div id="navbar"></div> in the page.
   ========================================================== */
function renderNavbar(activePage = "") {
  const target = document.getElementById("navbar");
  if (!target) return;

  const loggedIn = Auth.isLoggedIn();
  const role = Auth.getRole();

  let links = "";
  if (loggedIn) {
    if (role === "jobseeker") {
      links = `
        <a href="/jobseeker/jobs.html" class="${activePage === "jobs" ? "active" : ""}">Browse Jobs</a>
        <a href="/jobseeker/applications.html" class="${activePage === "applications" ? "active" : ""}">My Applications</a>
        <a href="/jobseeker/profile.html" class="${activePage === "profile" ? "active" : ""}">My Profile</a>`;
    } else if (role === "recruiter") {
      links = `
        <a href="/recruiter/dashboard.html" class="${activePage === "dashboard" ? "active" : ""}">My Jobs</a>
        <a href="/recruiter/post_job.html" class="${activePage === "post" ? "active" : ""}">Post a Job</a>
        <a href="/recruiter/company.html" class="${activePage === "company" ? "active" : ""}">Company Profile</a>`;
    } else if (role === "admin") {
      links = `<a href="/admin/dashboard.html" class="${activePage === "dashboard" ? "active" : ""}">Dashboard</a>`;
    }
  }

  target.innerHTML = `
    <nav class="navbar">
      <div class="container">
        <a href="/index.html" class="brand">💼 JobPortal</a>
        <div class="nav-links">
          ${links}
        </div>
        <div class="nav-user">
          ${
            loggedIn
              ? `<span class="badge-role">${role}</span>
                 <span class="text-muted" style="font-size:0.85rem">${escapeHtml(Auth.getName())}</span>
                 <button class="btn btn-outline btn-sm" onclick="Auth.logout()">Logout</button>`
              : `<a href="/login.html" class="btn btn-outline btn-sm">Login</a>
                 <a href="/register.html" class="btn btn-primary btn-sm">Register</a>`
          }
        </div>
      </div>
    </nav>`;
}
