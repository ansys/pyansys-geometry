---
name: api-deprecation-and-versioning
description: 'Use when changing public API signatures, argument positions, names or defaults, deprecating or removing arguments, adding deprecated_argument decorators, or assessing release compatibility and versioning at the _grpc layer in PyAnsys Geometry.'
---

# API Deprecation and Versioning

Guide API changes without silently breaking existing callers. Apply this workflow
when implementing or reviewing argument changes and deprecations in this repository.

## Agent Scope

Agents implement and review code, tests, and documentation; they never perform
releases or bump package versions. Read version information only to assess
compatibility and populate deprecation metadata. Do not edit the project version,
create release tags, publish packages, or invoke release workflows.

Release planning and execution belong to maintainers. References below to minor
or major releases describe compatibility requirements to report, not actions for
the agent to perform. If release intent is unclear, ask the user rather than
choosing or scheduling a release.

## Public API Compatibility Rules

- A user-facing argument must not change position, name, or default value without
  a minor release. A patch release is not sufficient.
- Avoid these changes unless necessary. Prefer retaining the existing signature
  and behavior, with a compatible replacement when needed.
- A minor release is a release requirement, not permission to bypass deprecation.
  Retain deprecated arguments and their behavior until the declared removal version.
- Never bump the package version to accommodate a signature change. Confirm
  maintainer-provided release intent or report the required minor release.
- Check positional as well as keyword callers. Inserting a parameter before an
  existing parameter changes the latter's position even if its name is unchanged.

## Procedure

1. Identify the public entry point and compare its signature and argument behavior
   with the existing API. Check nearby callers, tests, and documentation. Record
   any change to argument position, name, or default value.
2. Decide whether the change is necessary. If a compatible implementation meets
   the requirement, preserve the existing arguments. Otherwise, confirm that the
   signature change targets a maintainer-planned minor release before proceeding.
   Do not schedule or perform that release, or bump the version yourself.
3. Read the current package version from `pyproject.toml` without changing it;
   do not use an installed package version or an Ansys backend version as the
   release authority. Derive the public version for deprecation metadata using
   the convention below; ask the user if maintainer-provided release intent differs.
4. For every deprecated argument, use `deprecated_argument` from
   `ansys.geometry.core.misc.checks`. Always supply `arg`, `version` (the current
   version), and `remove` (two minor releases after the current version). Supply
   `alternative` when a replacement exists, or `info` when migration needs explanation.
5. Keep the deprecated argument's existing position, name, default, and supported
   behavior throughout the deprecation window. Implement any forwarding to the
   replacement explicitly. Define what happens when both old and new arguments
   are supplied, following nearby API conventions; do not silently discard either.
6. Update the argument documentation with the replacement and removal version.
   Follow the repository's release-note conventions when a release note is needed.
7. Add or update focused tests in the existing test file. Verify legacy positional
   and keyword calls, omitted/default values, replacement calls, and conflicts
   between old and new arguments where applicable. Check deprecation warnings
   using explicit warning assertions.
8. Run the focused checks for the changed API. In the completion summary, state
   the compatibility impact, required release, deprecation/removal versions, and
   any checks that could not run.

## Deprecation Versions

- Compute removal by advancing the minor release twice, not by adding two patch
  releases or using an Ansys product release number. This calculation sets the
  decorator's `remove` metadata only; it does not bump the project version or
  schedule a release.
- For example, current version `0.18.2` gives removal version `0.20.0`.
- A development version such as `0.19.dev0` refers to the upcoming public release
  `0.19.0`; use `version="0.19.0"`
  and `remove="0.21.0"`. If the intended release differs, ask before setting metadata.
- If the removal window crosses a planned major release or the release sequence
  is otherwise unclear, confirm the two-minor-release schedule instead of guessing.
- Remove a deprecated argument only when maintainer-provided release intent reaches
  its declared removal version and the requested work authorizes removal. Update
  docs and tests then; never bump the version to make an argument eligible for removal.

Example decorator metadata (preserve the existing function signature and behavior):

```python
from ansys.geometry.core.misc.checks import deprecated_argument

@deprecated_argument(
    arg="old_argument",
    alternative="replacement_argument",
    version="0.19.0",
    remove="0.21.0",
)
```

## Decorator Limitations

