from ansys.geometry.core import __version__


def test_pkg_version():
    assert __version__ == "0.1.dev0"
