(function () {
  const header = document.querySelector(".site-header");
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.querySelector(".nav");
  const slides = [...document.querySelectorAll(".slide")];
  const dots = [...document.querySelectorAll(".hero-dots button")];
  let i = 0;

  if (header) {
    const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      document.body.classList.toggle("nav-open", open);
    });
    nav.querySelectorAll("a").forEach((a) =>
      a.addEventListener("click", () => {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        document.body.classList.remove("nav-open");
      })
    );
    const dropBtn = nav.querySelector(".has-sub > span, .has-sub > button");
    if (dropBtn) {
      dropBtn.addEventListener("click", (e) => {
        if (window.matchMedia("(max-width: 900px)").matches) {
          e.preventDefault();
          dropBtn.parentElement.classList.toggle("is-open");
        }
      });
    }
  }

  if (!slides.length) return;

  const titleEl = document.getElementById("hero-title");
  function show(n) {
    i = (n + slides.length) % slides.length;
    slides.forEach((s, idx) => s.classList.toggle("is-on", idx === i));
    dots.forEach((d, idx) => d.classList.toggle("is-on", idx === i));
    if (titleEl && slides[i] && slides[i].dataset.title) {
      titleEl.textContent = slides[i].dataset.title;
    }
  }
  dots.forEach((d, idx) => d.addEventListener("click", () => show(idx)));
  setInterval(() => show(i + 1), 6000);
})();
