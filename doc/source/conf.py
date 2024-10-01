"""Sphinx documentation configuration file."""

from datetime import datetime
import json
import os
from pathlib import Path
import time

from ansys_sphinx_theme import (
    ansys_favicon,
    ansys_logo_white,
    ansys_logo_white_cropped,
    get_version_match,
    latex,
    watermark,
)
import requests
import sphinx
from sphinx.builders.latex import LaTeXBuilder
from sphinx.util import logging

from ansys.geometry.core import __version__

# Convert notebooks into Python scripts and include them in the output files
logger = logging.getLogger(__name__)


# For some reason the global var is not working on doc build...
# import ansys.tools.visualization_interface as viz_interface
#
# viz_interface.DOCUMENTATION_BUILD = True
#
# Using env var instead
os.environ["PYANSYS_VISUALIZER_DOC_MODE"] = "true"
os.environ["PYANSYS_VISUALIZER_HTML_BACKEND"] = "true"

LaTeXBuilder.supported_image_types = ["image/png", "image/pdf", "image/svg+xml"]


def get_wheelhouse_assets_dictionary():
    """Auxiliary method to build the wheelhouse assets dictionary."""
    assets_context_os = ["Linux", "Windows", "MacOS"]
    assets_context_runners = ["ubuntu-latest", "windows-latest", "macos-latest"]
    assets_context_python_versions = ["3.10", "3.11", "3.12"]
    if get_version_match(__version__) == "dev":
        # Try to retrieve the content three times before failing
        content = None
        for _ in range(3):
            response = requests.get(
                "https://api.github.com/repos/ansys/pyansys-geometry/releases/latest"
            )
            if response.status_code == 200:
                content = response.content
                break
            else:
                print("Failed to retrieve the latest release. Retrying...")
                time.sleep(2)

        if content is None:
            raise requests.exceptions.RequestException("Failed to retrieve the latest release.")

        # Just point to the latest version
        assets_context_version = json.loads(content)["name"]
    else:
        assets_context_version = f"v{__version__}"

    assets = {}
    for assets_os, assets_runner in zip(assets_context_os, assets_context_runners):
        download_links = []
        for assets_py_ver in assets_context_python_versions:
            temp_dict = {
                "os": assets_os,
                "runner": assets_runner,
                "python_versions": assets_py_ver,
                "latest_released_version": assets_context_version,
                "prefix_url": f"https://github.com/ansys/pyansys-geometry/releases/download/{assets_context_version}",  # noqa: E501
            }
            download_links.append(temp_dict)

        assets[assets_os] = download_links
    return assets


def intersphinx_pyansys_geometry(switcher_version: str):
    """Auxiliary method to build the intersphinx mapping for PyAnsys Geometry.

    Notes
    -----
    If the objects.inv file is not found whenever it is a release, the method
    will default to the "dev" version. If the objects.inv file is not found
    for the "dev" version, the method will return an empty string.

    Parameters
    ----------
    switcher_version : str
        Version of the PyAnsys Geometry package.

    Returns
    -------
    str
        The intersphinx mapping for PyAnsys Geometry.
    """
    prefix = "https://geometry.docs.pyansys.com/version"

    # Check if the object.inv file exists
    response = requests.get(f"{prefix}/{switcher_version}/objects.inv")

    if response.status_code == 404:
        if switcher_version == "dev":
            return ""
        else:
            return intersphinx_pyansys_geometry("dev")
    else:
        return f"{prefix}/{switcher_version}"


# Project information
project = "ansys-geometry-core"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
release = version = __version__
cname = os.getenv("DOCUMENTATION_CNAME", default="geometry.docs.pyansys.com")
switcher_version = get_version_match(__version__)

# Select desired logo, theme, and declare the html title
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "PyAnsys Geometry"
html_baseurl = f"https://{cname}/version/stable"

# specify the location of your github repo
html_context = {
    "github_user": "ansys",
    "github_repo": "pyansys-geometry",
    "github_version": "main",
    "doc_path": "doc/source",
}
html_theme_options = {
    "logo": "pyansys",
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": switcher_version,
    },
    "github_url": "https://github.com/ansys/pyansys-geometry",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "collapse_navigation": True,
    "use_edit_page_button": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "icon_links": [
        {
            "name": "Support",
            "url": "https://github.com/ansys/pyansys-geometry/discussions",
            "icon": "fa fa-comment fa-fw",
        },
        {
            "name": "Download documentation in PDF",
            "url": f"https://{cname}/version/{switcher_version}/_static/assets/download/ansys-geometry-core.pdf",  # noqa: E501
            "icon": "fa fa-file-pdf fa-fw",
        },
    ],
    "ansys_sphinx_theme_autoapi": {
        "project": project,
    },
    "cheatsheet": {
        "file": "cheat_sheet.qmd",
        "title": "PyAnsys Geometry cheat sheet",
    },
    "static_search": {
        "threshold": 0.5,
        "min_chars_for_search": 2,
        "ignoreLocation": True,
    },
}
# Sphinx extensions
extensions = [
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "nbsphinx",
    "myst_parser",
    "jupyter_sphinx",
    "sphinx_design",
    "sphinx_jinja",
    "ansys_sphinx_theme.extension.autoapi",
    "numpydoc",
]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.11", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "pyvista": ("https://docs.pyvista.org/version/stable", None),
    "grpc": ("https://grpc.github.io/grpc/python/", None),
    "pint": ("https://pint.readthedocs.io/en/stable", None),
    "beartype": ("https://beartype.readthedocs.io/en/stable/", None),
    "docker": ("https://docker-py.readthedocs.io/en/stable/", None),
    "pypim": ("https://pypim.docs.pyansys.com/version/stable", None),
    "semver": ("https://python-semver.readthedocs.io/en/latest/", None),
}

