(function () {
  var cfg = window.NGX_ANALYTICS || {};
  var provider = String(cfg.provider || "").trim();
  var id = String(cfg.measurementId || "").trim();
  if (!provider || !id) return;
  if (provider !== "ga4" || !/^G-[A-Z0-9]+$/.test(id)) return;

  var script = document.createElement("script");
  script.async = true;
  script.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(id);
  document.head.appendChild(script);

  window.dataLayer = window.dataLayer || [];
  function gtag() {
    window.dataLayer.push(arguments);
  }
  window.gtag = gtag;
  gtag("js", new Date());
  gtag("config", id);
})();