The existing decorator warns only when the deprecated argument is supplied by
keyword with a value other than `None`. Positional calls and explicit `None` do
not currently warn. Other falsey values still warn. Do not claim warning coverage
that the implementation does not provide.

The decorator forwards arguments unchanged. Its version fields are warning text,
not automatic migration, release gates, or removal enforcement. Compatibility
must be maintained in the method implementation itself.

Use `src/ansys/geometry/core/misc/checks.py` as the implementation reference and
`GeometryCommands.split_body` in
`src/ansys/geometry/core/designer/geometry_commands.py` as an existing migration
example. The decorator's focused regression check is:

```text
pytest tests/test_misc_checks.py -k test_deprecated_argument_decorator
```

## Versioning at the _grpc Layer

### Protocol and Release Boundaries

- The v0 backend/proto contract is frozen and will never change. All new proto
  changes must target v1 or a later protocol version; never add RPCs or fields to v0.
- v0 is compatible with Ansys releases up to and including 26R1.
- v1 is compatible with Ansys releases starting at 26R1. Both protocol versions
  are compatible at 26R1; do not turn this overlap into an exclusive cutoff.
- Do not drop v0 support before a major release of `pyansys-geometry`. A minor
  release or the introduction of a v1-only feature does not authorize dropping v0.
- Keep Python package versions, proto versions (`v0`, `v1`), and Ansys release
  versions distinct. Public argument deprecation metadata uses Python package
  versions, not protocol numbers or Ansys releases.

### Unsupported Methods in v0

When a shared service interface gains a method that v0 cannot support, implement
the actual functionality in v1 or later. Keep the v0 service implementation
consistent with the shared interface, but raise Python's `NotImplementedError`
(not C#'s `NotImplementedException`) for the unsupported operation. Adding this
local stub does not change the frozen v0 backend/proto contract.

Follow the existing pattern in
`src/ansys/geometry/core/_grpc/_services/v0/components.py` and
`src/ansys/geometry/core/_grpc/_services/v0/datum_lines.py`:

```python
@protect_grpc
def move_bodies_to_component(self, **kwargs) -> dict:
    raise NotImplementedError(
        f"Method '{self.__class__.__name__}.move_bodies_to_component' is not "
        "implemented in this protofile version."
    )
```

Import `protect_grpc` from `ansys.geometry.core.errors` when needed. Match the
shared interface and nearby service conventions. The error must name the actual
class and method and explain that this protofile version does not implement it.
Do not return an empty success response, silently ignore unsupported arguments,
call nonexistent v0 RPCs, or add v1 protobuf imports to a v0 implementation.

When a method gains additional arguments in v1 or later, do not implement those
arguments in v0 if they are absent from the frozen v0 proto. Keep the v0 method
limited to the arguments and request fields available in v0, and preserve its
existing behavior. Do not add v1-only arguments or request fields to the v0
implementation, or add `NotImplementedError` branches just for those arguments.

### gRPC Change Checks

1. Identify the selected protocol and supported backend releases. Preserve
   existing protocol negotiation in `src/ansys/geometry/core/_grpc/_version.py`;
   do not select a protocol solely from a Python package version.
2. Implement new proto functionality in v1 or later, with explicit unsupported
   handling in v0 wherever the shared interface requires it.
3. Write a normal test for the behavior being changed. Do not check the protocol
  version or add separate v0-specific tests; the developer will add version-specific
  coverage if needed.
4. If changing protocol selection or release compatibility checks, verify the
   26R1 overlap, v0 compatibility below it, and v1 compatibility above it. Run
   backend-dependent checks only with a suitable backend and report any gaps.

## Completion Checklist

- No package version was bumped and no release was performed, tagged, published,
  or scheduled by the agent. Release requirements are reported to maintainers.
- Existing public argument positions, names, and defaults are preserved, or the
  necessary changes target an explicitly maintainer-planned minor release.
- Every newly deprecated argument has a decorator with current and removal
  versions; removal metadata is two minor releases later.
- Legacy behavior remains available during the deprecation window.
- Migration documentation and focused compatibility tests reflect actual behavior.
- The v0 backend/proto contract remains unchanged, unsupported operations fail
  explicitly, and v0 support is retained until an authorized major package release.
- Any unresolved release-version or protocol policy decision is reported explicitly.