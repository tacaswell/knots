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
