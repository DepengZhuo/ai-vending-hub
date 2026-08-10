/* ============================================================
   include.js - Shared component injector
   Responsibilities:
   1) Reads data-root from <body> (page depth, e.g. "" or "../").
   2) Injects components/nav.html, footer.html, lead-modal.html into
      the page placeholders (#nav-placeholder, etc.).
   3) Emits "components-injected" when all three are in place.
   4) Marks the current section in the nav.
   5) Generates the canonical link from SITE_CONFIG.domain.
   6) Local preview fallback: when double-clicked via file:// the browser
      blocks fetch(), so the built-in FALLBACK_* strings are used instead.
   NOTE: the FALLBACK_* strings are regenerated from components/*.html by
   work/sync_components.py — keep that script and these files in sync.
   ============================================================ */

const SITE_CONFIG = {
  domain: "https://depengzhuo.github.io/ai-vending-hub", // 上线地址；以后绑定自定义域名时替换
};

/* ========== Local preview fallbacks (keep in sync with components/) ========== */

const FALLBACK_NAV = `<!-- ============================================================
     Shared component: site navigation (nav.html)
     Injected by assets/js/include.js into <div id="nav-placeholder">.
     Edit links below to update the menu site-wide.
     Note:
     - Links start with "/" (root-relative); include.js rewrites them
       to relative paths for the current page depth.
     - Book a Demo uses data-open-modal -> opens the shared Lead modal.
     ============================================================ -->

<!-- Announcement bar: site-wide updates (edit here to change everywhere) -->
<div class="announcement-bar bg-[#0b1220] text-white">
  <div class="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-2 text-[0.8rem] sm:px-6 lg:px-8">
    <p class="min-w-0 truncate">
      <span class="font-mono text-[0.68rem] font-semibold uppercase tracking-wider text-blue-300">New</span>
      <a href="/reports/2026-smart-retail-trends.html" class="ml-2 font-medium text-gray-200 hover:text-white">
        2026 Smart Retail Trends — now live
      </a>
    </p>
    <a href="/resources/roi-calculator.html" class="hidden shrink-0 font-semibold text-blue-200 hover:text-white sm:inline">
      ROI Calculator <i class="fa-solid fa-arrow-right ml-1 text-[0.7rem]"></i>
    </a>
  </div>
</div>

<header id="site-header" class="sticky top-0 z-40 w-full border-b border-gray-100 bg-white/90 backdrop-blur-md">
  <nav class="mx-auto flex h-16 max-w-7xl items-center justify-between gap-6 px-4 sm:px-6 lg:h-[72px] lg:px-8" aria-label="Main navigation">

    <!-- Brand -->
    <a href="/" class="flex shrink-0 items-center gap-2.5" aria-label="AI Vending Hub home">
      <span class="flex h-9 w-9 items-center justify-center rounded-[10px] bg-primary text-white shadow-[0_6px_18px_rgba(22,93,255,0.35)]">
        <i class="fa-solid fa-cube"></i>
      </span>
      <span class="text-lg font-bold tracking-tight text-gray-900">AI Vending Hub</span>
    </a>

    <!-- Desktop nav: one line -->
    <div class="hidden items-center gap-1 text-[0.9rem] font-medium text-gray-600 xl:flex">
      <a href="/" class="nav-link transition" data-nav="/">Home</a>
      <a href="/news/" class="nav-link transition" data-nav="/news/">News</a>
      <a href="/knowledge/" class="nav-link transition" data-nav="/knowledge/">Knowledge Base</a>
      <a href="/reviews/" class="nav-link transition" data-nav="/reviews/">Reviews</a>
      <a href="/companies/" class="nav-link transition" data-nav="/companies/">Companies</a>
      <a href="/deployment-guides/" class="nav-link transition" data-nav="/deployment-guides/">Guides</a>
      <a href="/resources/" class="nav-link transition" data-nav="/resources/">Resources</a>
    </div>

    <!-- Right: CTA + mobile toggle -->
    <div class="flex items-center gap-2.5">
      <button type="button" data-open-modal class="btn-primary hidden !py-2.5 text-sm md:inline-flex">
        <i class="fa-solid fa-calendar-check"></i> Book a Demo
      </button>
      <button id="nav-toggle" type="button"
              class="flex h-10 w-10 items-center justify-center rounded-[10px] text-gray-700 hover:bg-gray-100 xl:hidden"
              aria-label="Open menu" aria-controls="mobile-menu" aria-expanded="false">
        <i class="fa-solid fa-bars text-xl"></i>
      </button>
    </div>
  </nav>

  <!-- Mobile menu -->
  <div id="mobile-menu" class="border-t border-gray-100 bg-white px-4 text-[0.95rem] font-medium text-gray-700 xl:hidden">
    <a href="/" class="block rounded-[10px] px-3 py-2.5 hover:bg-gray-50">Home</a>
    <a href="/news/" class="block rounded-[10px] px-3 py-2.5 hover:bg-gray-50">News</a>
    <a href="/knowledge/" class="block rounded-[10px] px-3 py-2.5 hover:bg-gray-50">Knowledge Base</a>
    <a href="/reviews/" class="block rounded-[10px] px-3 py-2.5 hover:bg-gray-50">Reviews</a>
    <a href="/companies/" class="block rounded-[10px] px-3 py-2.5 hover:bg-gray-50">Companies</a>
    <a href="/deployment-guides/" class="block rounded-[10px] px-3 py-2.5 hover:bg-gray-50">Guides</a>
    <a href="/resources/" class="block rounded-[10px] px-3 py-2.5 hover:bg-gray-50">Resources</a>
    <div class="border-t border-gray-100 pt-3">
      <button type="button" data-open-modal class="btn-primary w-full">
        <i class="fa-solid fa-calendar-check"></i> Book a Demo
      </button>
    </div>
  </div>
</header>`;

