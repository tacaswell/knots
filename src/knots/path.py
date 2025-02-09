from collections import namedtuple
from collections.abc import Generator, Sequence
from dataclasses import dataclass, field
from typing import cast

import numpy as np
import numpy.typing as npt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.patches import PathPatch
from matplotlib.path import Path

from knots.spline import SplineCurve
from knots.transforms import KnotTransform

from contourpy import LineType, contour_generator

Pt = namedtuple("Pt", "x y")
Pt.__doc__ = "namedtuple for (x, y) coordinates."

Bounds = namedtuple("Bounds", "xlimits ylimits")


def make_artist(path: Path, *, color, **kwargs):
    return PathPatch(path, facecolor="none", edgecolor=color, **kwargs)


def guess_bounds(path: Path, scale=1.1) -> Bounds:
    extents = path.get_extents().expanded(scale, scale)
    return Bounds(
        tuple(extents.intervalx),
        tuple(extents.intervaly),
    )


@dataclass
class Knot:
    """
    Represents a Knot and some metadata about it
    """

    # The complete Path of the knot
    path: Path = field(repr=False)
    # if any, the uint cell of the knot
    base_path: Path | None = field(repr=False, default=None)
    # text description of the knot
    description: str = ""
    # the xlimits to use when rendering
    xlimits: tuple[float, float] = field(repr=False, default=(-1.1, 1.1))
    # the ylimits to use when rendering
    ylimits: tuple[float, float] = field(repr=False, default=(-1.1, 1.1))

    @classmethod
    def four_fold(cls, base_path: Path, **kwargs):
        """
        Generate a 4-fold symetric `Knot` from a `~matplotlib.path.Path`
        """
        path = four_fold(base_path)
        bounds = guess_bounds(path)

        return cls(
            path,
            base_path,
            **{"xlimits": bounds.xlimits, "ylimits": bounds.ylimits, **kwargs},
        )

    @classmethod
    def as_spline(cls, points, pix_err=0.2, **kwargs):
        sc = SplineCurve.from_pts(points, pix_err=pix_err, need_sort=False)
        verts = sc.q_phi_to_xy(0, np.linspace(0, 2 * np.pi, 1024)).T
        path = Path(verts, closed=True)
        bounds = guess_bounds(path)
        return cls(
            path,
            **{"xlimits": bounds.xlimits, "ylimits": bounds.ylimits},
        )

    @classmethod
    def from_path(cls, path: Path, **kwargs):
        bounds = guess_bounds(path)
        return cls(
            path, **{"xlimits": bounds.xlimits, "ylimits": bounds.ylimits, **kwargs}
        )


def join(*paths: Path, close: bool = False) -> Path:
    """
    Join N paths together with LINETO.

    This is different from `matplotlib.path.Path.make_compound_path` in
    that any internal MOVETO are converted to LINETO and there is option to
    close the result.

    Parameters
    ----------
    paths : Path
       The paths to join

    close : bool, default=False
        If the final path should be closed

    Returns
    -------
    Path
    """
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


def reverse(path: Path) -> Path:
    """
    Reverse the given Path.

    Parameters
    ----------
    path : Path

    Returns
    -------
    Path
    """
    verts = path.vertices[::-1]
    codes = np.concat(([Path.MOVETO], path.codes[1:][::-1]))

    return Path(verts, codes)


def four_fold(path: Path) -> Path:
    """
    Generate a 4-fold symmetric pattern from a Path.

    The initial path will be reflected a across the yaxis and the xaxis.  To
    look smooth, have the path leave the yaxis horizonatally and approach the
    xaxis vertically.

    Parameters
    ----------
    path : Path
        The unit cell

    Returns
    -------
    Path

    """
    trans = KnotTransform().reflect(0)
    p1 = join(path, reverse(trans.transform_path(path)))
    trans2 = KnotTransform().reflect(np.pi / 2)
    return join(p1, reverse(trans2.transform_path(p1)), close=True)


def gen_curve3(
    p1: Pt, p2: Pt, scale=0.15
) -> Generator[list[tuple[np.uint8, Pt]], Pt, None]:
    """
    A helper to generate a sequence of quadratic Bezier segments.

    The segments are generated such that the control points and start/end_time
    point are co-linear.

    The codes yielded are Matplotlib's Path codes.

    This did not do what I wanted and will likely be deleted or re-written.

    """
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