# Conditional intersphinx mapping
if intersphinx_pyansys_geometry(switcher_version):
    intersphinx_mapping["ansys.geometry.core"] = (
        intersphinx_pyansys_geometry(switcher_version),
        None,
    )

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
suppress_warnings = [
    "autoapi.python_import_resolution",
    "design.grid",
    "config.cache",
    "design.fa-build",
]

# Examples gallery customization
nbsphinx_execute = "always"
nbsphinx_custom_formats = {
    ".mystnb": ["jupytext.reads", {"fmt": "mystnb"}],
}
nbsphinx_thumbnails = {
    "examples/01_getting_started/01_math": "_static/thumbnails/101_getting_started.png",
    "examples/01_getting_started/02_units": "_static/thumbnails/101_getting_started.png",
    "examples/01_getting_started/03_sketching": "_static/thumbnails/101_getting_started.png",
    "examples/01_getting_started/04_modeling": "_static/thumbnails/101_getting_started.png",
    "examples/01_getting_started/05_plotter_picker": "_static/thumbnails/101_getting_started.png",  # noqa: E501
    "examples/02_sketching/basic_usage": "_static/thumbnails/basic_usage.png",
    "examples/02_sketching/dynamic_sketch_plane": "_static/thumbnails/dynamic_sketch_plane.png",
    "examples/02_sketching/advanced_sketching_gears": "_static/thumbnails/advanced_sketching_gears.png",  # noqa: E501
    "examples/03_modeling/add_design_material": "_static/thumbnails/add_design_material.png",
    "examples/03_modeling/plate_with_hole": "_static/thumbnails/plate_with_hole.png",
    "examples/03_modeling/tessellation_usage": "_static/thumbnails/tessellation_usage.png",
    "examples/03_modeling/design_organization": "_static/thumbnails/design_organization.png",
    "examples/03_modeling/boolean_operations": "_static/thumbnails/boolean_operations.png",
    "examples/03_modeling/scale_map_mirror_bodies": "_static/thumbnails/scale_map_mirror_bodies.png",  # noqa: E501
    "examples/03_modeling/sweep_chain_profile": "_static/thumbnails/sweep_chain_profile.png",
    "examples/03_modeling/revolving": "_static/thumbnails/revolving.png",
    "examples/03_modeling/export_design": "_static/thumbnails/export_design.png",
    "examples/03_modeling/design_tree": "_static/thumbnails/design_tree.png",
    "examples/04_applied/01_naca_airfoils": "_static/thumbnails/naca_airfoils.png",
    "examples/04_applied/02_naca_fluent": "_static/thumbnails/naca_fluent.png",
}
nbsphinx_epilog = """
----

.. admonition:: Download this example

    Download this example as a `Jupyter Notebook <{cname_pref}/{ipynb_file_loc}>`_
    or as a `Python script <{cname_pref}/{py_file_loc}>`_.

""".format(
    cname_pref=f"https://{cname}/version/{switcher_version}",
    ipynb_file_loc="{{ env.docname }}.ipynb",
    py_file_loc="{{ env.docname }}.py",
)

nbsphinx_prolog = """

.. admonition:: Download this example

    Download this example as a `Jupyter Notebook <{cname_pref}/{ipynb_file_loc}>`_
    or as a `Python script <{cname_pref}/{py_file_loc}>`_.

----
""".format(
    cname_pref=f"https://{cname}/version/{switcher_version}",
    ipynb_file_loc="{{ env.docname }}.ipynb",
    py_file_loc="{{ env.docname }}.py",
)

typehints_defaults = "comma"
simplify_optional_unions = False

# additional logos for the latex coverpage
latex_additional_files = [watermark, ansys_logo_white, ansys_logo_white_cropped]

# change the preamble of latex with customized title page
# variables are the title of pdf, watermark
latex_elements = {"preamble": latex.generate_preamble(html_title)}

