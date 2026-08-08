#!/usr/bin/env python3
"""Sync components/*.html into assets/js/include.js fallback constants.

Rebuilds include.js so the file:// preview fallbacks always match the
real component files. Safe to run any time components change.
"""
import io, re
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
COMPONENTS = SITE / "components"
JS = SITE / "assets" / "js" / "include.js"

HEADER = """/* ============================================================
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
  domain: "https://www.aivendinghub.com", // change before going live
};

/* ========== Local preview fallbacks (keep in sync with components/) ========== */

const FALLBACK_NAV = `__NAV__`;

const FALLBACK_FOOTER = `__FOOTER__`;

const FALLBACK_MODAL = `__MODAL__`;

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
    const path = location.pathname.replace(/\\/index\\.html$/, "").replace(/\\/$/, "");
    document.querySelectorAll("[data-nav]").forEach((link) => {
      const target = (link.getAttribute("data-nav") || "").replace(/\\/$/, "");
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
})();
"""


def js_escape(text):
    return text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


def main():
    nav = (COMPONENTS / "nav.html").read_text(encoding="utf-8")
    footer = (COMPONENTS / "footer.html").read_text(encoding="utf-8")
    modal = (COMPONENTS / "lead-modal.html").read_text(encoding="utf-8")

    js = HEADER
    js = js.replace("__NAV__", js_escape(nav.rstrip("\n")))
    js = js.replace("__FOOTER__", js_escape(footer.rstrip("\n")))
    js = js.replace("__MODAL__", js_escape(modal.rstrip("\n")))
    JS.write_text(js, encoding="utf-8")
    print("include.js rebuilt from components (nav/footer/modal)")


if __name__ == "__main__":
    main()
