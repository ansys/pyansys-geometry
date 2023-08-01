"""Provides constant and environment variables values or names."""

WINDOWS_GEOMETRY_SERVICE_FOLDER = "GeometryService"
"""
Default Geometry Service's folder name into the unified installer.
"""

DISCOVERY_FOLDER = "Discovery"
"""
Default Discovery's folder name into the unified installer.
"""

SPACECLAIM_FOLDER = "scdm"
"""
Default SpaceClaim's folder name into the unified installer.
"""

ADDINS_SUBFOLDER = "Addins"
"""
Default global Addins's folder name into the unified installer.
"""

BACKEND_SUBFOLDER = "ApiServer"
"""
Default backend's folder name into the ``ADDINS_SUBFOLDER`` folder.
"""

MANIFEST_FILENAME = "Presentation.ApiServerAddIn.Manifest.xml"
"""
Default backend's addin filename.
To be used only for local start of Ansys Discovery or Ansys SpaceClaim.
"""

GEOMETRY_SERVICE_EXE = "Presentation.ApiServerDMS.exe"
"""
The Windows Geometry Service's filename.
"""

DISCOVERY_EXE = "Discovery.exe"
"""
The Ansys Discovery's filename.
"""

SPACECLAIM_EXE = "SpaceClaim.exe"
"""
The Ansys SpaceClaim's filename.
"""

BACKEND_LOG_LEVEL_VARIABLE = "LOG_LEVEL"
"""
The backend's log level environment variable for local start.
"""

BACKEND_TRACE_VARIABLE = "ENABLE_TRACE"
"""
The backend's enable trace environment variable for local start.
"""

BACKEND_HOST_VARIABLE = "API_ADDRESS"
"""
The backend's ip address environment variable for local start.
"""

BACKEND_PORT_VARIABLE = "API_PORT"
"""
The backend's port number environment variable for local start.
"""

BACKEND_API_VERSION_VARIABLE = "API_VERSION"
"""
The backend's api version environment variable for local start.
To be used only with Ansys Discovery and Ansys SpaceClaim.
"""

BACKEND_SPACECLAIM_OPTIONS = "--spaceclaim-options"
"""
The additional argument for local Ansys Discovery start.
To be used only with Ansys Discovery.
"""

BACKEND_ADDIN_MANIFEST_ARGUMENT = "/ADDINMANIFESTFILE="
"""
The argument to specify the backend's addin manifest file's path.
To be used only with Ansys Discovery and Ansys SpaceClaim.
"""