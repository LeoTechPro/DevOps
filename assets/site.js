const body = document.body;
const menuToggle = document.querySelector("[data-menu-toggle]");
const menu = document.querySelector("[data-menu]");
const sectionLinks = Array.from(document.querySelectorAll('.site-nav a[href^="#"]'));
const sections = Array.from(document.querySelectorAll("main section[id]"));
const mobileMenuQuery = window.matchMedia("(max-width: 760px)");
const mobileContact = document.querySelector(".mobile-contact");
const heroSection = document.querySelector(".section--hero, .resume-hero");

const closeMenu = () => {
  if (!menuToggle) return;
  body.classList.remove("menu-open");
  menuToggle.setAttribute("aria-expanded", "false");
};

const syncMenuMode = () => {
  if (!menu || !menuToggle) return;

  if (!mobileMenuQuery.matches) {
    body.classList.remove("menu-open");
    menuToggle.setAttribute("aria-expanded", "false");
    menu.removeAttribute("aria-hidden");
    return;
  }

  if (menuToggle.getAttribute("aria-expanded") === "true") {
    menu.removeAttribute("aria-hidden");
    return;
  }

  menu.setAttribute("aria-hidden", "true");
};

const syncMobileContact = () => {
  if (!mobileContact) return;

  if (!mobileMenuQuery.matches) {
    mobileContact.classList.remove("is-visible");
    return;
  }

  if (body.classList.contains("menu-open")) {
    mobileContact.classList.remove("is-visible");
    return;
  }

  if (!heroSection) {
    mobileContact.classList.toggle("is-visible", window.scrollY > Math.min(320, window.innerHeight * 0.45));
    return;
  }

  const revealThreshold = Math.min(Math.max(heroSection.offsetHeight * 0.35, 220), 420);
  mobileContact.classList.toggle("is-visible", window.scrollY > revealThreshold);
};

if (menuToggle && menu) {
  menuToggle.addEventListener("click", () => {
    const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
    menuToggle.setAttribute("aria-expanded", String(!isOpen));
    body.classList.toggle("menu-open", !isOpen);
    menu.toggleAttribute("aria-hidden", isOpen);
  });

  menu.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      closeMenu();
      syncMenuMode();
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeMenu();
      syncMenuMode();
    }
  });

  syncMenuMode();
  syncMobileContact();
  mobileMenuQuery.addEventListener("change", syncMenuMode);
  mobileMenuQuery.addEventListener("change", syncMobileContact);
}

window.addEventListener("scroll", syncMobileContact, { passive: true });
window.addEventListener("resize", syncMobileContact);
syncMobileContact();

if (sectionLinks.length && sections.length) {
  const linkMap = new Map(sectionLinks.map((link) => [link.getAttribute("href"), link]));

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const target = linkMap.get(`#${entry.target.id}`);
        if (!target) return;
        sectionLinks.forEach((link) => link.classList.toggle("is-active", link === target));
      });
    },
    {
      threshold: 0.45,
      rootMargin: "-40% 0px -45% 0px"
    }
  );

  sections.forEach((section) => observer.observe(section));
}

document.querySelectorAll("[data-year]").forEach((node) => {
  node.textContent = String(new Date().getFullYear());
});
