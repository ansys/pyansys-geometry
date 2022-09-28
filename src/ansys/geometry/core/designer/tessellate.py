"""Support body tessellation."""
from ansys.api.geometry.v0.models_pb2 import Tessellation
import numpy as np
import pyvista as pv


def tess_to_pd(tess: Tessellation) -> pv.PolyData:
    """Convert a ansys.api.geometry.Tessellation to a pyvista.PolyData."""
    return pv.PolyData(np.array(tess.vertices).reshape(-1, 3), tess.faces)
