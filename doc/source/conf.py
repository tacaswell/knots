# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'knots'
copyright = '2025, Thomas A Caswell'
author = 'Thomas A Caswell'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'matplotlib.sphinxext.plot_directive',
#     'IPython.sphinxext.ipython_directive',
#     'IPython.sphinxext.ipython_console_highlighting',
    'numpydoc',
]


autosummary_generate = True

numpydoc_show_class_members = False
autodoc_default_options = {'members': True, 'show-inheritance': True}

default_role = 'obj'

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "pydata_sphinx_theme"
html_static_path = ['_static']

# Plot directive configuration
# ----------------------------

# For speedup, decide which plot_formats to build based on build targets:
#     html only -> png
#     latex only -> pdf
#     all other cases, including html + latex -> png, pdf
# For simplicity, we assume that the build targets appear in the command line.
# We're falling back on using all formats in case that assumption fails.
plot_formats = [('png', 100), ('svg', 200), ('pdf', 200)]

# make 2x images for srcset argument to <img>
# plot_srcset = ['2x']

# GitHub extension

github_project_url = "https://github.com/tacaswell/knots/"
intersphinx_mapping = {'python': ('https://docs.python.org/3', None),
                       'matplotlb': ('https://matplotlib.org/stable', None)}
