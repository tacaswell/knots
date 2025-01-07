import functools
import os

import numpy as np
from matplotlib.figure import Figure

from knots.path import Knot, as_outline, make_artist


def _auto_display(func):
    # TODO patch the __signature__
    @functools.wraps(func)
    def inner(*args, display: bool = True, **kwargs):
        display_mode = os.environ.get("KNOT_WINDOW_MODE", "mpl-gui").lower()

        fig = func(*args, **kwargs)
        if display:
            if display_mode == "mpl-gui":
                import mpl_gui

                mpl_gui.display(fig)
            elif display_mode == "pyplot":
                import matplotlib._pylab_helpers as _ph
                import matplotlib.pyplot as plt

                plt.get_backend()
                next_num = max(plt.get_fignums(), default=0) + 1
                _ph.Gcf._set_new_active_manager(
                    plt._backend_mod.new_figure_manager_given_figure(next_num, fig)
                )

        return fig

    return inner


@_auto_display
def show_with_guide(
    knot: Knot,
    lw: float = 7,
) -> Figure:
    """
    Show the knot with Bezier control points.

    Three things are shown:

     - the complete curve in solid blue
     - the unit cell in dashed red
     - the bezier control points in dashed pink with markers

    Parameters
    ----------
    knot : Knot
        The knot to display
    lw : float, default: 7
        The width of the line used to draw the knot in points

    Returns
    -------
    `matplotlib.figure.Figure`
    """
    fig = Figure(layout="constrained")
    ax = fig.subplots()
    ax.set_xlim(*knot.xlimits)
    ax.set_ylim(*knot.ylimits)
    ax.set_aspect("equal")
    ax.add_artist(make_artist(knot.path, color="blue", lw=lw, zorder=1))

    if knot.base_path is not None:
        base_path = knot.base_path
    else:
        base_path = knot.path

    ax.add_artist(make_artist(base_path, color="r", lw=lw / 2, zorder=2, ls="--"))
    verts = np.asarray(base_path.vertices)
    ax.plot(*verts.T, "--s", color="pink")

    return fig


@_auto_display
def generate_stage3(
    knot: Knot,
    width: float = 7,
    *,
    center_line: bool = False,
    fig_size: tuple[float, float] | None = None,
    center_alpha: float = 0.1,
) -> Figure:
    """
    Draw the "Stage 3" version of the knot ready to be interleaved.

    Parameters
    ----------
    knot : Knot
        The knot to render

    width : float, default: 7
        The width in points of the ribbon of the knot.

    center_line : bool, default: False
        If the center line of the knot should also be drawn.

        If the knot will be traced this can be a helpful guide for correctly
        doing the interleaving, but it can be distracting particularly if you
        plan to directly color a print out.

    fig_size : tuple, default: None
        The size of the rendered figure in in, following `matplotlib.figure.Figure`.

        If not given, get the aspect ratio from the `Knot` make the width 5in

    center_alpha : float, default: 0.1
        The alpha of the center line if it is drawn.

    Returns
    -------
    `matplotlib.figure.Figure`

    """
    if fig_size is None:
        aspect_ratio = float(np.diff(knot.ylimits) / np.diff(knot.xlimits))
        fig_size = (5, 5 * aspect_ratio)
    fig = Figure(figsize=fig_size)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(*knot.xlimits)
    ax.set_ylim(*knot.ylimits)

    ax.axis("off")
    ax.set_aspect("equal")
    ax.add_artist(
        make_artist(
            as_outline(knot, width=width),
            lw=1,
            color="k",
        )
    )
    if center_line:
        ax.add_artist(
            make_artist(knot.path, lw=1, ls="--", color="k", alpha=center_alpha)
        )

    return fig


def plot_segs_diagnostic(segs):
    "ugly but works"
    fig, ax = plt.subplots()
    colors = ["C0", "C1"]
    for j, seg in enumerate(segs):
        ax.plot(*seg.T, lw=10, zorder=1 + j % 2, color=colors[j % 2])


def colored_line_between_pts(pts, c, **lc_kwargs):
    """
    Plot a line with a color specified between (x, y) points by a third value.

    It does this by creating a collection of line segments between each pair of
    neighboring points. The color of each segment is determined by the
    made up of two straight lines each connecting the current (x, y) point to the
    midpoints of the lines connecting the current point with its two neighbors.
    This creates a smooth line with no gaps between the line segments.

    Parameters
    ----------
    x, y : array-like
        The horizontal and vertical coordinates of the data points.
    c : array-like
        The color values, which should have a size one less than that of x and y.
    ax : Axes
        Axis object on which to plot the colored line.
    **lc_kwargs
        Any additional arguments to pass to matplotlib.collections.LineCollection
        constructor. This should not include the array keyword argument because
        that is set to the color argument. If provided, it will be overridden.

    Returns
    -------
    matplotlib.collections.LineCollection
        The generated line collection representing the colored line.
    """
    if "array" in lc_kwargs:
        raise TypeError

    # Check color array size (LineCollection still works, but values are unused)
    if len(c) != pts.shape[0] - 1:
        raise ValueError
    # Create a set of line segments so that we can color them individually
    # This creates the points as an N x 1 x 2 array so that we can stack points
    # together easily to get the segments. The segments array for line collection
    # needs to be (numlines) x (points per line) x 2 (for x and y)
    points = pts.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, **lc_kwargs)

    # Set the values used for colormapping
    lc.set_array(c)

    return lc


def plot_segs_multiline(segs, pts, ci_array, ax):
    "currently busted"

    for j, (seg, ci) in enumerate(zip(segs, ci_array, strict=True)):
        cs = np.cumsum(np.hypot(*(seg - pts[ci]).T))
        ax.add_artist(colored_line_between_pts(seg, cs[1:], lw=14, cmap="twilight"))
