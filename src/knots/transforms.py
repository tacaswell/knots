import math


from matplotlib.transforms import Affine2D


class KnotTransform(Affine2D):
    def reflect(self, theta):
        """
        Add a rotation (in radians) to this transform in place.

        Returns *self*, so this method can easily be chained with more
        calls to :meth:`rotate`, :meth:`rotate_deg`, :meth:`translate`
        and :meth:`scale`.
        """
        a = math.cos(2 * theta)
        b = math.sin(2 * theta)
        mtx = self._mtx
        # Operating and assigning one scalar at a time is much faster.
        (xx, xy, x0), (yx, yy, y0), _ = mtx.tolist()
        # mtx = [[a b 0], [b -a 0], [0 0 1]] * mtx
        mtx[0, 0] = a * xx + b * yx
        mtx[0, 1] = a * xy + b * yy
        mtx[0, 2] = a * x0 + b * y0
        mtx[1, 0] = b * xx - a * yx
        mtx[1, 1] = b * xy - a * yy

        mtx[1, 2] = b * x0 - a * y0
        self.invalidate()
        return self

    def reflect_deg(self, degrees):
        """
        Add a rotation (in degrees) to this transform in place.

        Returns *self*, so this method can easily be chained with more
        calls to :meth:`rotate`, :meth:`rotate_deg`, :meth:`translate`
        and :meth:`scale`.
        """
        return self.rotate(math.radians(degrees))
