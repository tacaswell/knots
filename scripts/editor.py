import matplotlib.pyplot as plt
import numpy as np

from knots.editor import KnotInteractor
from knots.path import Pt

fig = plt.figure()


interactor = KnotInteractor(
    fig,
    [
        (Pt(0, 0.75), 0),
        (Pt(-0.75, 0.0), np.pi / 2),
        (Pt(0, -0.750), np.pi),
        (Pt(0.75, 0.0), -np.pi / 2),
    ],
    scale=0.5,
    width=10,
)

plt.show()
