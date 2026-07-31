(function () {
  var KEY = "theme";
  var root = document.documentElement;

  function labelFor(theme) {
    return theme === "dark" ? "☀ light" : "☾ dark";
  }

  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("theme-toggle");
    if (!btn) return;
    btn.textContent = labelFor(root.dataset.theme);
    btn.addEventListener("click", function () {
      var next = root.dataset.theme === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      try {
        localStorage.setItem(KEY, next);
      } catch (e) {
        /* storage unavailable — theme just won't persist across reloads */
      }
      btn.textContent = labelFor(next);
    });
  });
})();
