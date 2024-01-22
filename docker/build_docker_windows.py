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
import shutil
import subprocess
import urllib.request

# First, get all environment variables that start with AWP_ROOT
awp_root = {}
for env_key, env_val in os.environ.items():
    if env_key.startswith("AWP_ROOT"):
        # There is an Ansys installation... Check that the version is at
        # least 2023R2. Environment variables are in the form
        # AWP_ROOT232=/path/to/2023R2
        #
        # Get the version number
        version = env_key.split("AWP_ROOT")[1]
        if version < "232":
            # This version is too old, so we will ignore it
            continue
        else:
            # This version is new enough, so we will add it to the list
            awp_root[version] = env_val

if len(awp_root) == 0:
    # There are no Ansys installations
    print("XXXXXXX No Ansys installations found.. exiting process. XXXXXXX")
    exit(0)

# Request the user to select the version of Ansys to use
print(">>> Select the version of Ansys to use:")
for i, (env_key, _) in enumerate(awp_root.items()):
    print(f"{i+1}: {env_key}")
selection = input("Selection [default - last option]: ")

# If no selection is made, use the first version
if selection == "":
    print("... No selection made, using default")
    selection = len(awp_root)
else:
    selection = int(selection)
print(f">>> Using {list(awp_root.keys())[selection-1]}")

# Get the path to the Ansys installation
ANSYS_VER = list(awp_root.keys())[selection - 1]
ANSYS_PATH = list(awp_root.values())[selection - 1]

# Verify that the Geometry Service is installed
if not os.path.exists(os.path.join(ANSYS_PATH, "GeometryService")):
    print("XXXXXXX Geometry Service not installed.. exiting process. XXXXXXX")
    exit(0)

# Create a temporary directory to copy the Geometry Service files to
print(">>> Creating temporary directory for building docker image")
TMP_DIR = os.path.join(os.getcwd(), "docker_geometry_service")
if os.path.exists(TMP_DIR):
    # Remove the directory if it already exists
    shutil.rmtree(TMP_DIR)
os.mkdir(TMP_DIR)

# Copy the Geometry Service files to the temporary directory
print(">>> Copying Geometry Service files to temporary directory")
BIN_DIR = os.path.join(TMP_DIR, "bins", "DockerWindows", "bin", "x64", "Release_Headless", "net472")
# Create the directory structure
shutil.copytree(
    os.path.join(ANSYS_PATH, "GeometryService"),
    BIN_DIR,
)

# ZIP the temporary directory and delete it
print(">>> Zipping temporary directory. This might take some time...")
zip_file = shutil.make_archive(
    "windows-binaries",
    "zip",
    root_dir=os.path.join(TMP_DIR, "bins"),
)

# Move the ZIP file to the docker directory
print(">>> Moving ZIP file to temporary directory")
shutil.move(zip_file, TMP_DIR)

# Remove the temporary directory
print(">>> Removing Geometry Service files")
shutil.rmtree(os.path.join(TMP_DIR, "bins"))

# Download the Dockerfile from the repository
print(">>> Downloading Dockerfile")
urllib.request.urlretrieve(
    "https://raw.githubusercontent.com/ansys/pyansys-geometry/main/docker/Dockerfile.windows",
    os.path.join(TMP_DIR, "Dockerfile"),
)

# Search for the AWP_ROOT* env variables and replace them with the correct
# value
print(">>> Updating Dockerfile")
with open(os.path.join(TMP_DIR, "Dockerfile"), "r") as f:
    dockerfile = f.read()

# Find environment variables that start with AWP_ROOT
# inside the Dockerfile and replace them with the correct value
LENGTH_NO_VER = 12
LENGTH_VER = LENGTH_NO_VER + 3
line = dockerfile.find("ENV AWP_ROOT")
if line != -1:
    # Get the environment variable name
    env_var = dockerfile[line : LENGTH_NO_VER + line] + ANSYS_VER
    # Replace the environment variable with the correct value
    dockerfile = dockerfile.replace(
        dockerfile[line : LENGTH_VER + line],
        env_var,
    )
else:
    print("XXXXXXX No AWP_ROOT environment variable found.. exiting process. XXXXXXX")
    exit(0)

# Check if Docker is installed on the system
print(">>> Checking if Docker is installed")
if shutil.which("docker") is None:
    print("XXXXXXX Docker is not installed.. exiting process. XXXXXXX")
    exit(0)

# Build the docker image
print(">>> Building docker image. This might take some time...")
out = subprocess.run(
    ["docker", "build", "-t", "ghcr.io/ansys/geometry:windows-latest", "."],
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