def gen_curve4(
    start_point: Pt, exit_angle: float, scale: float = 0.15
) -> Generator[
    list[tuple[np.uint8, Pt]], tuple[Pt, float] | tuple[Pt, float, float], None
]:
    """
    A helper to generate a sequence of quadratic Bezier segments.

    The constraint imposed is that the tangent out of the start of
    a segment matches the tangent in from the previous.

    All angles are in degrees relative to the horizontal axis.

    The first yield will be an empty list.

    The accumulation of the data yielded from this generator can be passed to
    `path_data_to_path` to get a `matplotlib.path.Path` object.


    Parameters
    ----------
    start_point : Pt
        The location of the first point of the first segment

    exit_angle : float
        The angle the path should exit the first point in degrees

    scale : float, default: 0.15
        This controls how "loopy" the path is.  Smaller numbers
        stay closer to the direct line between the points and have
        sharper turns.  Bigger numbers have gentler curves, but get
        farther from the direct line in the transverse direction.

    Yields
    ------
    list[tuple[np.uint8, Pt]]
        The next codes and locations for a Bezier segment


    Receives
    --------
    end_point : Pt
        The end of the next segment to be generated.

    entrance_angle : float
        The angle in degrees relative to the horizonatal axis the segment should
        approach the **end_point** from.

    """
    exit_angle = np.deg2rad(exit_angle)
    last_point = start_point
    next_point, entrance_angle, *rest = yield []
    entrance_angle = np.deg2rad(entrance_angle)
    if len(rest):
        (scale,) = rest
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
        next_point, entrance_angle, *rest = yield [
            (Path.CURVE4, c1),
            (Path.CURVE4, c2),
            (Path.CURVE4, next_point),
        ]
        entrance_angle = np.deg2rad(entrance_angle)
        if len(rest):
            (scale,) = rest
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


def path_from_pts(
    points: Sequence[tuple[Pt, float]], scale: float = 0.3, closed: bool = False
) -> Path:
    """
    Convert a sequence of points and entrance angles to a `~matplotlib.path.Path`

    This will generate a compound cubic Bezier curve to represent the path via
    `gen_curve4`.

    Parameters
    ----------
    points : sequence of (Pt, float)
        The location and entrance angle of the point
    scale : float, default: 0.3
        This controls how "loopy" the path is.  Smaller numbers
        stay closer to the direct line between the points and have
        sharper turns.  Bigger numbers have gentler curves, but get
        farther from the direct line in the transverse direction.

        Is used to scale how far the control points are away from direct line between
        the end points as in `gen_curve4`.

    closed : bool, default: False
        If the path should be closed or not.

        If closed, the first point will be repeated at the and the `~matplotlib.path.Path`
        will include the ``CLOSEPOLY`` code.


    """
    itr = iter(points)
    start_point, start_angle, *rest = next(itr)
    if len(rest):
        (scale,) = rest
    path_data = [(Path.MOVETO, start_point)]
    gen = gen_curve4(path_data[-1][1], start_angle, scale=scale)
    # mypy is complaining about the initial send being None
    gen.send(None)  # type: ignore[arg-type]
    for pt in itr:
        path_data.extend(gen.send(pt))

    if closed:
        path_data.extend(gen.send((start_point, start_angle)))

    return path_data_to_path(path_data, closed=closed)


def path_data_to_path(
    path_data: list[tuple[np.uint8, Pt]], closed: bool = False
) -> Path:
    """
    Generate a `matpotlib.path.Path` object from a list of vertices and codes.

    `~matplotlb.path.Path` objects are column-major, but frequently it is easier to
    work with paths "row-wise".

    Parameters
    ----------
    path_data : list
        A list of "row-wise" code and point data.

    closed : bool, default:False
        If True, add a CLOSEPOLY if needed.

    Returns
    -------
    `matplotlib.path.Path`
    """
    codes, verts = zip(*path_data, strict=True)
    if closed and codes[-1] != Path.CLOSEPOLY:
        codes += (Path.CLOSEPOLY,)
        verts += (verts[0],)
    return Path(verts, codes)


def as_mask(
    knot: Knot, width: float, *, dpi: float = 200, fig_width: float = 5
) -> npt.NDArray[np.uint8]:
    """
    Generate a mask of points "in the ribbon".

    This works by rendering the path via Matplotlib and extracting a gray-scale
    image.

    Due to anti-aliasing this is a grayscale mask as uint8.  To get a binary mask,
    threshold at your level of choice.

    Parameters
    ----------
    knot : Knot
        The knot to generate mask of

    width : float
        The width of the ribbon in points.

    dpi : float, default: 200
        The dpi to render at internally

    fig_width : float, default: 5
        The width of the transient figure used in in.


    Returns
    -------
    mask : NDArray[np.uint8]
        gray-scale mask of the knot
    """
    aspect_ratio = float(np.diff(knot.ylimits) / np.diff(knot.xlimits))
    fig = Figure(dpi=dpi, figsize=(fig_width, fig_width * aspect_ratio))
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.axis("off")
    ax.set_aspect("equal")
    ax.set_xlim(*knot.xlimits)
    ax.set_ylim(*knot.ylimits)

    ax.add_artist(make_artist(knot.path, color="k", lw=width))
    canvas.draw()

    return np.flipud(np.asarray(canvas.buffer_rgba())[:, :, 0])


def as_outline(knot: Knot, width: float = 7, *, thresh=128) -> Path:
    """
    Generate the (compound) path of the outline of the knot ribbon.

    This works by generating the mask of the knot and then extracting a contour
    at a given gray level.

    Parameters
    ----------
    knot : Knot
        The knot to generate mask of

    width : float, default : 7
        The width of the ribbon in points.

    thresh : int, default: 128
        The level to generate the contour at

    Returns
    -------
    `matplotlib.path.Path`
    """
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
        tuple[list[npt.ArrayLike], list[npt.ArrayLike]],
        gen.lines(thresh),
    )
    p = Path(verts, codes)
    p.should_simplify = True
    return p
