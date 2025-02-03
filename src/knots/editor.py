from collections.abc import Sequence
from pprint import pprint

import numpy as np
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseButton
from matplotlib.figure import Figure
from matplotlib.widgets import RangeSlider, Slider

from knots.display import generate_stage3, make_guide, make_stage3
from knots.path import Knot, Pt, as_outline, guess_bounds, path_from_pts


class ReleaseSlider(Slider):
    def on_release(self, func):
        """
        Connect *func* as callback function to changes of the slider value.

        Parameters
        ----------
        func : callable
            Function to call when slider is changed.
            The function must accept a single float as its arguments.

        Returns
        -------
        int
            Connection id (which can be used to disconnect *func*).
        """
        return self._observers.connect("released", lambda: func())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # very bad from, mutating private state on private state!
        self._observers._signals.append("released")

    def _update(self, event):
        """Update the slider position."""
        if self.ignore(event) or event.button != 1:
            return

        if event.name == "button_press_event" and self.ax.contains(event)[0]:
            self.drag_active = True
            event.canvas.grab_mouse(self.ax)

        if not self.drag_active:
            return

        if (
            event.name == "button_release_event"
            or event.name == "button_press_event"
            and not self.ax.contains(event)[0]
        ):
            self.drag_active = False
            event.canvas.release_mouse(self.ax)
            if self.eventson:
                self._observers.process("released")

            return

        xdata, ydata = self._get_data_coords(event)
        val = self._value_in_bounds(
            xdata if self.orientation == "horizontal" else ydata
        )
        if val not in [None, self.val]:
            self.set_val(val)


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
        sfa, sfc = fig.subfigures(2, height_ratios=(5, 2))
        fig.set_layout_engine("constrained")
        c_axes = sfc.subplot_mosaic("ii;aa;ss;ww;xy")

        self.ax_path, self.ax_stage3 = sfa.subplots(
            1,
            2,
            sharex=True,
            sharey=True,
        )
        self.points = [p if len(p) == 3 else (*p, scale) for p in points]
        self.scale = scale
        self.reflect_func = reflect_func

        self.kam = KnotArtistManager(self.generate_knot(), width=width)

        self.kam.add_guide(self.ax_path, animated=True)
        self.kam.add_stage3(self.ax_stage3)

        self._ind = None  # the active vertex
        self._slider_ind = 0  # the active vertex

        self.widgets = {}
        self.widgets["w"] = Slider(c_axes["w"], "width", 1, 25, valinit=width)
        self.widgets["i"] = ReleaseSlider(
            c_axes["i"],
            "point index",
            0,
            len(points) - 1,
            valstep=1,
            initcolor="none",
            valinit=0,
        )
        self.widgets["a"] = ReleaseSlider(
            c_axes["a"], "angle", -180, 180, valfmt=r"%.1f°", initcolor="none"
        )
        self.widgets["s"] = ReleaseSlider(c_axes["s"], "scale", 0, 3, initcolor="none")
        self.widgets["x"] = RangeSlider(c_axes["x"], "xlimits", -2, 2, valfmt="%.2f")
        self.widgets["y"] = RangeSlider(c_axes["y"], "ylimits", -2, 2, valfmt="%.2f")

        # prompt updates
        self.widgets["i"].on_changed(self._index_change)
        self.widgets["s"].on_changed(self._scale_change)
        self.widgets["a"].on_changed(self._angle_change)

        # delayed updates
        self.widgets["i"].on_release(self.kam.update_satge3)
        self.widgets["s"].on_release(self.kam.update_satge3)
        self.widgets["a"].on_release(self.kam.update_satge3)

        self.widgets["w"].on_changed(lambda val: setattr(self.kam, "width", val))

        self._index_change(self._slider_ind)

        canvas = fig.canvas
        canvas.mpl_connect("draw_event", self.on_draw)
        canvas.mpl_connect("button_press_event", self.on_button_press)
        canvas.mpl_connect("key_press_event", self.on_key_press)
        canvas.mpl_connect("button_release_event", self.on_button_release)
        canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas = canvas

    def _index_change(self, val):
        self._slider_ind = int(val)
        vert = self.points[self._slider_ind]
        _, angle, scale = vert
        try:
            for k in ["a", "s"]:
                self.widgets[k].eventson = False
            self.widgets["a"].set_val(angle)
            self.widgets["s"].set_val(scale)

        finally:
            for k in ["a", "s"]:
                self.widgets[k].eventson = True

    def _scale_change(self, val):
        vert = self.points[self._slider_ind]
        self.points[self._slider_ind] = (*vert[:2], val)
        self.kam.update(knot=self.generate_knot())

    def _angle_change(self, val):
        vert = self.points[self._slider_ind]
        self.points[self._slider_ind] = (vert[0], val, vert[-1])
        self.kam.update(knot=self.generate_knot())

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
        bounds = guess_bounds(path, 1.1)
        return Knot(path, base_path, xlimits=bounds.xlimits, ylimits=bounds.ylimits)

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
        self._ind = ind = self.get_ind_under_point(event)
        if ind is not None:
            self.widgets["i"].set_val(self._ind)

    def on_button_release(self, event):
        """Callback for mouse button releases."""
        if event.button != MouseButton.LEFT or not self.showverts:
            return
        self.kam.update_satge3()
        self._ind = None

    def on_key_press(self, event):
        """Callback for key presses."""

        if event.key == "R":
            generate_stage3(self.knot, self.kam.width, center_line=True)
        elif event.key == "P":
            pprint(
                {
                    "width": self.kam.width,
                    "scale": self.scale,
                    "points": self.points,
                    "reflect_func": f"{self.reflect_func.__module__}.{self.reflect_func.__name__}"
                    if self.reflect_func is not None
                    else None,
                }
            )

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
            *self.points[self._ind][1:],
        )

        self.kam.update(knot=self.generate_knot())

        self.canvas.restore_region(self.background)
        self.kam.draw_guide()
        self.canvas.blit(self.canvas.figure.bbox)
