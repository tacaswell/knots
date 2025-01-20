import matplotlib.pyplot as plt

from knots.editor import KnotInteractor
from knots.path import Pt, four_fold

fig = plt.figure()
fig.suptitle("'R' to render template, 'P' to print state")

interactor = KnotInteractor(
    fig,
    [
        (Pt(x=0.0, y=0.9), 180, 0.28),
        (Pt(x=-0.7, y=0.15), -18, 0.21),
        (Pt(x=-0.7, y=0.75), 4, 0.5),
        (Pt(x=0.3, y=-0.9), -180, 0.33),
        (Pt(x=-0.8, y=0), -90, 0.3),
    ],
    reflect_func=four_fold,
    width=7,
)

plt.show()
