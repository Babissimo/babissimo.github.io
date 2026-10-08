// The landing chart's swell: one wave field that the lettering, depth line,
// buoys and anchor all sample, so they move as the same water. The markup is
// the still chart; the swell eases in from it and returns to it under
// prefers-reduced-motion.
(() => {
  const chart = document.getElementById("chart");
  if (!chart) return;

  const TAU = Math.PI * 2;
  const arc = document.getElementById("chart-arc");
  const depth = document.getElementById("chart-depth");
  const name = document.getElementById("chart-name");
  const anchorage = document.getElementById("chart-anchorage");
  const buoys = [...chart.querySelectorAll(".buoys circle")].map((el, i) => ({
    el,
    x: +el.getAttribute("cx"),
    y: +el.getAttribute("cy"),
    r: +el.getAttribute("r"),
    period: 3.6 + ((i * 0.73) % 2.6),
    phase: i * 1.7,
  }));

  const swell = (x, t) =>
    5 * Math.sin(TAU * (x / 640 - t / 7.5)) +
    2.2 * Math.sin(TAU * (x / 290 + t / 11) + 1.3);
  const slope = (x, t) => (swell(x + 1, t) - swell(x - 1, t)) / 2;
  // Must match the still arc and depth line in index.qmd.
  const arcBase = (x) => { const u = (x - 40) / 920; return 318 - 208 * u * (1 - u); };
  const depthBase = (x) => 120 + 30 * Math.sin((TAU * x) / 780 + 2.6);
  const ease = (t) => { const u = Math.min(t / 3, 1); return u * u * (3 - 2 * u); };
  const f = (n) => n.toFixed(1);

  // Quadratic midpoint smoothing keeps the textPath free of kinks between samples.
  const pathThrough = (x0, x1, n, y) => {
    const pts = Array.from({ length: n + 1 }, (_, i) => {
      const x = x0 + ((x1 - x0) * i) / n;
      return [x, y(x)];
    });
    let d = `M ${f(pts[0][0])} ${f(pts[0][1])}`;
    for (let i = 1; i < n; i++) {
      const [x, y0] = pts[i], [nx, ny] = pts[i + 1];
      d += ` Q ${f(x)} ${f(y0)} ${f((x + nx) / 2)} ${f((y0 + ny) / 2)}`;
    }
    return d + ` L ${f(pts[n][0])} ${f(pts[n][1])}`;
  };

  const draw = (t) => {
    const k = ease(t);
    arc.setAttribute("d", pathThrough(40, 960, 40, (x) => arcBase(x) + k * swell(x, t)));
    depth.setAttribute("d", pathThrough(0, 1000, 40, (x) => depthBase(x) + k * 0.6 * swell(x, t - 1.4)));
    name.style.letterSpacing = `${(0.36 + k * 0.02 * Math.sin((TAU * t) / 9)).toFixed(4)}em`;
    for (const b of buoys) {
      const dy = 0.8 * swell(b.x, t - 0.6) + 2.4 * Math.sin((TAU * t) / b.period + b.phase);
      const dx = 1.6 * Math.sin((TAU * t) / (b.period * 1.7) + b.phase);
      const breath = 1 + 0.08 * Math.sin((TAU * t) / (b.period * 1.3) + b.phase);
      b.el.setAttribute("cx", (b.x + k * dx).toFixed(2));
      b.el.setAttribute("cy", (b.y + k * dy).toFixed(2));
      b.el.setAttribute("r", (b.r * (1 + k * (breath - 1))).toFixed(2));
    }
    // Pivot on the ring (16, 6 before the 0.95 scale), so the anchor swings rather than spins.
    const tilt = k * ((Math.atan(slope(900, t)) * 180) / Math.PI + 3 * Math.sin((TAU * t) / 6.3));
    const lift = k * 0.8 * swell(900, t - 0.6);
    anchorage.setAttribute(
      "transform",
      `translate(884 ${(122 + lift).toFixed(2)}) rotate(${tilt.toFixed(2)} 15.2 5.7) scale(0.95)`,
    );
  };

  const still = matchMedia("(prefers-reduced-motion: reduce)");
  let t = 0, last = null, raf = 0, onScreen = true;

  const frame = (now) => {
    // Capped so a backgrounded tab resumes where it left off rather than jumping.
    if (last !== null) t += Math.min(now - last, 100) / 1000;
    last = now;
    draw(t);
    raf = requestAnimationFrame(frame);
  };

  const sync = () => {
    cancelAnimationFrame(raf);
    last = null;
    if (still.matches) { t = 0; draw(0); return; }
    if (onScreen) raf = requestAnimationFrame(frame);
  };

  still.addEventListener("change", sync);
  new IntersectionObserver(([entry]) => {
    onScreen = entry.isIntersecting;
    sync();
  }).observe(chart);
  sync();
})();
