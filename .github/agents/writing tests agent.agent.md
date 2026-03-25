---
description: 'Writes unit and integration tests for PyAnsys Geometry code. Use when a user asks to write tests, add code coverage, test a new feature, or write unit tests for something specific.'
tools: ['execute/runInTerminal', 'execute/getTerminalOutput', 'read/readFile', 'read/problems', 'edit/editFiles', 'search']
---

# Writing Tests Agent

## Purpose
Write unit and integration tests for PyAnsys Geometry code. This agent ensures code works properly by creating comprehensive test coverage, running tests against a geometry service, and iterating until tests pass.

## When to Use
- User asks to "write tests" or "add unit tests"
- User wants to "add code coverage" for existing code
- User asks to "test a new feature" or specific functionality
- User says "write a unit test for" a method or class

## Workflow

### Step 1: Activate Virtual Environment
Look for a `.venv` directory in the workspace folder (`pyansys-geometry/.venv`). If one exists, activate it:
- Windows: `./.venv/Scripts/Activate.ps1`
- Linux/macOS: `source ./.venv/bin/activate`

If no `.venv` exists, check the parent directory. If still not found, follow `.github/copilot-instructions.md` "Install (developer)" instructions to create one.

### Step 2: Understand the Code to Test
- Read any code the user references or wants tested
- Understand the method signatures, parameters, return types, and error conditions
- Note any dependencies (e.g., modeler sessions, fixtures, other services)

### Step 3: Locate or Create the Test File
- Navigate to the `tests/` folder
- Find the most relevant existing test file based on the code being tested:
  - Unit tests go in `tests/` (root level test files)
  - Integration tests requiring a modeler session go in `tests/integration/`
- If no relevant test file exists, create a new one following the naming convention `test_<module_name>.py`

### Step 4: Write Comprehensive Tests
- Use pytest style and fixtures
- Leverage existing fixtures for modeler sessions (for integration tests)
- Include a docstring briefly describing what each test does
- Test thoroughly:
  - Happy path scenarios
  - Edge cases and boundary conditions
  - Error paths that raise exceptions
  - Before/after state verification (e.g., if code alters a face, test the area before and after)
- Follow PyAnsys coding style guidelines
- **Code style — line length:** The project enforces a maximum line length of **100 characters** (configured in `pyproject.toml`). Every line of test code you write must stay within this limit. When a call expression would exceed 100 characters, break it across multiple lines using Python's implicit line continuation inside parentheses:
  ```python
  # Too long (> 100 chars) — do not write this:
  curves = modeler.geometry_commands.revolve_points([dp1, dp2, dp3], axis, Angle(np.pi, UNITS.rad))

  # Correct — wrap the arguments:
  curves = modeler.geometry_commands.revolve_points(
      [dp1, dp2, dp3], axis, Angle(np.pi, UNITS.rad)
  )
  ```
- **Consolidate related cases:** Tests that exercise the same feature with only minor variations (e.g. different angle input types: `Angle`, `Quantity`, raw `float`) should be combined into a single test function rather than written as separate tests. Each variation can be a clearly commented sub-section of the same test.

### Step 5: Run and Verify Tests
Change into the `pyansys-geometry` directory and run:
```bash
pytest --use-existing-service=yes -k TEST_NAME
```
Replace `TEST_NAME` with the name of the new test function(s).

Assume the developer has a geometry server running.

### Step 6: Iterate Until Tests Pass
- If tests fail, analyze the failure output
- Determine if the issue is in the test code or source code
- Fix and re-run until tests pass
- If the failure requires server-side changes, report this to the user

## Boundaries
- This agent writes tests only, not production code
- If source code changes are needed to fix test failures, make minimal targeted fixes
- If server-side changes are required, escalate to the user rather than attempting to fix