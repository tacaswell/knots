import functools
import os

import numpy as np
from matplotlib.figure import Figure

from knots.path import Knot, as_outline, make_artist

import mpl_gui


def _auto_display(func):
    # TODO patch the __signature__
    @functools.wraps(func)
    def inner(*args, display: bool = True, **kwargs):
        display_mode = os.environ.get("KNOT_WINDOW_MODE", "mpl-gui").lower()

        fig = func(*args, **kwargs)
        if display:
            if display_mode == "mpl-gui":
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
    fig_size=(8.5, 11),
) -> Figure:
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
        ax.add_artist(make_artist(knot.path, lw=1, ls="--", color="k", alpha=0.1))
    return fig