const FALLBACK_FOOTER = `<!-- ============================================================
     Shared component: site footer (footer.html)
     Injected by assets/js/include.js into <div id="footer-placeholder">.
     Layout: brand + mission on row 1 (left / right), link columns
     on row 2, legal bar on row 3.
     ============================================================ -->
<footer class="bg-[#0b1220] text-gray-400">
  <div class="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8 lg:py-16">

    <!-- Row 1: brand on the left, mission statement on the right -->
    <div class="grid items-end gap-8 lg:grid-cols-[1fr_1.4fr] lg:gap-16">
      <div>
        <a href="/" class="flex items-center gap-2.5" aria-label="AI Vending Hub home">
          <span class="flex h-9 w-9 items-center justify-center rounded-[10px] bg-primary text-white">
            <i class="fa-solid fa-cube"></i>
          </span>
          <span class="text-lg font-bold text-white">AI Vending Hub</span>
        </a>
        <p class="mt-4 max-w-md text-base font-semibold leading-7 text-white sm:text-lg">
          The independent resource for Smart Retail &amp; AI Vending.
        </p>
      </div>
      <p class="max-w-2xl text-sm leading-7 text-gray-400 lg:justify-self-end lg:text-right">
        Plain-English guides, neutral comparisons, and market intelligence for operators,
        venue owners, and investors planning unattended retail in North America.
      </p>
    </div>

    <!-- Row 2: link columns -->
    <div class="mt-12 grid grid-cols-2 gap-x-8 gap-y-10 border-t border-white/10 pt-12 sm:grid-cols-4 lg:mt-14 lg:pt-14">
      <div>
        <h3 class="footer-col-title">Explore</h3>
        <ul class="mt-4 space-y-2.5 text-sm">
          <li><a href="/" class="footer-link">Home</a></li>
          <li><a href="/news/" class="footer-link">Industry News</a></li>
          <li><a href="/knowledge/" class="footer-link">Knowledge Base</a></li>
          <li><a href="/reviews/" class="footer-link">Reviews &amp; Comparisons</a></li>
        </ul>
      </div>
      <div>
        <h3 class="footer-col-title">Plan</h3>
        <ul class="mt-4 space-y-2.5 text-sm">
          <li><a href="/resources/" class="footer-link">Buyer's Guides</a></li>
          <li><a href="/resources/roi-calculator.html" class="footer-link">ROI Calculator</a></li>
          <li><a href="/deployment-guides/" class="footer-link">Deployment Guides</a></li>
          <li><a href="/reports/" class="footer-link">Industry Reports</a></li>
        </ul>
      </div>
      <div>
        <h3 class="footer-col-title">Directory</h3>
        <ul class="mt-4 space-y-2.5 text-sm">
          <li><a href="/companies/" class="footer-link">Company Directory</a></li>
          <li><a href="/companies/365-retail-markets.html" class="footer-link">365 Retail Markets</a></li>
          <li><a href="/companies/haha.html" class="footer-link">Haha Vending</a></li>
          <li><a href="/companies/sandstar.html" class="footer-link">SandStar</a></li>
        </ul>
      </div>
      <div>
        <h3 class="footer-col-title">Hub</h3>
        <ul class="mt-4 space-y-2.5 text-sm">
          <li><a href="/about.html" class="footer-link">About</a></li>
          <li><a href="/contact.html" class="footer-link">Contact</a></li>
          <li><a href="/privacy.html" class="footer-link">Privacy Policy</a></li>
          <li><a href="/terms.html" class="footer-link">Terms of Use</a></li>
        </ul>
      </div>
    </div>

    <!-- Bottom bar -->
    <div class="mt-10 flex flex-col items-start justify-between gap-3 border-t border-white/10 pt-7 text-xs text-gray-500 sm:flex-row sm:items-center lg:mt-12">
      <p>&copy; 2026 AI Vending Hub. All rights reserved.</p>
      <p class="font-mono tracking-wide">Independent media. Not affiliated with any vendor.</p>
    </div>
  </div>
</footer>
`;

