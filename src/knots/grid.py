from typing import NamedTuple

import numpy as np

from knots.path import Pt


class Loc(NamedTuple):
    col: int
    row: int


def generate_grid(row, col):
    grid = np.zeros((2 * row - 1, 2 * col - 1))
    grid[::2, ::2] = -1
    grid[1::2, 1::2] = -2
    return grid


def walk_grid(grid, start):
    max_row, max_col = grid.shape
    row, col = start
    first_step = next_step = Loc(row=row, col=col)
    dir_row = dir_col = 1
    out = []
    segments = set()
    while True:
        out.append(next_step)
        last_point = next_step
        # handle hitting wall
        if 0 <= (cand := last_point.row + dir_row) < max_row:
            next_row = cand
        else:
            dir_row *= -1
            next_row = last_point.row + dir_row
        if 0 <= (cand := last_point.col + dir_col) < max_col:
            next_col = cand
        else:
            dir_col *= -1
            next_col = last_point.col + dir_col

        match grid[next_row, next_col]:
            case 0:
                # happy path!
                ...
            case -4:
                # vertical mirror
                dir_col *= -1
                next_col = last_point.col
                next_row += dir_row
            case -8:
                dir_row *= -1
                next_row = last_point.row
                next_col += dir_col
            case _:
                print("someplace I should not be")
                break

        next_step = Loc(row=next_row, col=next_col)
        segment = (last_point, next_step)
        if segment not in segments:
            segments.add(segment)
        else:
            break
        if first_step == next_step:
            out.append(next_step)
            break
        if next_step == last_point:
            break
    return out


def walk_to_pts(walk_out):
    source = iter(walk_out)
    a = next(source)
    b = next(source)
    yield Pt(*a), 0, 0.3
    last_scale = 0.3
    for c in source:
        d1 = ((b.row - a.row), (b.col - a.col))
        d2 = ((c.row - b.row), (c.col - b.col))
        d3 = ((c.row - a.row), (c.col - a.col))
        if d1 == d2:
            scale = 0
            angle = np.rad2deg(np.arctan2(*d1))
        else:
            scale = 0.3
            angle = np.rad2deg(np.arctan2(*d3))

        if scale != 0:
            yield Pt(*b), angle, max(scale, last_scale)
        last_scale = scale
        a = b
        b = c

    # yield Pt(*c), 0, 0.3
