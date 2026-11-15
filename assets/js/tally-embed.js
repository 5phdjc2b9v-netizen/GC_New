/* GeoCenter / Tally: safely initialise responsive embedded forms. */
(function () {
  "use strict";
  var loader = "https://tally.so/widgets/embed.js";
  function fallback() {
    document.querySelectorAll("iframe[data-tally-src]:not([src])").forEach(function (frame) {
      frame.src = frame.getAttribute("data-tally-src");
    });
  }
  function initialise() {
    if (window.Tally && typeof window.Tally.loadEmbeds === "function") {
      window.Tally.loadEmbeds();
    } else {
      fallback();
    }
  }
  if (window.Tally && typeof window.Tally.loadEmbeds === "function") {
    initialise();
  } else {
    var script = document.querySelector('script[src="' + loader + '"]');
    if (!script) {
      script = document.createElement("script");
      script.src = loader;
      script.async = true;
      script.onload = initialise;
      script.onerror = fallback;
      document.head.appendChild(script);
    } else {
      script.addEventListener("load", initialise, { once: true });
      script.addEventListener("error", fallback, { once: true });
    }
  }
})();
