import numpy as np
from matplotlib.figure import Figure

from knots.path import Knot, make_artist

import mpl_gui


def show_with_guide(knot: Knot):
    fig = Figure(layout="constrained")
    ax = fig.subplots()
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)

    ax.add_artist(make_artist(knot.path, color="blue", lw=7, zorder=1))

    if knot.base_path is not None:
        base_path = knot.base_path
    else:
        base_path = knot.path

    ax.add_artist(make_artist(base_path, color="r", lw=3, zorder=2, ls="--"))
    verts = np.asarray(base_path.vertices)
    ax.plot(*verts.T, "--s", color="pink")

    mpl_gui.display(fig)
