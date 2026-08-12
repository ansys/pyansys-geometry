# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Script to build the Linux Core Service docker image for the project."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import urllib.request

# Linux Core Service requires at least 2025R2 (252)
awp_root: dict[int, str] = {}

print(">>> How would you like to specify the Ansys installation?")
print("1: Auto-detect from AWP_ROOT* environment variables")
print("2: Provide version and path manually")
detect_mode = input("Selection [default - 1]: ").strip()

if detect_mode in ("", "1"):
    for env_key, env_val in os.environ.items():
        if env_key.startswith("AWP_ROOT"):
            version = int(env_key.split("AWP_ROOT")[1])
            if version >= 252:
                awp_root[version] = env_val

    if len(awp_root) == 0:
        print(
            "XXXXXXX No compatible AWP_ROOT* environment variables found.. exiting process. XXXXXXX"
        )
        print(
            "XXXXXXX Please re-run and choose option 2 to provide the path manually.        XXXXXXX"
        )
        exit(0)

    print(">>> Select the version of Ansys to use:")
    for i, (ver, _) in enumerate(awp_root.items()):
        print(f"{i + 1}: {ver}")
    selection = input("Selection [default - last option]: ").strip()
    selection = len(awp_root) if selection == "" else int(selection)
    ANSYS_VER = list(awp_root.keys())[selection - 1]
else:
    manual_version = input(">>> Ansys version (e.g. 252 for 2025R2, minimum 252): ").strip()
    manual_path = input(">>> Path to Ansys installation (e.g. /ansys_inc/v252): ").strip()
    try:
        ANSYS_VER = int(manual_version)
    except ValueError:
        print("XXXXXXX Invalid version provided.. exiting process. XXXXXXX")
        exit(0)
    if ANSYS_VER < 252:
        print("XXXXXXX Version must be 252 (2025R2) or newer.. exiting process. XXXXXXX")
        exit(0)
    if not Path(manual_path).exists():
        print("XXXXXXX Provided path does not exist.. exiting process. XXXXXXX")
        exit(0)
    awp_root[ANSYS_VER] = manual_path

print(f">>> Using {ANSYS_VER}")

# Get the path to the Ansys installation
ANSYS_PATH = Path(awp_root[ANSYS_VER])

# Determine dotnet/net version based on Ansys release
if ANSYS_VER >= 271:
    print(">>> Using .NET 10 based on Ansys release version")
    net_folder = "net10.0"
    dockerfile_suffix = ".net10"
else:
    print(">>> Using .NET 8 based on Ansys release version")
    net_folder = "net8.0"
    dockerfile_suffix = ""

# Verify that the Geometry Service is installed
if not Path.exists(ANSYS_PATH / "GeometryService"):
    print("XXXXXXX Geometry Service not installed.. exiting process. XXXXXXX")
    exit(0)

# Create a temporary directory to copy the Geometry Service files to
print(">>> Creating temporary directory for building docker image")
TMP_DIR = Path(tempfile.mkdtemp(prefix="docker_geometry_service_"))

# Copy the Geometry Service files to the temporary directory
print(f">>> Copying Geometry Service files to temporary directory to {TMP_DIR}")
BIN_DIR = TMP_DIR / "archive" / "bin" / "x64" / "Release_Core_Linux" / net_folder

# Create the directory structure
shutil.copytree(
    ANSYS_PATH / "GeometryService",
    BIN_DIR,
)

# ZIP the temporary directory and delete it
print(">>> Zipping temporary directory. This might take some time...")
zip_file = shutil.make_archive(
    "linux-core-binaries",
    "zip",
    root_dir=TMP_DIR / "archive",
)

# Move the ZIP file to the temporary directory
print(">>> Moving ZIP file to temporary directory")
shutil.move(zip_file, TMP_DIR)

# Remove the temporary directory
print(">>> Removing Geometry Service files")
shutil.rmtree(TMP_DIR / "archive")

# Download the Dockerfile from the repository
print(">>> Downloading Dockerfile")
dockerfile_url = f"https://raw.githubusercontent.com/ansys/pyansys-geometry/main/docker/linux/coreservice/Dockerfile{dockerfile_suffix}"
urllib.request.urlretrieve(
    dockerfile_url,
    TMP_DIR / "Dockerfile",
)

# Check if Docker is installed on the system
print(">>> Checking if Docker is installed")
if shutil.which("docker") is None:
    print("XXXXXXX Docker is not installed.. exiting process. XXXXXXX")
    exit(0)

# Build the docker image
print(">>> Building docker image. This might take some time...")
image_name = "ghcr.io/ansys/geometry:core-linux-latest"

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
