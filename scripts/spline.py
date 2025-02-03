import matplotlib.figure
import matplotlib.path
import numpy as np

from knots.display import generate_stage3, show_with_guide
from knots.grid import generate_grid, walk_grid
from knots.path import Knot

import mpl_gui

grid = generate_grid(3, 5)
grid[2, 1] = -8
grid[2, 7] = -8
grid[3, 4] = -4
# grid[3, 2] = -4
# grid[4, 1] = -4


out = np.array(walk_grid(grid, (0, 1))).T
# this makes it look more symmetric?!
out = np.fliplr(out)


col, row = np.array(out)
k = Knot.as_spline(out, pix_err=0.1)

fig = matplotlib.figure.Figure()
ax = fig.subplots()
ax.imshow(grid, origin="lower")
ax.plot(col, row)

fig_guide = show_with_guide(k, display=False)
fig_stage3 = generate_stage3(k, display=False, width=15)
# plt.show()
mpl_gui.display(fig, fig_guide, fig_stage3)
