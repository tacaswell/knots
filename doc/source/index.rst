.. knots documentation master file, created by
   sphinx-quickstart on Sat Jan  4 21:46:33 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

knots documentation
===================

source https://github.com/tacaswell/knots

Based on *Celtic Art: The Methods of Construction* [#book]_, which covers how to
create Celtic-style knot work this code automates the initial steps for basic
knots.


Method
------


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


Usage
-----

A minimal script to generate and display a knot is:

.. literalinclude:: ../../scripts/scratch.py


which can be run via ::

   pixi run scratch

Edit to something that brings you joy!

Development and Contributions
-----------------------------

This project is typed and has ruff formatting and linting applied.

There are no tests other than looking at the demo section of the docs.

The docs can be rebuilt via ::

  pixi run build_docs

Contributions are welcome, particularly additional knots in ``demos.py`` (shown
in :doc:`demos`).

Dependencies
~~~~~~~~~~~~

- Matplotlib
- contourpy (which Matplotlib also depends on, but used directly)
- mpl-gui (technically optional)


George Bain
-----------

To quote `the website of his collection <https://georgebain.groamhouse.org.uk>`__


   George Bain (1881-1968) was a Scottish illustrator, watercolourist, designer
   and art teacher whose vision and advocacy of a living, creative Celtic craft
   provides an important and influential contribution to continued interest in
   Celtic and Insular art.


.. toctree::
   :maxdepth: 1
   :caption: Contents
   :hidden:

   demos.rst
   api.rst


.. rubric:: Footnotes

.. [#book] Bain, George. Celtic Art: The Methods of Construction. Contsable, 1996. ISBN 978-0-09-476900-7
