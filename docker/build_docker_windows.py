# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Script to build docker image for the project."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import urllib.request

# First, get all environment variables that start with AWP_ROOT
awp_root: dict[int, str] = {}
for env_key, env_val in os.environ.items():
    if env_key.startswith("AWP_ROOT"):
        # There is an Ansys installation... Check that the version is at
        # least 2024R1. Environment variables are in the form
        # AWP_ROOT241=/path/to/2024R1
        #
        # Get the version number
        version = int(env_key.split("AWP_ROOT")[1])
        if version < 241:
            # This version is too old, so we will ignore it
            continue
        else:
            # This version is new enough, so we will add it to the list
            awp_root[version] = env_val

if len(awp_root) == 0:
    # There are no Ansys installations
    print("XXXXXXX No Ansys compatible installations found.. exiting process. XXXXXXX")
    print("XXXXXXX Please install Ansys 2024R1 or newer.                      XXXXXXX")
    exit(0)

# Request the user to select the version of Ansys to use
print(">>> Select the version of Ansys to use:")
for i, (env_key, _) in enumerate(awp_root.items()):
    print(f"{i + 1}: {env_key}")
selection = input("Selection [default - last option]: ")

# If no selection is made, use the first version
if selection == "":
    print("... No selection made, using default")
    selection = len(awp_root)
else:
    selection = int(selection)
ANSYS_VER = list(awp_root.keys())[selection - 1]
print(f">>> Using {ANSYS_VER}")

# Get the path to the Ansys installation
ANSYS_PATH = Path(awp_root[ANSYS_VER])

# Starting on 2025R2, only Core Service is available
# Before that, only DMS is available
if ANSYS_VER >= 252:
    print(">>> Using Core Service")
    backend_selection = 2  # Core Service
else:
    print(">>> Using DMS Service")
    backend_selection = 1 # DMS Service

# Verify that the Geometry Service is installed
if not Path.exists(ANSYS_PATH / "GeometryService"):
    print("XXXXXXX Geometry Service not installed.. exiting process. XXXXXXX")
    exit(0)

# Create a temporary directory to copy the Geometry Service files to
print(">>> Creating temporary directory for building docker image")
TMP_DIR = Path(tempfile.mkdtemp(prefix="docker_geometry_service_"))

# Copy the Geometry Service files to the temporary directory
print(f">>> Copying Geometry Service files to temporary directory to {TMP_DIR}")
if backend_selection == 1:
    BIN_DIR = TMP_DIR / "archive" / "bin" / "x64" / "Release_Headless" / "net472"
else:
    BIN_DIR = TMP_DIR / "archive" / "bin" / "x64" / "Release_Core_Windows" / "net8.0"

# Create the directory structure
shutil.copytree(
    ANSYS_PATH / "GeometryService",
    BIN_DIR,
)

# ZIP the temporary directory and delete it
print(">>> Zipping temporary directory. This might take some time...")
zip_file = shutil.make_archive(
    "windows-dms-binaries" if backend_selection == 1 else "windows-core-binaries",
    "zip",
    root_dir=TMP_DIR / "archive",
)

# Move the ZIP file to the docker directory
print(">>> Moving ZIP file to temporary directory")
shutil.move(zip_file, TMP_DIR)

# Remove the temporary directory
print(">>> Removing Geometry Service files")
shutil.rmtree(TMP_DIR / "archive")

# Download the Dockerfile from the repository
print(">>> Downloading Dockerfile")
if backend_selection == 1:
    dockerfile_url = "https://raw.githubusercontent.com/ansys/pyansys-geometry/main/docker/windows/dms/Dockerfile"
else:
    dockerfile_url = "https://raw.githubusercontent.com/ansys/pyansys-geometry/main/docker/windows/coreservice/Dockerfile"
urllib.request.urlretrieve(
    dockerfile_url,
    TMP_DIR / "Dockerfile",
)

# Search for the AWP_ROOT* env variables and replace them with the correct
# value
print(">>> Updating Dockerfile")
with Path.open(TMP_DIR / "Dockerfile", "r") as f:
    dockerfile = f.read()

# Find environment variables that start with AWP_ROOT
# inside the Dockerfile and replace them with the correct value
if backend_selection == 1:
    LENGTH_NO_VER = 12
    LENGTH_VER = LENGTH_NO_VER + 3
    line = dockerfile.find("ENV AWP_ROOT")
    if line != -1:
        # Get the environment variable name
        env_var = f"{dockerfile[line : LENGTH_NO_VER + line]}{ANSYS_VER}"
        # Replace the environment variable with the correct value
        dockerfile = dockerfile.replace(
            dockerfile[line : LENGTH_VER + line],
            env_var,
        )
        # Write the updated Dockerfile
        with Path.open(TMP_DIR / "Dockerfile", "w") as f:
            f.write(dockerfile)
    else:
        print(
            "XXXXXXX No AWP_ROOT environment variable found in Dockerfile.. exiting process. XXXXXXX"  # noqa: E501
        )
        exit(0)

# Check if Docker is installed on the system
print(">>> Checking if Docker is installed")
if shutil.which("docker") is None:
    print("XXXXXXX Docker is not installed.. exiting process. XXXXXXX")
    exit(0)

# Build the docker image
print(">>> Building docker image. This might take some time...")
if backend_selection == 1:
    image_name = "ghcr.io/ansys/geometry:windows-latest"
else:
    image_name = "ghcr.io/ansys/geometry:core-windows-latest"

out = subprocess.run(
    ["docker", "build", "-t", image_name, "."],
    cwd=TMP_DIR,
    capture_output=True,
)

if out.returncode != 0:
    print(out.stdout.decode())
    print(out.stderr.decode())
    print("XXXXXXX Docker build failed.. exiting process. XXXXXXX")
    exit(0)
else:
    print(">>> Docker image built successfully")
    print(">>> Cleaning up temporary directory")
    shutil.rmtree(TMP_DIR)
    print(">>> Docker image is ready to use")
