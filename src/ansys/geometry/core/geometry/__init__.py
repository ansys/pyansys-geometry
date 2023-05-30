"""Provides the PyGeometry ``geometry`` subpackage."""

from ansys.geometry.core.geometry.curves.circle import Circle, CircleEvaluation
from ansys.geometry.core.geometry.curves.curve import Curve
from ansys.geometry.core.geometry.curves.ellipse import Ellipse, EllipseEvaluation
from ansys.geometry.core.geometry.curves.line import Line, LineEvaluation
from ansys.geometry.core.geometry.parameterization import (
    Interval,
    Parameterization,
    ParamForm,
    ParamType,
    ParamUV,
)
from ansys.geometry.core.geometry.surfaces.cone import Cone, ConeEvaluation
from ansys.geometry.core.geometry.surfaces.cylinder import Cylinder, CylinderEvaluation
from ansys.geometry.core.geometry.surfaces.sphere import Sphere, SphereEvaluation
from ansys.geometry.core.geometry.surfaces.surface import Surface
from ansys.geometry.core.geometry.surfaces.surface_evaluation import SurfaceEvaluation
from ansys.geometry.core.geometry.surfaces.torus import Torus
