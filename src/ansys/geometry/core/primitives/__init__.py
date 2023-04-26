"""Provides the PyGeometry ``primitives`` subpackage."""

from ansys.geometry.core.primitives.circle import Circle, CircleEvaluation
from ansys.geometry.core.primitives.cone import Cone, ConeEvaluation
from ansys.geometry.core.primitives.cylinder import Cylinder, CylinderEvaluation
from ansys.geometry.core.primitives.ellipse import Ellipse, EllipseEvaluation
from ansys.geometry.core.primitives.line import Line, LineEvaluation
from ansys.geometry.core.primitives.parameterization import (
    Parameterization,
    ParamForm,
    ParamType,
    ParamUV,
)
from ansys.geometry.core.primitives.sphere import Sphere, SphereEvaluation
from ansys.geometry.core.primitives.surface_evaluation import SurfaceEvaluation
from ansys.geometry.core.primitives.torus import Torus