linkcheck_exclude_documents = ["index", "getting_started/local/index"]
linkcheck_ignore = [
    r"https://github.com/ansys/pyansys-geometry-binaries",
    r"https://download.ansys.com/",
    r".*/examples/.*.py",
    r".*/examples/.*.ipynb",
    r"_static/assets/.*",
]

# If we are on a release, we have to ignore the "release" URLs, since it is not
# available until the release is published.
if switcher_version != "dev":
    linkcheck_ignore.append(
        rf"https://github.com/ansys/pyansys-geometry/releases/download/v{__version__}/.*"
    )  # noqa: E501
    linkcheck_ignore.append(
        f"https://github.com/ansys/pyansys-geometry/releases/tag/v{__version__}"
    )  # noqa: E501

# User agent
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81"  # noqa: E501


# -- Declare the Jinja context -----------------------------------------------
exclude_patterns = []
BUILD_API = True if os.environ.get("BUILD_API", "true") == "true" else False
if not BUILD_API:
    exclude_patterns.append("autoapi")

BUILD_EXAMPLES = True if os.environ.get("BUILD_EXAMPLES", "true") == "true" else False
if not BUILD_EXAMPLES:
    exclude_patterns.append("examples/**")
    exclude_patterns.append("examples.rst")

jinja_contexts = {
    "main_toctree": {
        "build_api": BUILD_API,
        "build_examples": BUILD_EXAMPLES,
    },
    "linux_containers": {
        "add_windows_warnings": False,
    },
    "windows_containers": {
        "add_windows_warnings": True,
    },
    "wheelhouse-assets": {"assets": get_wheelhouse_assets_dictionary()},
}

nitpick_ignore_regex = [
    # Ignore typing
    (r"py:.*", r"optional"),
    (r"py:.*", r"ansys.geometry.core.typing.*"),
    (r"py:.*", r"Real.*"),
    (r"py:.*", r"SketchObject"),
    # Ignore API package
    (r"py:.*", r"ansys.api.geometry.v0.*"),
    (r"py:.*", r"GRPC.*"),
    (r"py:.*", r"method"),
    # Python std lib errors
    (r"py:obj", r"logging.PercentStyle"),
]


def convert_notebooks_to_scripts(app: sphinx.application.Sphinx, exception):
    """Convert notebooks to scripts.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx instance containing all the configuration for the documentation build.
    exception : Exception
        Exception raised during the build process.
    """
    if exception is None:
        # Get the examples output directory and retrieve all the notebooks
        import subprocess

        examples_output_dir = Path(app.outdir) / "examples"
        if not examples_output_dir.exists():
            logger.info("No examples directory found, skipping conversion...")
            return

        notebooks = examples_output_dir.glob("**/*.ipynb")
        count = 0
        for notebook in notebooks:
            count += 1
            logger.info(f"Converting {notebook}")  # using jupytext
            output = subprocess.run(
                [
                    "jupytext",
                    "--to",
                    "py",
                    str(notebook),
                    "--output",
                    str(notebook.with_suffix(".py")),
                ],
                env=os.environ,
                capture_output=True,
            )

            if output.returncode != 0:
                logger.error(f"Error converting {notebook} to script")
                logger.error(output.stderr)

        if count == 0:
            logger.warning("No notebooks found to convert to scripts")
        else:
            logger.info(f"Converted {count} notebooks to scripts")


def replace_version_in_qmd(file_path: Path, search, replace):
    """Update the version in cheatsheet."""
    with file_path.open("r") as file:
        content = file.read()

    logger.info(f"replace_version_in_qmd: replacing {search} with {replace}")
    content = content.replace(f"version: {search}", f"version: {replace}")

    with file_path.open("w") as file:
        file.write(content)


def update_qmd_mod(app: sphinx.application.Sphinx):
    """Update the version in cheatsheet."""
    cheathseet_path = Path(__file__).parent / "cheat_sheet.qmd"
    logger.info(f"Changing {cheathseet_path}")
    replace_version_in_qmd(cheathseet_path, "main", version)


def revert_qmd_mod(app: sphinx.application.Sphinx, exception):
    """Revert the version in cheatsheet that was modified."""
    cheathseet_path = Path(__file__).parent / "cheat_sheet.qmd"
    logger.info(f"Reverting {cheathseet_path}")
    replace_version_in_qmd(cheathseet_path, version, "main")


def setup(app: sphinx.application.Sphinx):
    """Run different hook functions during the documentation build.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx instance containing all the configuration for the documentation build.
    """
    logger.info("Configuring Sphinx hooks...")

    # At the beginning of the build process - update the version in cheatsheet
    app.connect("builder-inited", update_qmd_mod)

    if BUILD_EXAMPLES:
        # Run at the end of the build process
        logger.info("Connecting build-finished hook for converting notebooks to scripts...")
        app.connect("build-finished", convert_notebooks_to_scripts)

    # Reverting the version in cheatsheet
    app.connect("build-finished", revert_qmd_mod)
