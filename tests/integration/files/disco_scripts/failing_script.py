# Python Discovery Script
doc = Document.Create()

sphere = Sphere.Create(Frame.Create(Point.Create(0,0,0), Direction.Create(1,0,0), Direction.Create(0,1,0)), 1)
u_range = Interval.Create(0, 2*math.pi)
v_range = Interval.Create(-math.pi/2, math.pi/2)
box = BoxUV.Create(u_range, v_range)
import numpy as np
b = Body.CreateSurfaceBody(sphere, box)
db = DesignBody.Create(doc.MainPart, "sphere", b)

result = {"design": doc, "design_body": db}
