"""Sphinx documentation configuration file."""
from datetime import datetime

from ansys_sphinx_theme import ansys_favicon, pyansys_logo_black

# Project information
project = "ansys-geometry-core"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
release = version = "0.1.dev0"

# Select desired logo, theme, and declare the html title
html_logo = pyansys_logo_black
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "PyGeometry"


# specify the location of your github repo
html_theme_options = {
    "github_url": "https://github.com/pyansys/pygeometry",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
}

# Sphinx extensions
extensions = [
    "autoapi.extension",
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.autosummary",
    "numpydoc",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "nbsphinx",
    "sphinx_gallery.load_style",
    "myst_parser",
    "jupyter_sphinx",
    "sphinx_design",
]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/dev", None),
    "pint": ("https://pint.readthedocs.io/en/stable", None),
    "numpy": ("https://numpy.org/devdocs", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    "pyvista": ("https://docs.pyvista.org/", None),
    "grpc": ("https://grpc.github.io/grpc/python/", None),
    # kept here as an example
    # "matplotlib": ("https://matplotlib.org/stable", None),
    "pypim": ("https://pypim.docs.pyansys.com/", None),
}

# numpydoc configuration
numpydoc_show_class_members = False
numpydoc_xref_param_type = True

# Consider enabling numpydoc validation. See:
# https://numpydoc.readthedocs.io/en/latest/validation.html#
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    # "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}


# static path
html_static_path = ["_static"]

html_css_files = [
    "custom.css",
]

html_favicon = ansys_favicon

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = {
    ".rst": "restructuredtext",
    ".mystnb": "jupyter_notebook",
    ".md": "markdown",
}

# The master toctree document.
master_doc = "index"

# Configuration for Sphinx autoapi
autoapi_type = "python"
autoapi_dirs = ["../../src/ansys"]
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
]
autoapi_template_dir = "_autoapi_templates"
suppress_warnings = ["autoapi.python_import_resolution"]
exclude_patterns = ["_autoapi_templates/index.rst"]
autoapi_python_use_implicit_namespaces = True

# Examples gallery customization
nbsphinx_execute = "always"
nbsphinx_custom_formats = {
    ".mystnb": ["jupytext.reads", {"fmt": "mystnb"}],
}
nbsphinx_thumbnails = {
    "examples/basic/basic_usage": "_static/thumbnails/basic_usage.png",
    "examples/design/dynamic_sketch_plane": "_static/thumbnails/dynamic_sketch_plane.png",
    "examples/design/add_design_material": "_static/thumbnails/add_design_material.png",
    "examples/design/plate_with_hole": "_static/thumbnails/plate_with_hole.png",
    "examples/design/tessellation_usage": "_static/thumbnails/tessellation_usage.png",
    "examples/design/design_organization": "_static/thumbnails/design_organization.png",
}

typehints_defaults = "comma"
simplify_optional_unions = False