const FALLBACK_MODAL = `<div id="lead-modal" class="fixed inset-0 z-50 hidden items-center justify-center p-4" aria-hidden="true" role="dialog" aria-modal="true">
  <!-- Backdrop: click to close -->
  <div class="absolute inset-0 bg-[#0b1220]/70 backdrop-blur-sm" data-modal-close></div>

  <!-- Modal body -->
  <div data-modal-body class="relative w-full max-w-xl overflow-y-auto rounded-2xl bg-white p-6 shadow-2xl sm:p-7">
    <!-- Close -->
    <button type="button" data-modal-close
            class="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            aria-label="Close">
      <i class="fa-solid fa-xmark text-lg"></i>
    </button>

    <span class="chip">Talk to us</span>
    <h2 class="mt-2.5 text-xl font-extrabold tracking-tight text-gray-900 sm:text-2xl">Book a Demo</h2>
    <p class="mt-1.5 text-sm leading-6 text-gray-600">
      Tell us about your project — we'll reply within one business day.
    </p>

    <form id="lead-form" data-lead-form data-formspree-id="mgogqyoa"
          class="mt-5 space-y-3" action="https://formspree.io/f/mgogqyoa" method="POST">

      <input type="text" name="_gotcha" class="hidden" tabindex="-1" autocomplete="off" />
      <input type="hidden" name="_subject" value="Book a Demo / Contact Us - AI Vending Hub" />

      <div data-fs-success class="hidden rounded-lg bg-green-50 px-3 py-2 text-sm text-green-700">
        Thanks! We will get back to you within 1 business day.
      </div>
      <div data-fs-error class="hidden rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600"></div>

      <div class="grid gap-3 sm:grid-cols-2">
        <div>
          <label for="lead-name" class="field-label">Name *</label>
          <input id="lead-name" type="text" name="name" data-fs-field required class="field-input field-input-sm" placeholder="Jane Cooper" />
        </div>
        <div>
          <label for="lead-email" class="field-label">Work Email *</label>
          <input id="lead-email" type="email" name="email" data-fs-field required class="field-input field-input-sm" placeholder="jane@company.com" />
          <span data-fs-error="email" class="mt-1 block text-xs text-red-600"></span>
        </div>
      </div>

      <div class="grid gap-3 sm:grid-cols-2">
        <div>
          <label for="lead-company" class="field-label">Company</label>
          <input id="lead-company" type="text" name="company" data-fs-field class="field-input field-input-sm" placeholder="Company name" />
        </div>
        <div>
          <label for="lead-interest" class="field-label">I'm interested in</label>
          <select id="lead-interest" name="interest" data-fs-field class="field-input field-input-sm">
            <option value="demo">Book a Demo</option>
            <option value="quote">Get a Quote</option>
            <option value="partnership">Partnership</option>
            <option value="media">Media / Editorial</option>
          </select>
        </div>
      </div>

      <div>
        <label for="lead-message" class="field-label">How can we help? *</label>
        <textarea id="lead-message" name="message" data-fs-field required rows="2" class="field-input field-input-sm" placeholder="Location, product mix, volume..."></textarea>
        <span data-fs-error="message" class="mt-1 block text-xs text-red-600"></span>
      </div>

      <label class="flex items-start gap-2.5 text-xs leading-5 text-gray-500">
        <input type="checkbox" name="consent" value="yes" required
               class="mt-0.5 h-4 w-4 shrink-0 rounded border-gray-300 text-primary focus:ring-primary" />
        <span>I agree to the <a href="/privacy.html" class="font-semibold text-gray-700 underline hover:text-primary">Privacy Policy</a> and <a href="/terms.html" class="font-semibold text-gray-700 underline hover:text-primary">Terms of Use</a>.</span>
      </label>

      <button type="submit" data-fs-submit-btn class="btn-primary w-full !py-3">
        <i class="fa-solid fa-paper-plane"></i> Submit
      </button>

      <div class="modal-note justify-center">
        <span><i class="fa-solid fa-circle-check"></i> No spam, ever</span>
        <span><i class="fa-solid fa-bolt"></i> Reply within 1 business day</span>
        <span><i class="fa-solid fa-lock"></i> We never sell your data</span>
      </div>
    </form>
  </div>
</div>`;

