import matplotlib.pyplot as plt
import numpy as np

from knots.editor import KnotInteractor
from knots.path import Pt, four_fold

fig = plt.figure()
fig.suptitle("'R' to render template, 'P' to print state")

interactor = KnotInteractor(
    fig,
    [
        (Pt(0, 0.8), np.pi),
        (Pt(-0.7, 0.15), -np.pi / 10),
        (Pt(-0.7, 0.7), 0),
        (Pt(0.5, -0.75), -np.pi / 2),
        (Pt(-0.8, 0), -np.pi / 2),
    ],
    reflect_func=four_fold,
    width=7,
)

plt.show()
