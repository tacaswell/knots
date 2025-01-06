.. knots documentation master file, created by
   sphinx-quickstart on Sat Jan  4 21:46:33 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

knots documentation
===================

Based on *Celtic Art: The Methods of Construction* [#book]_, which covers how to
create Celtic-style knot work this code automates the initial steps for basic
knots.


Very briefly, the method is to:

1. construct a single line that is the path of the knot
2. expand to a ribbon around the center line
3. remove the center line
4. interleave the crossings
5. elaboration and decoration

Using this code you will be able to generate up to stage 3 that can be printed
and traced.

To make this concrete, the initial step is to generate the path of the knot,
shown here including the control points used for path and indicating the unit
cell that was mirrored to make the complete knot.

.. plot::

   from knots.demos import knot1
   from knots.display import show_with_guide
   from knots.path import Knot
   show_with_guide(Knot.four_fold(knot1()))

Dropping the construction marks and showing the center line gives

.. plot::

   from knots.demos import knot1
   from knots.display import generate_stage3
   from knots.path import Knot

   generate_stage3(
       Knot.four_fold(knot1()),
       fig_size=(5, 5),
       center_line=True,
       center_alpha=.7,
   )


At this stage, this is ready to be printed to begin the manual process of
interleaving the crossings.  Pick any crossing and decide which direction will
be "over".  You then move either direction along the ribbon alternating
over/under until you return to the starting point.



.. plot::

   from knots.demos import knot1
   from knots.display import generate_stage3
   from knots.path import Knot

   generate_stage3(Knot.four_fold(knot1()), fig_size=(5, 5))




.. toctree::
   :maxdepth: 1
   :caption: Contents
   :hidden:

   demos.rst
   api.rst


.. rubric:: Footnotes

.. [#book] Bain, George. Celtic Art: The Methods of Construction. Contsable, 1996. ISBN 978-0-09-476900-7
