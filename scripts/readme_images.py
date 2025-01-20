import numpy as np
from matplotlib.path import Path

from knots.display import generate_stage3, show_with_guide
from knots.path import Knot, Pt, gen_curve4


def path1() -> list[tuple[np.uint8, Pt]]:
    """
    This generates the path for the upper-left quadrant which is expected
    to be mirroed first vertically and then horizonatally to make the full
    panel

    """
    path_data = [
        (Path.MOVETO, Pt(0, 0.8)),
    ]
    gen = gen_curve4(path_data[-1][1], np.rad2deg(np.pi), scale=0.3)
    gen.send(None)
    for pt in [
        (Pt(-0.7, 0.15), np.rad2deg(-np.pi / 10)),
        (Pt(-0.7, 0.7), 0),
        (Pt(0.5, -0.75), np.rad2deg(-np.pi / 2)),
    ]:
        path_data.extend(gen.send(pt))

    path_data.extend(gen.send((Pt(-0.8, 0), np.rad2deg(-np.pi / 2))))
    return path_data


if __name__ == "__main__":
    k = Knot.four_fold(path1())
    guide_fig = show_with_guide(k, display=False)
    guide_fig.savefig("static/guide.svg")

    with_center = generate_stage3(
        k,
        display=False,
        fig_size=(5, 5),
        center_line=True,
    )
    with_center.savefig("static/center_line.svg")

    final = generate_stage3(k, display=False, fig_size=(5, 5))
    final.savefig("static/stage_3.svg")
