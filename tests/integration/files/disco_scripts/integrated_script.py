doc = GetActiveDocument()
radius = MM(int(argsDict["radius"]))

sphere = Sphere.Create(Frame.World, radius)
u_range = Interval.Create(0, 2 * math.pi)
v_range = Interval.Create(-math.pi / 2, math.pi / 2)
box = BoxUV.Create(u_range, v_range)
b = Body.CreateSurfaceBody(sphere, box)
db = DesignBody.Create(doc.MainPart, "sphere", b)

numBodies = doc.MainPart.Bodies.Count

result = {"numBodies": numBodies}