(function () {
  const body = document.body;
  const root = body.getAttribute("data-root") || "";

  /* Rewrite root-relative links in injected components to current depth. */
  function rewriteRootPaths(container) {
    container.querySelectorAll('a[href^="/"]').forEach((a) => {
      a.setAttribute("href", root + a.getAttribute("href").slice(1));
    });
    container.querySelectorAll('img[src^="/"]').forEach((img) => {
      img.setAttribute("src", root + img.getAttribute("src").slice(1));
    });
    fixDirectoryLinks(container);
  }

  /* file:// only: turn "news/" links into "news/index.html". */
  function fixDirectoryLinks(container) {
    if (location.protocol !== "file:") return;
    const scope = container || document;
    scope.querySelectorAll("a[href]").forEach((a) => {
      const href = a.getAttribute("href");
      if (!href || href === "#" || href.startsWith("http") || href.startsWith("mailto:")) return;
      if (href.endsWith("/")) {
        a.setAttribute("href", href + "index.html");
      }
    });
  }

  /* Inject one shared component into its placeholder. */
  function inject(componentPath, placeholderId, fallbackHtml) {
    const placeholder = document.getElementById(placeholderId);
    if (!placeholder) return;

    fetch(root + componentPath)
      .then((res) => {
        if (!res.ok) throw new Error("load failed");
        return res.text();
      })
      .then((html) => {
        placeholder.innerHTML = html;
        rewriteRootPaths(placeholder);
        afterInject(placeholderId);
      })
      .catch(() => {
        /* file:// local preview: fetch is blocked, use built-in copy. */
        placeholder.innerHTML = fallbackHtml;
        rewriteRootPaths(placeholder);
        afterInject(placeholderId);
      });
  }

  /* Post-injection hooks. */
  function afterInject(placeholderId) {
    if (placeholderId === "nav-placeholder") {
      initMobileNav();
      initHeaderShadow();
    }
  }

  /* Mobile hamburger menu toggle (smooth expand + icon swap). */
  function initMobileNav() {
    const toggle = document.getElementById("nav-toggle");
    const menu = document.getElementById("mobile-menu");
    if (!toggle || !menu) return;
    toggle.addEventListener("click", () => {
      const isOpen = menu.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(isOpen));
      const icon = toggle.querySelector("i");
      if (icon) {
        icon.classList.toggle("fa-bars", !isOpen);
        icon.classList.toggle("fa-xmark", isOpen);
      }
    });
  }

  /* Sticky header: subtle elevation after scrolling. */
  function initHeaderShadow() {
    const header = document.querySelector("#site-header");
    if (!header) return;
    const onScroll = () => {
      if (window.scrollY > 8) header.classList.add("is-scrolled");
      else header.classList.remove("is-scrolled");
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* Mark the current section in the nav after components load. */
  function initActiveNav() {
    const path = location.pathname.replace(/\/index\.html$/, "").replace(/\/$/, "");
    document.querySelectorAll("[data-nav]").forEach((link) => {
      const target = (link.getAttribute("data-nav") || "").replace(/\/$/, "");
      const isHome = target === "" && path === "";
      const isChild = target !== "" && (path === target || path.startsWith(target + "/"));
      if (isHome || isChild) {
        link.classList.add("active");
      }
    });
  }

  /* Automatic canonical (domain set once in SITE_CONFIG). */
  const canonical = document.createElement("link");
  canonical.rel = "canonical";
  canonical.href = SITE_CONFIG.domain + location.pathname;
  document.head.appendChild(canonical);

  /* Rewrite static links on the page itself (file:// only). */
  fixDirectoryLinks(document);

  /* Inject the three shared components (falls back to built-in copy). */
  inject("components/nav.html", "nav-placeholder", FALLBACK_NAV);
  inject("components/footer.html", "footer-placeholder", FALLBACK_FOOTER);
  inject("components/lead-modal.html", "lead-modal-placeholder", FALLBACK_MODAL);
  initActiveNav();

  /* Notify other scripts once everything is injected. */
  const checkReady = setInterval(() => {
    const done =
      document.getElementById("nav-placeholder").children.length > 0 &&
      document.getElementById("footer-placeholder").children.length > 0 &&
      document.getElementById("lead-modal-placeholder").children.length > 0;
    if (done) {
      clearInterval(checkReady);
      window.dispatchEvent(new CustomEvent("components-injected"));
    }
  }, 120);

  /* Back-to-top button (site-wide). */
  (function initBackToTop() {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "back-to-top";
    btn.setAttribute("aria-label", "Back to top");
    btn.innerHTML = '<i class="fa-solid fa-arrow-up"></i>';
    document.body.appendChild(btn);
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const onScroll = () => {
      btn.classList.toggle("visible", window.scrollY > 320);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    btn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
    });
  })();
})();
