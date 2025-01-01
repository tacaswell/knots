from itertools import cycle

import numpy as np
from matplotlib.path import Path

from knots.display import generate_stage3, show_with_guide
from knots.path import (
    Knot,
    Pt,
    gen_curve3,
    path_data_to_path,
    path_from_pts,
)


def path0():
    path_data = [
        (Path.MOVETO, Pt(0, 0.5)),
    ]
    gen = gen_curve3(Pt(-0.15, 0.5), Pt(-0.25, 0.25), scale=1.2)
    path_data.extend(gen.send(None))
    for pt in [
        Pt(-0.8, 0.15),
        Pt(-1, 0.25),
        Pt(-0.8, 0.35),
    ]:
        path_data.extend(gen.send(pt))

    path_data.extend(gen.send(Pt(-0.5, 0)))
    return path_data_to_path(path_data)


def knot1():
    return path_from_pts(
        [
            (Pt(0, 0.8), np.pi),
            (Pt(-0.7, 0.15), -np.pi / 10),
            (Pt(-0.7, 0.7), 0),
            (Pt(0.5, -0.75), -np.pi / 2),
            (Pt(-0.8, 0), -np.pi / 2),
        ],
    )



def path2():
    path_data = [
        (Path.MOVETO, Pt(0, 0.8)),
    ]
    gen = gen_curve4(path_data[-1][1], np.pi, scale=0.3)
    gen.send(None)
    for pt in [
        # (Pt(-0.2, 0.05), np.pi / 5),
        (Pt(-0.7, 0.5), -np.pi / 5),
        (Pt(-0.5, 0.1), np.pi / 3),
        # (Pt(1, -0.15), 0),
    ]:
        path_data.extend(gen.send(pt))

    path_data.extend(gen.send((Pt(-0.8, 0), -np.pi / 2)))
    return path_data


k = Knot.four_fold(path1())
show_with_guide(k)
