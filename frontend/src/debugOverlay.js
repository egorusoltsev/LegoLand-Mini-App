// src/debugOverlay.js
export function installDebugOverlay() {
  // debug=1 может быть и в search, и внутри hash (из-за hash-router)
  var enabled = false;

  try {
    var search = String(window.location.search || "");
    var hash = String(window.location.hash || "");
    enabled = (search.indexOf("debug=1") !== -1) || (hash.indexOf("debug=1") !== -1);
  } catch (e) {}

  if (!enabled) return;

  function show(text) {
    console.log("[DEBUG OVERLAY]", text);
    try {
      var el = document.getElementById("__debug_overlay__");
      if (!el) {
        el = document.createElement("pre");
        el.id = "__debug_overlay__";
        el.style.position = "fixed";
        el.style.left = "8px";
        el.style.right = "8px";
        el.style.bottom = "8px";
        el.style.maxHeight = "50vh";
        el.style.overflow = "auto";
        el.style.zIndex = "999999";
        el.style.padding = "10px";
        el.style.borderRadius = "10px";
        el.style.border = "1px solid #f5c2c7";
        el.style.background = "#fff5f5";
        el.style.color = "#b00020";
        el.style.fontSize = "12px";
        el.style.whiteSpace = "pre-wrap";
        document.body.appendChild(el);
      }
      el.textContent = String(text || "Unknown error");
    } catch (e) {
      // last resort
      try { alert(String(text)); } catch (e2) {}
    }
  }

  window.onerror = function (msg, url, line, col, err) {
    var out =
      "JS ERROR:\n" +
      String(msg) +
      "\n\n" +
      (url ? (url + ":" + line + ":" + col) : "") +
      "\n\n" +
      (err && err.stack ? err.stack : "");
    show(out);
    return false;
  };

  window.onunhandledrejection = function (e) {
    var reason = e && e.reason ? e.reason : e;
    var out = "PROMISE REJECTION:\n" + String(reason);
    // иногда reason — объект
    try {
      if (reason && typeof reason === "object") {
        out += "\n\n" + JSON.stringify(reason);
      }
    } catch (e2) {}
    show(out);
  };

  // Бонус: логируем fetch-ошибки
  var origFetch = window.fetch;
  window.fetch = function () {
    return origFetch.apply(this, arguments).catch(function (err) {
      show("FETCH FAILED:\n" + String(err));
      throw err;
    });
  };

  show("Debug overlay enabled ✅ (add ?debug=1)");
}