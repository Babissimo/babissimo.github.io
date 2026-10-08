#!/usr/bin/env python3
"""Draw the about map's trail with a hand's wobble.

The route is the smooth path in the trail's `data-route` in about/_voyage.qmd.
This rewrites the trail's `d` as that route pushed sideways by a couple of slow
sines and refitted through Catmull-Rom. The wobble dies away at each stop (the
`.vy-stops` circles), so the trail still meets them, and in tight bends, so the
loop keeps its shape. It is seeded, so rerunning it on an unchanged route
changes nothing.

Run by hand after editing the route: python3 tools/voyage-trail.py
"""

import math
import pathlib
import random
import re

MAP = pathlib.Path(__file__).resolve().parent.parent / "about" / "_voyage.qmd"
SEED = 21
AMPLITUDE = 7.0   # map units either side of the route
SPACING = 13      # map units between refitted points
BEND = 42         # bends tighter than about this radius damp the wobble


def bezier(seg, t):
    p0, p1, p2, p3 = seg
    u = 1 - t
    return tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d
                 for a, b, c, d in zip(p0, p1, p2, p3))


def arclength(pts):
    out = [0.0]
    for a, b in zip(pts, pts[1:]):
        out.append(out[-1] + math.dist(a, b))
    return out


def curvature(pts, i):
    a, b, c = pts[max(i - 6, 0)], pts[i], pts[min(i + 6, len(pts) - 1)]
    ab, bc, ca = math.dist(a, b), math.dist(b, c), math.dist(c, a)
    if ab * bc * ca == 0:
        return 0
    cross = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
    return 2 * cross / (ab * bc * ca)


def legs(route, stops):
    """Sample the route densely, split into legs at the stops."""
    nums = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", route)]
    start = (nums[0], nums[1])
    out, leg, p = [], [start], start
    for i in range(2, len(nums), 6):
        seg = (p, (nums[i], nums[i + 1]), (nums[i + 2], nums[i + 3]), (nums[i + 4], nums[i + 5]))
        leg += [bezier(seg, k / 400) for k in range(1, 401)]
        p = seg[3]
        if (round(p[0]), round(p[1])) in stops:
            out.append(leg)
            leg = [p]
    if len(leg) > 1:
        out.append(leg)
    return out


def wobble(leg):
    s = arclength(leg)
    length = s[-1]
    l1, l2 = random.uniform(95, 130), random.uniform(38, 52)
    f1, f2 = random.uniform(0, 2 * math.pi), random.uniform(0, 2 * math.pi)
    amp = AMPLITUDE * random.uniform(0.85, 1.15)
    damp = [1 / (1 + (curvature(leg, i) * BEND) ** 2) for i in range(len(leg))]
    # The weakest damping nearby, so the wobble eases out before a bend.
    eased = [min(damp[max(0, i - 40):i + 41]) for i in range(len(leg))]
    out = []
    for i, (pt, si) in enumerate(zip(leg, s)):
        envelope = math.sin(math.pi * si / length) ** 0.6
        off = amp * envelope * eased[i] * (math.sin(2 * math.pi * si / l1 + f1)
                                           + 0.45 * math.sin(2 * math.pi * si / l2 + f2))
        a, b = leg[max(i - 1, 0)], leg[min(i + 1, len(leg) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        n = math.hypot(tx, ty) or 1
        out.append((pt[0] - ty / n * off, pt[1] + tx / n * off))
    return out


def resample(pts):
    """Every SPACING units or so, without the ends, which the caller keeps."""
    s = arclength(pts)
    step = s[-1] / max(2, round(s[-1] / SPACING))
    out, target = [], step
    for pt, si in zip(pts[1:-1], s[1:-1]):
        if si >= target:
            out.append(pt)
            target += step
    return out


def fmt(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def catmull_rom(pts):
    d = f"M {fmt(pts[0][0])} {fmt(pts[0][1])}"
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += " C " + " ".join(fmt(v) for v in (*c1, *c2, *p2))
    return d


def main():
    random.seed(SEED)
    src = MAP.read_text(encoding="utf-8")
    route = re.search(r'class="vy-trail" data-route="([^"]*)"', src).group(1)
    assert set(re.findall(r"[A-Za-z]", route)) == {"M", "C"}, "the route is a move, then cubics"
    stops_block = re.search(r'<g class="vy-stops">(.*?)</g>', src, re.S).group(1)
    stops = {(round(float(x)), round(float(y)))
             for x, y in re.findall(r'cx="([\d.]+)" cy="([\d.]+)"', stops_block)}

    route_legs = legs(route, stops)
    pts = [route_legs[0][0]]
    for leg in route_legs:
        pts += resample(wobble(leg)) + [leg[-1]]
    # A refitted point can land right beside a stop; the stop wins.
    ends = {pts[0]} | {leg[-1] for leg in route_legs}
    kept = [pts[0]]
    for pt in pts[1:]:
        if math.dist(pt, kept[-1]) < 5 and pt not in ends:
            continue
        kept.append(pt)

    new, n = re.subn(r'(class="vy-trail" data-route="[^"]*" d=")[^"]*(")',
                     lambda m: m.group(1) + catmull_rom(kept) + m.group(2), src)
    assert n == 1, "expected one trail in the map"
    MAP.write_text(new, encoding="utf-8")


if __name__ == "__main__":
    main()
