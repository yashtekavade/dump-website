(function () {
  var canvas = document.getElementById("bg-canvas");
  if (!canvas || !canvas.getContext) return;

  var ctx = canvas.getContext("2d");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var W, H, DPR;
  var nodes = [];
  var edges = [];
  var pulses = [];
  var running = true;
  var rafId = null;

  function colors() {
    var dark = document.documentElement.dataset.theme === "dark";
    return dark
      ? { dot: "rgba(124,157,255,0.38)", line: "rgba(124,157,255,0.13)", pulse: "rgba(180,200,255,0.9)" }
      : { dot: "rgba(36,86,219,0.30)", line: "rgba(36,86,219,0.12)", pulse: "rgba(36,86,219,0.8)" };
  }

  function seed() {
    var spacing = 210;
    var cols = Math.max(3, Math.round(W / spacing));
    var rows = Math.max(3, Math.round(H / spacing));
    nodes = [];
    for (var i = 0; i <= cols; i++) {
      for (var j = 0; j <= rows; j++) {
        var x = (i / cols) * W + (Math.random() - 0.5) * 70;
        var y = (j / rows) * H + (Math.random() - 0.5) * 70;
        nodes.push({ x: x, y: y, baseX: x, baseY: y, phase: Math.random() * Math.PI * 2 });
      }
    }
    edges = [];
    for (var a = 0; a < nodes.length; a++) {
      for (var b = a + 1; b < nodes.length; b++) {
        var dx = nodes[a].x - nodes[b].x;
        var dy = nodes[a].y - nodes[b].y;
        if (Math.sqrt(dx * dx + dy * dy) < spacing * 1.35) edges.push([a, b]);
      }
    }
  }

  function resize() {
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth;
    H = window.innerHeight;
    canvas.width = W * DPR;
    canvas.height = H * DPR;
    canvas.style.width = W + "px";
    canvas.style.height = H + "px";
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    seed();
  }

  function maybeSpawnPulse() {
    if (edges.length && Math.random() < 0.018) {
      var e = edges[(Math.random() * edges.length) | 0];
      pulses.push({ edge: e, t: 0, speed: 0.006 + Math.random() * 0.007 });
    }
  }

  function draw(ts) {
    var c = colors();
    ctx.clearRect(0, 0, W, H);

    ctx.strokeStyle = c.line;
    ctx.lineWidth = 1;
    for (var i = 0; i < edges.length; i++) {
      var n1 = nodes[edges[i][0]], n2 = nodes[edges[i][1]];
      ctx.beginPath();
      ctx.moveTo(n1.x, n1.y);
      ctx.lineTo(n2.x, n2.y);
      ctx.stroke();
    }

    ctx.fillStyle = c.dot;
    for (var k = 0; k < nodes.length; k++) {
      var n = nodes[k];
      if (!reduceMotion) {
        n.x = n.baseX + Math.sin(ts * 0.00035 + n.phase) * 7;
        n.y = n.baseY + Math.cos(ts * 0.00035 + n.phase) * 7;
      }
      ctx.beginPath();
      ctx.arc(n.x, n.y, 1.8, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.fillStyle = c.pulse;
    for (var p = 0; p < pulses.length; p++) {
      var pu = pulses[p];
      var a2 = nodes[pu.edge[0]], b2 = nodes[pu.edge[1]];
      var x = a2.x + (b2.x - a2.x) * pu.t;
      var y = a2.y + (b2.y - a2.y) * pu.t;
      ctx.beginPath();
      ctx.arc(x, y, 2.3, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function tick(ts) {
    if (!running) return;
    maybeSpawnPulse();
    for (var i = pulses.length - 1; i >= 0; i--) {
      pulses[i].t += pulses[i].speed;
      if (pulses[i].t >= 1) pulses.splice(i, 1);
    }
    draw(ts);
    rafId = requestAnimationFrame(tick);
  }

  window.addEventListener("resize", resize);
  document.addEventListener("visibilitychange", function () {
    running = !document.hidden;
    if (running && !reduceMotion) rafId = requestAnimationFrame(tick);
  });

  resize();
  draw(0);
  requestAnimationFrame(function () {
    canvas.classList.add("is-ready");
  });
  if (!reduceMotion) rafId = requestAnimationFrame(tick);
})();
