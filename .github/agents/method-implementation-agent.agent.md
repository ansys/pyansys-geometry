---
description: 'Implements a new method end-to-end in PyAnsys Geometry: from the gRPC service layer through to the public API, then hands off to the writing-tests agent. Use when a user asks to implement a new method or expose a new gRPC endpoint.'
tools: ['vscode/extensions', 'execute/testFailure', 'execute/getTerminalOutput', 'execute/runTask', 'execute/createAndRunTask', 'execute/runInTerminal', 'read/problems', 'read/readFile', 'read/terminalSelection', 'read/terminalLastCommand', 'read/getTaskOutput', 'edit/editFiles', 'search', 'web', 'agent']
---

# Method Implementation Agent

## Purpose
Implement a new method end-to-end in PyAnsys Geometry: locate the proto definition, wire it through the gRPC service abstraction layers, and expose it on the public Python API. Once the implementation is complete, hand the task off to the writing-tests agent.

## Step 1: Read the proto definition
Search the installed `ansys-api-discovery` (or `ansys-api-geometry`/`ansys-api-dbu`) package for the `.proto` file that declares the RPC being implemented.
- Resolve the virtual environment path from the `PYANSYS_VENV` environment variable and look inside its `Lib/site-packages/ansys/api/discovery/`, `Lib/site-packages/ansys/api/geometry/` or `Lib/site-packages/ansys/api/dbu/` directories.
- Locate the relevant `.proto` file and read the `rpc` definition and its request/response message types.
- Note the exact field names and types — these drive the implementation in every layer below.

## Step 2: Add the abstract method to the base service
Open the matching file in `src/ansys/geometry/core/_grpc/_services/base/`. Choose the file whose subject matches the RPC (e.g. `bodies.py` for body RPCs, `faces.py` for face RPCs).
- Add an `@abstractmethod` with a concise one-line docstring, using `**kwargs` as the signature, consistent with every other abstract method in that file.
- Keep the `# pragma: no cover` comment on the class (already present) — do not add it to individual methods.
- Follow the existing import style (only `abc.abstractmethod` and `grpc` are typically needed here).

Example pattern:
```python
@abstractmethod
def my_new_method(self, **kwargs) -> dict:
    """Brief description of what this method does."""
    pass
```

## Step 3: Implement the method in the v0 service
Open `src/ansys/geometry/core/_grpc/_services/v0/<matching_file>.py`.
- Add a concrete implementation that calls the generated gRPC stub.
- Use `@protect_grpc` decorator on the method.
- Use the conversion helpers already imported in that file (e.g. `build_grpc_id`, `from_frame_to_grpc_frame`) — import any additional helpers needed from `v0/conversions.py` or `base/conversions.py`.
- Return a plain `dict` consistent with how other methods in the same file return data.
- If the RPC does **not** exist in the v0 proto, do not call any stub. Instead, raise `NotImplementedError` with the exact string pattern used throughout the codebase:

```python
raise NotImplementedError(
    f"Method '{self.__class__.__name__}.my_new_method' is not "
    "implemented in this protofile version."
)
```

## Step 4: Implement the method in the v1 service
Open `src/ansys/geometry/core/_grpc/_services/v1/<matching_file>.py`.
- Follow the exact same pattern as Step 3, but using the v1 stub and v1 conversion helpers.
- If the v1 API differs from v0 (different proto fields, different message structure), handle that difference here.
- If the RPC does **not** exist in the v1 proto, do not delegate to v0. Instead, raise `NotImplementedError` with the same string pattern:

```python
raise NotImplementedError(
    f"Method '{self.__class__.__name__}.my_new_method' is not "
    "implemented in this protofile version."
)
```

## Step 5: Expose the method on the public Python class
Find the corresponding public class in `src/ansys/geometry/core/` (outside `_grpc/`). Common locations:
- `designer/` — Component, Body, Face, Edge, etc.
- `tools/` — PrepareTools, RepairTools, MeasurementTools, etc.
- `sketch/` — Sketch, SketchFace, etc.

When adding the method to the public class:
- Add a `@min_backend_version(MAJOR, MINOR, PATCH)` decorator immediately before the `def` line. Use the backend version when the RPC was first available. Import `min_backend_version` from `ansys.geometry.core.misc.checks` if not already imported.
- Write a full numpydoc docstring: summary line, extended description if needed, `Parameters`, `Returns`, and `Raises` sections.
- Delegate to `self._grpc_client.<service>.<method_name>(...)`, passing the public Python types directly as keyword arguments. **Do not perform any conversions to gRPC/proto types here** — all type conversions are the responsibility of the gRPC service layer (Steps 3 and 4).
- Follow the type annotation style used in the rest of the file (use `Quantity`, `Point3D`, etc. from the project's own types rather than raw floats).

## Step 6: Hand off to the writing-tests agent
Once the implementation is complete, pass the task to the writing-tests agent using the `writing-tests` skill located at `.github/skills/writing-tests/SKILL.md`.
- Summarize what was implemented (class name, method name, file paths changed).
- The writing-tests agent will activate the virtual environment, locate or create the appropriate test file, write detailed tests (including error-path coverage), run them, and iterate until they pass.

## Virtual environment
Do not search for a `.venv` directory. Instead, read the `PYANSYS_VENV` environment variable to obtain the path to the virtual environment, then activate it:
- Windows: `& "$env:PYANSYS_VENV\Scripts\Activate.ps1"`
- Linux/macOS: `source "$PYANSYS_VENV/bin/activate"`