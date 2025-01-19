import matplotlib.pyplot as plt

from knots.editor import KnotInteractor
from knots.path import Pt, four_fold

fig = plt.figure()
fig.suptitle("'R' to render template, 'P' to print state")

interactor = KnotInteractor(
    fig,
    [
        (Pt(x=0.0, y=0.9), 3.141592653589793, 0.28),
        (Pt(x=-0.7, y=0.15), -0.3141592653589793, 0.21),
        (Pt(x=-0.7, y=0.75), 0.06828614629510353, 0.5),
        (Pt(x=0.3, y=-0.9), -3.141592653589793, 0.33),
        (Pt(x=-0.8, y=0), -1.5707963267948966, 0.3),
    ],
    reflect_func=four_fold,
    width=7,
)

plt.show()
