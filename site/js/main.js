/* Renders the homepage from window.PORTFOLIO (see js/data.js). */
(function () {
  var P = window.PORTFOLIO;
  if (!P) { console.error("PORTFOLIO data not found"); return; }
  var profile = P.profile, projects = P.projects || [];

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  /* ---- Hero ---- */
  var hero = document.getElementById("hero");
  var firstName = (profile.name || "").split(" ")[0];
  var lastName = (profile.name || "").split(" ").slice(1).join(" ");
  hero.innerHTML =
    '<div class="reveal in">' +
      '<div class="eyebrow">' + esc(profile.role || "") + '</div>' +
      '<h1>' + esc(firstName) + ' <span class="accent">' + esc(lastName) + '</span></h1>' +
      '<p class="lead">' + esc(profile.tagline || "") + '</p>' +
      '<div class="meta">' +
        (profile.location ? '&#9679; <span>' + esc(profile.location) + '</span>&nbsp;&nbsp;&nbsp;' : '') +
        (profile.email ? '&#9993; <span>' + esc(profile.email) + '</span>' : '') +
      '</div>' +
      heroButtons(profile.links || {}) +
    '</div>';

  function heroButtons(links) {
    var b = '<div class="btns">';
    b += '<a class="btn primary" href="#work">View Projects &#8595;</a>';
    if (links.email)    b += '<a class="btn" href="mailto:' + esc(links.email) + '">Email</a>';
    if (links.linkedin) b += '<a class="btn" href="' + esc(links.linkedin) + '" target="_blank" rel="noopener">LinkedIn</a>';
    if (links.github)   b += '<a class="btn" href="' + esc(links.github) + '" target="_blank" rel="noopener">GitHub</a>';
    if (links.resume)   b += '<a class="btn" href="' + esc(links.resume) + '" target="_blank" rel="noopener">Résumé</a>';
    return b + '</div>';
  }

  /* ---- Projects (grouped into sections by `group`) ---- */
  function cardHTML(p) {
    var tags = (p.tags || []).slice(0, 4).map(function (t) { return '<span>' + esc(t) + '</span>'; }).join("");
    var badge = p.status ? '<span class="badge">' + esc(p.status) + '</span>' : '';
    return '' +
      '<a class="card reveal" href="project.html?p=' + encodeURIComponent(p.slug) + '">' +
        '<div class="card-thumb"><img src="' + esc(p.thumb) + '" alt="' + esc(p.title) + '" loading="lazy"></div>' +
        '<div class="card-body">' +
          '<div class="card-meta">' + esc(p.org || "") + (p.date ? ' &middot; ' + esc(p.date) : '') + badge + '</div>' +
          '<h3>' + esc(p.title) + '</h3>' +
          (p.subtitle ? '<div class="sub">' + esc(p.subtitle) + '</div>' : '') +
          '<div class="desc">' + esc(p.summary || "") + '</div>' +
          '<div class="card-tags">' + tags + '</div>' +
          '<span class="card-cta">View project <span class="arr">&#8594;</span></span>' +
        '</div>' +
      '</a>';
  }

  // Build the ordered list of group names: configured groups first, then any
  // leftover groups found on projects, then an "Other" bucket for ungrouped.
  var configured = (P.groups || []);
  var order = configured.map(function (g) { return g.name; });
  var blurbs = {};
  configured.forEach(function (g) { blurbs[g.name] = g.blurb || ""; });

  projects.forEach(function (p) {
    var g = p.group || "Other";
    if (order.indexOf(g) === -1) order.push(g);
  });

  var groupsWrap = document.getElementById("project-groups");
  groupsWrap.innerHTML = order.map(function (name) {
    var inGroup = projects.filter(function (p) { return (p.group || "Other") === name; });
    if (!inGroup.length) return "";
    var slug = name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    return '<div class="proj-group reveal" id="grp-' + slug + '">' +
        '<div class="group-head">' +
          '<h3>' + esc(name) + '</h3>' +
          (blurbs[name] ? '<p>' + esc(blurbs[name]) + '</p>' : '') +
        '</div>' +
        '<div class="grid">' + inGroup.map(cardHTML).join("") + '</div>' +
      '</div>';
  }).join("");

  /* ---- About ---- */
  var skills = (profile.skills || []).map(function (s, i) {
    return '<span class="chip' + (i < 4 ? ' solid' : '') + '">' + esc(s) + '</span>';
  }).join("");
  document.getElementById("about-body").innerHTML =
    '<div><p>' + esc(profile.about || "") + '</p></div>' +
    '<div><div class="skills-title">Skills &amp; Tools</div><div class="chips">' + skills + '</div></div>';

  /* ---- Contact ---- */
  var links = profile.links || {};
  var cbtns = '<div class="btns">';
  if (links.email)    cbtns += '<a class="btn primary" href="mailto:' + esc(links.email) + '">Send an Email</a>';
  if (links.linkedin) cbtns += '<a class="btn" href="' + esc(links.linkedin) + '" target="_blank" rel="noopener">LinkedIn</a>';
  if (links.github)   cbtns += '<a class="btn" href="' + esc(links.github) + '" target="_blank" rel="noopener">GitHub</a>';
  cbtns += '</div>';
  document.getElementById("contact-body").innerHTML =
    '<h2>Let&#39;s build something.</h2>' +
    '<p>I&#39;m always happy to talk hardware, embedded systems, or motorsport electronics.</p>' +
    cbtns;

  /* ---- Misc ---- */
  document.getElementById("brand-name").textContent = profile.name || "";
  document.getElementById("foot-name").textContent = profile.name || "";
  document.getElementById("year").textContent = new Date().getFullYear();
  document.title = (profile.name || "Portfolio") + " — " + (profile.role || "");

  /* ---- Reveal on scroll ---- */
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
  }, { threshold: 0.12 });
  document.querySelectorAll(".reveal").forEach(function (el) { io.observe(el); });
})();
