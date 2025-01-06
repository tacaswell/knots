from itertools import cycle

import numpy as np
from matplotlib.path import Path

from knots.path import (
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


def band1():
    return path_from_pts(
        [
            (Pt(x, y), 0)
            for (x, y) in zip(
                np.arange(-2, 2, 0.1),
                cycle([-0.55, 0.55]),
            )
        ],
        scale=0.7,
        closed=False,
    )


def band2():
    return path_from_pts(
        [
            (Pt(x, y), angle)
            for (x, y, angle) in zip(
                np.arange(-2, 2, 0.2), cycle([-0.55, 0.55]), cycle([0, np.pi])
            )
        ],
        scale=0.7,
        closed=False,
    )


def ring1():
    r = 0.5

    return path_from_pts(
        [
            (Pt(np.cos(th) * (r + dr), np.sin(th) * (r - dr)), (th - np.pi / 2))
            for (th, dr) in zip(np.linspace(0, 2 * np.pi, 13), cycle([-0.4, 0.4]))
        ],
        scale=1,
        closed=True,
    )


def ring2():
    r = 0.5

    return path_from_pts(
        [
            (
                Pt(np.cos(th) * (r + dr), np.sin(th) * (r + dr)),
                th + phi,
            )
            for (th, dr, phi) in zip(
                np.linspace(0, 2 * np.pi, 13),
                cycle([-0.3, 0.3]),
                cycle([-np.pi / 2, np.pi / 2]),
            )
        ],
        scale=1,
        closed=True,
    )
