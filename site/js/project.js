/* Renders a single project detail page from ?p=<slug>. */
(function () {
  var P = window.PORTFOLIO || {};
  var projects = P.projects || [];
  var profile = P.profile || {};

  document.getElementById("brand-name").textContent = profile.name || "";
  document.getElementById("foot-name").textContent = profile.name || "";

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function param(name) {
    var m = new RegExp("[?&]" + name + "=([^&]+)").exec(location.search);
    return m ? decodeURIComponent(m[1]) : null;
  }

  var slug = param("p");
  var p = projects.filter(function (x) { return x.slug === slug; })[0];
  var mount = document.getElementById("proj");

  if (!p) {
    mount.innerHTML =
      '<div class="wrap nf"><h1>Project not found</h1>' +
      '<p><a class="btn primary" href="index.html">&#8592; Back to portfolio</a></p></div>';
    return;
  }

  document.title = p.title + " — " + (profile.name || "Portfolio");

  var tags = (p.tags || []).map(function (t) { return '<span>' + esc(t) + '</span>'; }).join("");
  var badge = p.status ? '<span class="badge">' + esc(p.status) + '</span>' : '';

  var highlights = (p.highlights || []).length
    ? '<div class="block"><h2>Highlights</h2><ul class="hl">' +
        p.highlights.map(function (h) { return '<li>' + esc(h) + '</li>'; }).join("") +
      '</ul></div>'
    : '';

  var role = p.role
    ? '<div class="block"><div class="role-box"><div class="lbl">My Role</div><p>' + esc(p.role) + '</p></div></div>'
    : '';

  // Interactive 3D model block (only if the project defines a `model:` STEP path)
  var viewer = p.model
    ? '<div class="block"><h2>3D Model</h2>' +
        '<div class="viewer3d" id="viewer3d" data-model="' + esc(p.model) + '">' +
          '<div class="viewer3d-cta">' +
            '<div class="v3d-icon">&#9788;</div>' +
            '<button class="btn primary" id="viewer3d-load" type="button">Load interactive 3D model</button>' +
            '<div class="v3d-hint">Drag to rotate &middot; scroll to zoom. Loads a CAD file in your browser — may take a few seconds.</div>' +
            '<a class="v3d-dl" href="' + esc(p.model) + '" download>or download the STEP file &#8595;</a>' +
          '</div>' +
        '</div>' +
      '</div>'
    : '';

  var sections = (p.sections || []).map(function (s) {
    return '<div class="block"><h2>' + esc(s.heading) + '</h2><p>' + esc(s.body) + '</p></div>';
  }).join("");

  var gallery = (p.gallery || []).length
    ? '<div class="block"><h2>Gallery</h2><div class="gallery">' +
        p.gallery.map(function (g) {
          return '<figure><img src="' + esc(g.src) + '" alt="' + esc(g.caption || p.title) + '" loading="lazy">' +
            (g.caption ? '<figcaption>' + esc(g.caption) + '</figcaption>' : '') + '</figure>';
        }).join("") +
      '</div></div>'
    : '';

  var specs = (p.specs || []).length
    ? '<div class="side-card"><h3>Specs</h3><div class="specs">' +
        p.specs.map(function (s) {
          return '<div class="spec"><span class="k">' + esc(s.label) + '</span><span class="v">' + esc(s.value) + '</span></div>';
        }).join("") +
      '</div>'
    : '';

  var files = (p.files || []).length
    ? '<div class="side-card"><h3>Files &amp; Downloads</h3><div class="dl">' +
        p.files.map(function (f) {
          var kind = f.kind || "file";
          var label = kind === "pdf" ? "PDF" : kind === "step" ? "3D" : "DL";
          return '<a href="' + esc(f.href) + '" target="_blank" rel="noopener">' +
            '<span class="ic ' + esc(kind) + '">' + label + '</span>' +
            '<span class="nm">' + esc(f.label) + '</span><span class="arr2">&#8595;</span></a>';
        }).join("") +
      '</div></div>'
    : '';

  var extLinks = (p.links || []).length
    ? '<div class="side-card"><h3>Links</h3><div class="dl">' +
        p.links.map(function (l) {
          return '<a href="' + esc(l.href) + '" target="_blank" rel="noopener">' +
            '<span class="ic file">&#8599;</span><span class="nm">' + esc(l.label) + '</span></a>';
        }).join("") +
      '</div></div>'
    : '';

  mount.innerHTML =
    '<div class="wrap proj-head">' +
      '<a class="back" href="index.html#work">&#8592; All projects</a>' +
      '<div class="meta">' + esc(p.org || "") + (p.date ? ' &middot; ' + esc(p.date) : '') + badge + '</div>' +
      '<h1>' + esc(p.title) + '</h1>' +
      (p.subtitle ? '<div class="subtitle">' + esc(p.subtitle) + '</div>' : '') +
      '<div class="proj-tags">' + tags + '</div>' +
    '</div>' +
    '<div class="wrap proj-layout">' +
      '<div class="proj-main">' +
        (p.summary ? '<p class="proj-summary">' + esc(p.summary) + '</p>' : '') +
        role + highlights + viewer + sections + gallery +
      '</div>' +
      '<aside class="side">' + specs + files + extLinks + '</aside>' +
    '</div>';

  /* lightbox for gallery images */
  var lb = document.getElementById("lightbox");
  var lbImg = lb.querySelector("img");
  mount.addEventListener("click", function (e) {
    var img = e.target.closest(".gallery img");
    if (img) { lbImg.src = img.src; lb.classList.add("open"); }
  });
  lb.addEventListener("click", function () { lb.classList.remove("open"); lbImg.src = ""; });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") lb.classList.remove("open"); });

  /* ---- 3D STEP viewer: load on demand when the user clicks the button ---- */
  var loadBtn = document.getElementById("viewer3d-load");
  if (loadBtn) {
    loadBtn.addEventListener("click", function () {
      var box = document.getElementById("viewer3d");
      var url = box.getAttribute("data-model");
      box.classList.add("loading");
      box.innerHTML = '<div class="v3d-status" id="v3d-status">Starting…</div>';
      var statusEl = document.getElementById("v3d-status");
      var setStatus = function (t) { if (statusEl) statusEl.textContent = t || ""; };

      // Resolve relative to the page (works at site root and under a
      // GitHub Pages /<repo>/ subpath alike).
      var viewerUrl = new URL("js/step-viewer.js", document.baseURI).href;
      import(viewerUrl)
        .then(function (mod) { return mod.mountViewer(box, url, setStatus); })
        .then(function (handle) {
          box.classList.remove("loading");
          box.classList.add("ready");
          // small reset-view control
          var reset = document.createElement("button");
          reset.className = "v3d-reset"; reset.type = "button"; reset.textContent = "Reset view";
          reset.addEventListener("click", function () { handle.reset(); });
          box.appendChild(reset);
        })
        .catch(function (err) {
          box.classList.remove("loading");
          box.innerHTML = '<div class="v3d-error">Couldn’t load the 3D model.<br><span>' +
            esc(err && err.message ? err.message : String(err)) + '</span><br>' +
            '<a class="btn" href="' + esc(url) + '" download>Download the STEP file instead &#8595;</a></div>';
        });
    });
  }
})();
