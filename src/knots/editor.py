from collections.abc import Sequence

import numpy as np
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseButton
from matplotlib.figure import Figure

from knots.display import make_guide, make_stage3
from knots.path import Knot, Pt, as_outline, path_from_pts


class KnotArtistManager:
    def __init__(self, knot: Knot, *, width=7):
        self.guide_artists = make_guide(knot, width)
        self.stage3_artists = make_stage3(knot, width)
        self.knot = knot
        self.width = width

    def update(self, knot: Knot | None = None):
        if knot is not None:
            self.knot = knot
        knot = self.knot

        self.guide_artists.path.set_path(knot.path)

        # Bezier control points
        if knot.base_path is not None:
            base_path = knot.base_path
        else:
            base_path = knot.path
        self.guide_artists.base_path.set_path(base_path)
        self.guide_artists.bezier.set_data(np.asarray(base_path.vertices).T)

    def update_satge3(self):
        self.stage3_artists.outline.set_path(
            as_outline(self.knot, width=self.width),
        )
        self.stage3_artists.center_line.set_path(self.knot.path)
        self.stage3_artists.outline.figure.canvas.draw_idle()

    def add_guide(self, ax: Axes, animated=False):
        ax.set_xlim(*self.knot.xlimits)
        ax.set_ylim(*self.knot.ylimits)
        ax.set_aspect("equal")
        for art in self.guide_artists:
            art.set_animated(animated)
            ax.add_artist(art)

    def add_stage3(self, ax: Axes, animated=False):
        ax.set_xlim(*self.knot.xlimits)
        ax.set_ylim(*self.knot.ylimits)
        ax.set_aspect("equal")
        ax.axis("off")
        for art in self.stage3_artists:
            art.set_animated(animated)
            ax.add_artist(art)

    def draw_guide(self):
        for art in self.guide_artists:
            art.axes.draw_artist(art)


class KnotInteractor:
    """
    A path editor.

    Press 't' to toggle vertex markers on and off.  When vertex markers are on,
    they can be dragged with the mouse.
    """

    showverts = True
    epsilon = 5  # max pixel distance to count as a vertex hit

    def __init__(
        self,
        fig: Figure,
        points: Sequence[tuple[Pt, float]],
        scale: float = 0.3,
        width=7,
        reflect_func=None,
    ):
        self.ax_path, self.ax_stage3 = fig.subplots(
            1,
            2,
            sharex=True,
            sharey=True,
        )
        self.points = points
        self.scale = scale
        self.reflect_func = reflect_func

        self.kam = KnotArtistManager(self.generate_knot(), width=width)

        self.kam.add_guide(self.ax_path, animated=True)
        self.kam.add_stage3(self.ax_stage3)

        self._ind = None  # the active vertex
        canvas = fig.canvas
        canvas.mpl_connect("draw_event", self.on_draw)
        canvas.mpl_connect("button_press_event", self.on_button_press)
        canvas.mpl_connect("key_press_event", self.on_key_press)
        canvas.mpl_connect("button_release_event", self.on_button_release)
        canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas = canvas

    @property
    def knot(self) -> Knot:
        return self.kam.knot

    def generate_knot(self):
        if self.reflect_func is None:
            base_path = None
            path = path_from_pts(self.points, self.scale, closed=True)
        else:
            base_path = path_from_pts(self.points, self.scale)
            path = self.reflect_func(base_path)
        return Knot(path, base_path)

    def get_ind_under_point(self, event):
        """
        Return the index of the point closest to the event position or *None*
        if no point is within ``self.epsilon`` to the event position.
        """
        xy = np.asarray([_[0] for _ in self.points])
        xyt = self.kam.guide_artists.bezier.get_transform().transform(
            xy
        )  # to display coords
        xt, yt = xyt.T
        d = np.sqrt((xt - event.x) ** 2 + (yt - event.y) ** 2)
        ind = d.argmin()
        return ind if d[ind] < self.epsilon else None

    def on_draw(self, event):  # noqa: ARG002
        """Callback for draws."""
        self.background = self.canvas.copy_from_bbox(self.canvas.figure.bbox)
        self.kam.draw_guide()

    def on_button_press(self, event):
        """Callback for mouse button presses."""
        if (
            event.inaxes is None
            or event.button != MouseButton.LEFT
            or not self.showverts
        ):
            return
        self._ind = self.get_ind_under_point(event)

    def on_button_release(self, event):
        """Callback for mouse button releases."""
        if event.button != MouseButton.LEFT or not self.showverts:
            return
        self.kam.update_satge3()
        self._ind = None

    def on_key_press(self, event):
        """Callback for key presses."""
        if not event.inaxes:
            return
        if event.key == "t":
            self.showverts = not self.showverts
            self.line.set_visible(self.showverts)
            if not self.showverts:
                self._ind = None
        self.canvas.draw()

    def on_mouse_move(self, event):
        """Callback for mouse movements."""
        if (
            self._ind is None
            or event.inaxes is None
            or event.button != MouseButton.LEFT
            or not self.showverts
        ):
            return

        self.points[self._ind] = (
            Pt(event.xdata, event.ydata),
            self.points[self._ind][1],
        )

        self.kam.update(knot=self.generate_knot())

        self.canvas.restore_region(self.background)
        self.kam.draw_guide()
        self.canvas.blit(self.canvas.figure.bbox)
