# Lightly adapted from infra.py in https://github.com/tacaswell/leidenfrost
# that I wrote as part of my PhD thesis.

from collections import namedtuple
from functools import reduce

import numpy as np
import numpy.fft as fft
import scipy.interpolate as si


class TooFewPointsException(Exception):
    pass


class SplineCurve:
    mode_param = namedtuple("mode_param", ["n", "x", "y"])
    abs_angle = namedtuple("abs_angle", ["abs", "angle"])

    """
    A class that wraps the scipy.interpolation objects
    """

    @classmethod
    def _get_spline(cls, points, pix_err=2, need_sort=True, **kwargs):
        """
        Returns a closed spline for the points handed in.
        Input is assumed to be a (2xN) array

        =====
        input
        =====

        :param points: the points to fit the spline to
        :type points: a 2xN ndarray or a list of len =2 tuples

        :param pix_err: the error is finding the spline in pixels
        :param need_sort: if the points need to be sorted
            or should be processed as-is

        =====
        output
        =====
        tck
           The return data from the spline fitting
        """

        if type(points) is np.ndarray:
            # make into a list
            pt_lst = list(zip(*points, strict=True))
            # get center
            center = np.mean(points, axis=1).reshape(2, 1)
        else:
            # make a copy of the list
            pt_lst = list(points)
            # compute center
            center = np.array(
                reduce(lambda x, y: (x[0] + y[0], x[1] + y[1]), pt_lst)
            ).reshape(2, 1)
            center /= len(pt_lst)

        if len(pt_lst) < 5:
            raise TooFewPointsException("not enough points")

        if need_sort:
            # sort the list by angle around center
            pt_lst.sort(key=lambda x: np.arctan2(x[1] - center[1], x[0] - center[0]))

        # add first point to end because it is periodic (makes the
        # interpolation code happy)
        if pt_lst[0] != pt_lst[-1]:
            pt_lst.append(pt_lst[0])

        # make array for handing in to spline fitting
        pt_array = np.vstack(pt_lst).T
        # do spline fitting

        tck, u = si.splprep(pt_array, s=len(pt_lst) * (pix_err**2), per=True, k=3)

        return tck

    @classmethod
    def from_pts(cls, new_pts, **kwargs):
        tck = cls._get_spline(new_pts, **kwargs)
        this = cls(tck)
        this.raw_pts = new_pts
        return this

    def __init__(self, tck):
        """A really hacky way of doing different"""
        self.tck = tck
        self._cntr = None
        self._circ = None
        self._th_offset = None

    @property
    def circ(self):
        """returns a rough estimate of the circumference"""
        if self._circ is None:
            new_pts = si.splev(np.linspace(0, 1, 1000), self.tck, ext=2)
            self._circ = np.sum(np.sqrt(np.sum(np.diff(new_pts, axis=1) ** 2, axis=0)))
        return self._circ

    @property
    def cntr(self):
        """returns a rough estimate of the circumference"""
        if self._cntr is None:
            new_pts = si.splev(np.linspace(0, 1, 1000), self.tck, ext=2)
            self._cntr = np.mean(new_pts, 1)
        return self._cntr

    @property
    def th_offset(self):
        """
        The angle from the y-axis for (x, y) at `phi=0`
        """
        if self._th_offset is None:
            x, y = self.q_phi_to_xy(0, 0) - self.cntr.reshape(2, 1)
            self._th_offset = np.arctan2(y, x)
        return self._th_offset

    @property
    def tck0(self):
        return self.tck[0]

    @property
    def tck1(self):
        return self.tck[1]

    @property
    def tck2(self):
        return self.tck[2]

    def q_phi_to_xy(self, q, phi, cross=None):
        """Converts q, phi pairs -> x, y pairs.  All other code that
        does this should move to using this so that there is minimal
        breakage when we change over to using additive q instead of
        multiplicative"""
        # make sure data is arrays
        q = np.asarray(q)
        # convert real units -> interpolation units
        phi = np.mod(np.asarray(phi), 2 * np.pi) / (2 * np.pi)
        # get the shapes
        q_shape, phi_shape = (
            _.shape if (_.shape != () and len(_) > 1) else None for _ in (q, phi)
        )

        # flatten everything
        q = q.ravel()
        phi = phi.ravel()
        # sanity checks on shapes
        if cross is False and phi_shape != q_shape:
            raise ValueError("q and phi must have same" + " dimensions to broadcast")
        if cross is None:
            if (
                (phi_shape is not None)
                and (q_shape is not None)
                and (phi_shape == q_shape)
            ):
                cross = False
            elif q_shape is None:
                cross = False
                q = q[0]
            else:
                cross = True

        x, y = si.splev(phi, self.tck, ext=2)
        dx, dy = si.splev(phi, self.tck, der=1, ext=2)
        norm = np.sqrt(dx**2 + dy**2)
        nx, ny = dy / norm, -dx / norm

        # if cross, then
        if cross:
            data_out = list(
                zip(
                    *[
                        (
                            (x + q_ * nx).reshape(phi_shape),
                            (y + q_ * ny).reshape(phi_shape),
                        )
                        for q_ in q
                    ],
                    strict=False,
                )
            )
        else:
            data_out = np.vstack(
                [(x + q * nx).reshape(phi_shape), (y + q * ny).reshape(phi_shape)]
            )

        return data_out

    def fft_filter(self, mode):
        if mode == 0:
            return
        sample_pow = 12
        tmp_pts = si.splev(np.linspace(0, 1, 2**sample_pow), self.tck)

        mask = np.zeros(2**sample_pow)
        mask[0] = 1
        mask[1 : (mode + 1)] = 1
        mask[-mode:] = 1

        new_pts = []
        for w in tmp_pts:
            wfft = fft.fft(w)
            new_pts.append(np.real(fft.ifft(wfft * mask)))

        new_pts = np.vstack(new_pts)

        tck = self._get_spline(new_pts, pix_err=0.05, need_sort=False)

        self.tck = tck

    def draw_to_axes(self, ax, N=1024, **kwargs):
        return ax.plot(
            *(self.q_phi_to_xy(0, np.linspace(0, 2 * np.pi, N)) + 0.5), **kwargs
        )

    def curve_shape_fft(self, N=3):
        """
        Returns the amplitude and phase of the components of the rim curve

        Parameters
        ----------
        self : SplineCurve
            The curve to extract the data from

        n : int
            The maximum mode to extract data for

        Returns
        -------
        ret : list
            [mode_param(n=n, x=abs_angle(x_amp, x_phase),
                        y=abs_angle(y_amp, y_phase)), ...]
        """
        curve_data = self.q_phi_to_xy(1, np.linspace(0, 2 * np.pi, 1000))
        curve_fft = [np.fft.fft(_d) / len(_d) for _d in curve_data]
        return [
            self.mode_param(
                n,
                *[
                    self.abs_angle(2 * np.abs(_cfft[n]), np.angle(_cfft[n]))
                    for _cfft in curve_fft
                ],
            )
            for n in range(1, N + 1)
        ]

    def cum_length(self, N=1024):
        """Returns the cumulative length at N evenly
        sampled points in parameter space

        Parameters
        ----------
        N : int
            Number of points to sample

        Returns
        -------
        ret : ndarray
            An ndarray of length N which is the cumulative distance
            around the rim
        """
        # turns out you _can_ write un-readable python
        return np.concatenate(
            (
                [0],
                np.cumsum(
                    np.sqrt(
                        np.sum(
                            np.diff(
                                si.splev(np.linspace(0, 1, N), self.tck, ext=2), axis=1
                            )
                            ** 2,
                            axis=0,
                        )
                    )
                ),
            )
        )

    def cum_length_theta(self, N=1024):
        """Returns the cumulative length evenly sampled in theta space.  Does by
        evenly sampling the rim in spline units and the interpolating to
        evenly spaced theta positions.

        Parameters
        ----------
        N : int
            Number of points to sample

        Returns
        -------
        ret : ndarray
            An ndarray of length N which is the cumulative distance
            around the rim
        """
        intep_func = si.interp1d
        cntr = self.cntr.reshape(2, 1)
        # over sample in spline space
        XY = si.splev(np.linspace(0, 1, 2 * N), self.tck, ext=2) - cntr
        theta = np.mod(np.arctan2(XY[1], XY[0]), 2 * np.pi)
        indx = np.argsort(theta)
        XY = XY[:, indx]
        theta = theta[indx]
        # pad one past the end
        theta = np.r_[theta[-1] - 2 * np.pi, theta, theta[0] + 2 * np.pi]
        XY = np.c_[XY[:, -1:], XY, XY[:, :1]]
        # the sample points
        sample_theta = np.linspace(0, 2 * np.pi, N)
        # re-sample
        XY_resample = np.vstack([intep_func(theta, _xy)(sample_theta) for _xy in XY])
        return np.concatenate(
            ([0], np.cumsum(np.sqrt(np.sum(np.diff(XY_resample, axis=1) ** 2, axis=0))))
        )
