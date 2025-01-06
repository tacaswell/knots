import numpy as np

from knots.display import generate_stage3, show_with_guide
from knots.path import Knot, Pt, path_from_pts

import mpl_gui


def gen():
    return path_from_pts(
        [
            (Pt(0, 0.5), 0),
            (Pt(-0.5, 0.0), np.pi / 2),
            (Pt(0, -0.50), np.pi),
            (Pt(0.5, 0.0), -np.pi / 2),
        ],
        scale=0.5,
        closed=True,
    )


k = Knot(gen())
mpl_gui.display(
    show_with_guide(k, display=False),
    generate_stage3(k, display=False, width=15),
)
