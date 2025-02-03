import matplotlib.pyplot as plt
import numpy as np

from knots.editor import KnotInteractor
from knots.grid import generate_grid, walk_grid, walk_to_pts

grid = generate_grid(3, 5)
grid[2, 1] = -8
grid[2, 7] = -8
grid[3, 4] = -4
# grid[3, 2] = -4
# grid[4, 1] = -4

plt.imshow(grid, origin="lower")
out = walk_grid(grid, (0, 1))
col, row = np.array(out).T
plt.plot(col, row)
plt.show()

fig = plt.figure()
fig.suptitle("'R' to render template, 'P' to print state")

interactor = KnotInteractor(
    fig,
    list(walk_to_pts(walk_grid(grid, (0, 1)))),
    width=7,
)

plt.show()
