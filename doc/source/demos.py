from knots.demos import knot1, ring1, ring2, band1, band2
from knots.display import generate_stage3, show_with_guide
from knots.path import Knot

def demo_knot1():
    k = Knot.four_fold(knot1())
    show_with_guide(k)
    generate_stage3(k, center_line=True, width=7)


def demo_ring1():
    k = Knot(ring1())
    show_with_guide(k)
    generate_stage3(k, center_line=True, width=7)


def demo_ring2():
    k = Knot(ring2())
    show_with_guide(k)
    generate_stage3(k, center_line=True, width=7)


def demo_band1():
    k = Knot(band1(), ylimits=(-.8, .8))
    generate_stage3(k, center_line=True, width=7)


def demo_band2():
    k = Knot(band2(), ylimits=(-.8, .8))
    generate_stage3(k, center_line=True, width=7)
