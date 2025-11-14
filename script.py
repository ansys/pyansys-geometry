from ansys.geometry.core import Modeler

modeler = Modeler(host="localhost", port=654, proto_version="v0")

print(modeler)

modeler.close()
