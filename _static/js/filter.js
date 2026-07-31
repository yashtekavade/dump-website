(function () {
  var bar = document.getElementById("filter-bar");
  var grid = document.getElementById("job-grid");
  if (!bar || !grid) return;

  var cards = Array.prototype.slice.call(grid.querySelectorAll(".job-card"));
  var buttons = Array.prototype.slice.call(bar.querySelectorAll(".tag-btn"));

  bar.addEventListener("click", function (e) {
    var btn = e.target.closest(".tag-btn");
    if (!btn) return;
    var tag = btn.dataset.tag;

    buttons.forEach(function (b) { b.classList.remove("is-active"); });
    btn.classList.add("is-active");

    cards.forEach(function (card) {
      var tags = (card.dataset.tags || "").split(",");
      var show = tag === "all" || tags.indexOf(tag) !== -1;
      if (show) {
        card.removeAttribute("hidden");
      } else {
        card.setAttribute("hidden", "");
      }
    });
  });
})();
