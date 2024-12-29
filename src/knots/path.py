from collections import namedtuple
from dataclasses import dataclass, field
from typing import cast

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from numpy.typing import ArrayLike

from knots.transforms import KnotTransform

from contourpy import LineType, contour_generator

Pt = namedtuple("Pt", "x y")


def make_artist(path: Path, *, color, **kwargs):
    return PathPatch(path, facecolor="none", edgecolor=color, **kwargs)


@dataclass
class Knot:
    path: Path = field(repr=False)
    base_path: Path | None = field(repr=False, default=None)
    description: str = ""
    xlimits: tuple[float, float] = field(repr=False, default=(-1.1, 1.1))
    ylimits: tuple[float, float] = field(repr=False, default=(-1.1, 1.1))

    @classmethod
    def four_fold(cls, path_data: list[tuple[int, float]], description: str = ""):
        codes, verts = zip(*path_data, strict=True)
        base_path = Path(verts, codes, closed=True)
        path = four_fold(base_path)
        return cls(path, base_path, description)


def join(*paths, close=False):
    pout = Path.make_compound_path(*paths)
    running_total = 0
    for p in paths[:-1]:
        running_total += len(p.codes)
        assert pout.codes[running_total] == Path.MOVETO
        pout.codes[running_total] = Path.LINETO
    if close:
        verts = np.concatenate([pout.vertices, pout.vertices[:1]])
        codes = np.concatenate([pout.codes, [Path.CLOSEPOLY]])
        pout = Path(verts, codes)
    return pout


def reverse(path):
    verts = path.vertices[::-1]
    codes = np.concat(([Path.MOVETO], path.codes[1:][::-1]))

    return Path(verts, codes)


def four_fold(path):
    trans = KnotTransform().reflect(0)
    p1 = join(path, reverse(trans.transform_path(path)))
    trans2 = KnotTransform().reflect(np.pi / 2)
    return join(p1, reverse(trans2.transform_path(p1)), close=True)


def gen_curve3(p1: Pt, p2: Pt, scale=0.15):
    next_point = yield [
        (Path.CURVE3, p1),
        (Path.CURVE3, p2),
    ]
    slope = (p2.y - p1.y) / (p2.x - p1.x)
    last_point = p2
    while True:
        dx = next_point.x - last_point.x
        p1 = Pt(last_point.x + scale * dx, last_point.y + scale * dx * slope)
        p2 = next_point

        last_point = p2
        slope = (p2.y - p1.y) / (p2.x - p1.x)
        next_point = yield [
            (Path.CURVE3, p1),
            (Path.CURVE3, p2),
        ]


def gen_curve4(start_point: Pt, exit_angle: float, scale: float = 0.15):
    last_point = start_point
    next_point, entrance_angle = yield
    dist = np.hypot(next_point.x - last_point.x, next_point.y - last_point.y)
    c1 = Pt(
        last_point.x + dist * scale * np.cos(exit_angle),
        last_point.y + dist * scale * np.sin(exit_angle),
    )
    c2 = Pt(
        next_point.x - dist * scale * np.cos(entrance_angle),
        next_point.y - dist * scale * np.sin(entrance_angle),
    )
    exit_angle = entrance_angle
    last_point = next_point
    while True:
        next_point, entrance_angle = yield [
            (Path.CURVE4, c1),
            (Path.CURVE4, c2),
            (Path.CURVE4, next_point),
        ]
        dist = np.hypot(next_point.x - last_point.x, next_point.y - last_point.y)
        c1 = Pt(
            last_point.x + dist * scale * np.cos(exit_angle),
            last_point.y + dist * scale * np.sin(exit_angle),
        )
        c2 = Pt(
            next_point.x - dist * scale * np.cos(entrance_angle),
            next_point.y - dist * scale * np.sin(entrance_angle),
        )
        last_point = next_point
        exit_angle = entrance_angle


def as_mask(knot: Knot, width: float, *, dpi=200):
    aspect_ratio = float(np.diff(knot.xlimits) / np.diff(knot.ylimits))
    fig = Figure(dpi=dpi, figsize=(5, 5 * aspect_ratio))
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.axis("off")
    ax.set_aspect("equal")
    ax.set_xlim(*knot.xlimits)
    ax.set_ylim(*knot.ylimits)

    ax.add_artist(make_artist(knot.path, color="k", lw=width))
    canvas.draw()

    return np.asarray(canvas.buffer_rgba())[:, :, :3].mean(axis=2)


def as_outline(knot: Knot, width: float = 7, *, thresh=128):
    mask = as_mask(knot, width, dpi=600)
    ny, nx = mask.shape
    gen = contour_generator(
        z=mask,
        x=np.linspace(*knot.xlimits, nx),
        y=np.linspace(*knot.ylimits, ny),
        line_type=LineType.ChunkCombinedCode,
    )
    # this is clearer?
    (verts,), (codes,) = cast(
        tuple[list[ArrayLike], list[ArrayLike]],
        gen.lines(thresh),
    )
    p = Path(verts, codes)
    p.should_simplify = True
    return p
